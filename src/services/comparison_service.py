from typing import Dict, List, Any
import pandas as pd
import numpy as np

from src.models.model_factory import ModelFactory
from src.models.base_model import BaseMLModel
from src.core.logger import get_logger

logger = get_logger(__name__)


class ModelComparisonService:
    """
    Service for comparing multiple models
    """
    
    def __init__(self):
        self.factory = ModelFactory()
    
    def compare_models(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray,
        model_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Train and compare multiple models
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            model_types: List of model types to compare (None for all)
            
        Returns:
            Comparison results
        """
        logger.info("Starting model comparison")
        
        if model_types is None:
            model_types = self.factory.get_available_models()
        
        results = {}
        
        for model_type in model_types:
            logger.info(f"Training {model_type}")
            
            try:
                model = self.factory.create_model(model_type)
                metrics = model.train(X_train, y_train, X_test, y_test)
                
                results[model_type] = {
                    'model': model,
                    'metrics': metrics,
                    'feature_importance': model.feature_importance.tolist() if model.feature_importance is not None else None
                }
                
            except Exception as e:
                logger.error(f"Error training {model_type}: {str(e)}")
                results[model_type] = {
                    'error': str(e)
                }
        
        # Create comparison summary
        comparison = self._create_comparison_summary(results)
        
        logger.info("Model comparison complete")
        
        return {
            'models': results,
            'comparison': comparison,
            'best_model': self._get_best_model(results)
        }
    
    def _create_comparison_summary(
        self,
        results: Dict[str, Any]
    ) -> pd.DataFrame:
        """Create comparison summary DataFrame"""
        rows = []
        
        for model_type, result in results.items():
            if 'metrics' in result:
                row = {'model': model_type}
                row.update(result['metrics'])
                rows.append(row)
        
        if not rows:
            return pd.DataFrame()
        
        df = pd.DataFrame(rows)
        df = df.round(4)
        
        return df
    
    def _get_best_model(
        self,
        results: Dict[str, Any],
        metric: str = 'auc'
    ) -> Dict[str, Any]:
        """Determine best model by metric"""
        best_model = None
        best_score = -1
        
        for model_type, result in results.items():
            if 'metrics' in result:
                score = result['metrics'].get(metric, 0)
                if score > best_score:
                    best_score = score
                    best_model = {
                        'model_type': model_type,
                        'metric': metric,
                        'score': best_score
                    }
        
        return best_model