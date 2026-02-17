from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)

from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)


class BaseMLModel(ABC):
    """
    Abstract base class for all ML models
    """
    
    def __init__(self, name: str):
        self.name = name
        self.model = None
        self.scaler = None
        self.is_trained = False
        self.metrics = {}
        self.feature_importance = None
        
    @abstractmethod
    def build_model(self, **kwargs) -> Any:
        """
        Build and return the model instance
        Must be implemented by subclasses
        """
        pass
    
    def prepare_data(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        test_size: float = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare and split data for training
        
        Args:
            X: Feature dataframe
            y: Target series
            test_size: Test set size (default from settings)
            
        Returns:
            X_train, X_test, y_train, y_test
        """
        test_size = test_size or settings.TEST_SIZE
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=test_size,
            shuffle=False,
            random_state=settings.RANDOM_STATE
        )
        
        logger.info(f"Data split: Train={len(X_train)}, Test={len(X_test)}")
        
        return X_train, X_test, y_train, y_test
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """
        Train the model and evaluate
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info(f"Training {self.name} model")
        
        # Build model if not already built
        if self.model is None:
            self.model = self.build_model()
        
        # Train
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        self.metrics = self.evaluate(X_test, y_test)
        
        # Extract feature importance if available
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = self.model.feature_importances_
        elif hasattr(self.model, 'coef_'):
            self.feature_importance = np.abs(self.model.coef_[0])
        
        logger.info(f"{self.name} training complete. AUC: {self.metrics.get('auc', 0):.4f}")
        
        return self.metrics
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Make predictions
        
        Args:
            X: Features
            
        Returns:
            Predictions (0 or 1)
        """
        if not self.is_trained:
            raise ValueError(f"{self.name} model is not trained")
        
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict probabilities
        
        Args:
            X: Features
            
        Returns:
            Probability of class 1
        """
        if not self.is_trained:
            raise ValueError(f"{self.name} model is not trained")
        
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)[:, 1]
        else:
            return self.model.decision_function(X)
    
    def evaluate(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """
        Evaluate model performance
        
        Args:
            X: Test features
            y: Test labels
            
        Returns:
            Dictionary of metrics
        """
        y_pred = self.predict(X)
        y_proba = self.predict_proba(X)
        
        metrics = {
            'accuracy': accuracy_score(y, y_pred),
            'precision': precision_score(y, y_pred, zero_division=0),
            'recall': recall_score(y, y_pred, zero_division=0),
            'f1_score': f1_score(y, y_pred, zero_division=0),
            'auc': roc_auc_score(y, y_proba) if len(np.unique(y)) > 1 else 0.5
        }
        
        # Confusion matrix
        cm = confusion_matrix(y, y_pred)
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
            metrics['true_positives'] = int(tp)
            metrics['true_negatives'] = int(tn)
            metrics['false_positives'] = int(fp)
            metrics['false_negatives'] = int(fn)
        
        return metrics
    
    def get_params(self) -> Dict[str, Any]:
        """Get model parameters"""
        if self.model is None:
            return {}
        return self.model.get_params()
    
    def set_params(self, **params):
        """Set model parameters"""
        if self.model is not None:
            self.model.set_params(**params)
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', trained={self.is_trained})"