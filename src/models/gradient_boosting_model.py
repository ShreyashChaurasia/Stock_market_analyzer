from sklearn.ensemble import GradientBoostingClassifier
from src.models.base_model import BaseMLModel


class GradientBoostingModel(BaseMLModel):
    """
    Gradient Boosting Classifier Model
    """
    
    def __init__(self):
        super().__init__(name="Gradient Boosting")
        
    def build_model(self, **kwargs):
        """Build Gradient Boosting model"""
        params = {
            'n_estimators': kwargs.get('n_estimators', 100),
            'max_depth': kwargs.get('max_depth', 5),
            'learning_rate': kwargs.get('learning_rate', 0.1),
            'subsample': kwargs.get('subsample', 0.8),
            'min_samples_split': kwargs.get('min_samples_split', 5),
            'min_samples_leaf': kwargs.get('min_samples_leaf', 2),
            'random_state': kwargs.get('random_state', 42)
        }
        
        return GradientBoostingClassifier(**params)