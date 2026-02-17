from xgboost import XGBClassifier
from src.models.base_model import BaseMLModel


class XGBoostModel(BaseMLModel):
    """
    XGBoost Classifier Model
    """
    
    def __init__(self):
        super().__init__(name="XGBoost")
        
    def build_model(self, **kwargs):
        """Build XGBoost model"""
        params = {
            'n_estimators': kwargs.get('n_estimators', 100),
            'max_depth': kwargs.get('max_depth', 6),
            'learning_rate': kwargs.get('learning_rate', 0.1),
            'subsample': kwargs.get('subsample', 0.8),
            'colsample_bytree': kwargs.get('colsample_bytree', 0.8),
            'random_state': kwargs.get('random_state', 42),
            'eval_metric': 'logloss',
            'use_label_encoder': False
        }
        
        return XGBClassifier(**params)