from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from src.models.model_factory import ModelFactory
from src.models.base_model import BaseMLModel
from src.registry.model_registry import registry
from src.services.comparison_service import ModelComparisonService
from src.services.tuning_service import TuningService
from src.core.logger import get_logger
from src.config.features import FEATURE_COLUMNS

logger = get_logger(__name__)


class ModelService:
    """
    High-level service for model operations
    """
    
    def __init__(self):
        self.factory = ModelFactory()
        self.comparison_service = ModelComparisonService()
        self.tuning_service = TuningService()
        self.registry = registry
    
    def train_single_model(
        self,
        df: pd.DataFrame,
        ticker: str,
        model_type: str = 'logistic',
        tune: bool = False
    ) -> Dict[str, Any]:
        """
        Train a single model
        
        Args:
            df: DataFrame with features and target
            ticker: Stock ticker
            model_type: Type of model to train
            tune: Whether to tune hyperparameters
            
        Returns:
            Training results
        """
        logger.info(f"Training {model_type} for {ticker}")
        
        # Get available features from dataframe
        available_features = [col for col in FEATURE_COLUMNS if col in df.columns]
        
        if len(available_features) == 0:
            raise ValueError(f"No features found in dataframe. Available columns: {df.columns.tolist()}")
        
        logger.info(f"Using {len(available_features)} features: {available_features}")
        
        # Prepare data
        X = df[available_features]
        y = df['Target']
        
        # Handle missing values
        X = X.fillna(X.median())
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Create model
        model = self.factory.create_model(model_type)
        
        # Split data
        X_train, X_test, y_train, y_test = model.prepare_data(X_scaled, y)
        
        # Tune if requested
        tuning_results = None
        if tune:
            tuning_results = self.tuning_service.tune_model(
                model, X_train, y_train
            )
        
        # Train
        metrics = model.train(X_train, y_train, X_test, y_test)
        
        # Save to registry
        version_id = self.registry.save_model(
            model, ticker,
            metadata={
                'scaler': scaler,
                'tuning_results': tuning_results,
                'feature_columns': available_features
            }
        )
        
        return {
            'version_id': version_id,
            'model_type': model_type,
            'metrics': metrics,
            'tuning_results': tuning_results
        }
    
    def train_all_models(
        self,
        df: pd.DataFrame,
        ticker: str,
        tune: bool = False
    ) -> Dict[str, Any]:
        """
        Train all available models and compare
        
        Args:
            df: DataFrame with features and target
            ticker: Stock ticker
            tune: Whether to tune hyperparameters
            
        Returns:
            Comparison results
        """
        logger.info(f"Training all models for {ticker}")
        
        # Get available features
        available_features = [col for col in FEATURE_COLUMNS if col in df.columns]
        
        if len(available_features) == 0:
            raise ValueError(f"No features found in dataframe. Available columns: {df.columns.tolist()}")
        
        logger.info(f"Using {len(available_features)} features")
        
        # Prepare data
        X = df[available_features]
        y = df['Target']
        
        X = X.fillna(X.median())
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Use first model to split data
        temp_model = self.factory.create_model('logistic')
        X_train, X_test, y_train, y_test = temp_model.prepare_data(X_scaled, y)
        
        # Compare all models
        comparison_results = self.comparison_service.compare_models(
            X_train, y_train, X_test, y_test
        )
        
        # Save all models to registry
        saved_versions = []
        for model_type, result in comparison_results['models'].items():
            if 'model' in result:
                version_id = self.registry.save_model(
                    result['model'], ticker,
                    metadata={
                        'scaler': scaler,
                        'feature_columns': available_features
                    }
                )
                saved_versions.append({
                    'model_type': model_type,
                    'version_id': version_id,
                    'metrics': result['metrics']
                })
        
        return {
            'ticker': ticker,
            'models_trained': len(saved_versions),
            'saved_versions': saved_versions,
            'comparison': comparison_results['comparison'].to_dict('records') if not comparison_results['comparison'].empty else [],
            'best_model': comparison_results['best_model']
        }
    
    def predict_with_model(
        self,
        version_id: str,
        df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Make prediction using a specific model version
        
        Args:
            version_id: Model version ID
            df: DataFrame with features
            
        Returns:
            Prediction results
        """
        # Load model and metadata
        model = self.registry.load_model(version_id)
        metadata = self.registry.get_metadata(version_id)
        
        # Get scaler and features
        scaler = metadata.get('scaler')
        feature_columns = metadata.get('feature_columns', FEATURE_COLUMNS)
        
        # Prepare features
        available_features = [col for col in feature_columns if col in df.columns]
        X = df[available_features].fillna(df[available_features].median())
        
        if scaler:
            X = scaler.transform(X)
        
        # Predict
        probability = model.predict_proba(X[-1:])
        prediction = model.predict(X[-1:])
        
        return {
            'version_id': version_id,
            'model_type': metadata['model_type'],
            'probability_up': float(probability[0]),
            'prediction': int(prediction[0]),
            'model_metrics': metadata.get('metrics', {})
        }