from sklearn.ensemble import RandomForestClassifier
from src.models.base_model import BaseMLModel


class RandomForestModel(BaseMLModel):
    """
    Random Forest Classifier Model
    """
    
    def __init__(self):
        super().__init__(name="Random Forest")
        
    def build_model(self, **kwargs):
        """Build Random Forest model"""
        params = {
            'n_estimators': kwargs.get('n_estimators', 100),
            'max_depth': kwargs.get('max_depth', 10),
            'min_samples_split': kwargs.get('min_samples_split', 5),
            'min_samples_leaf': kwargs.get('min_samples_leaf', 2),
            'max_features': kwargs.get('max_features', 'sqrt'),
            'random_state': kwargs.get('random_state', 42),
            'class_weight': kwargs.get('class_weight', 'balanced'),
            'n_jobs': kwargs.get('n_jobs', -1)
        }
        
        return RandomForestClassifier(**params)