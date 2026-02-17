from sklearn.linear_model import LogisticRegression
from src.models.base_model import BaseMLModel


class LogisticModel(BaseMLModel):
    """
    Logistic Regression Model
    """
    
    def __init__(self):
        super().__init__(name="Logistic Regression")
        
    def build_model(self, **kwargs):
        """Build Logistic Regression model"""
        params = {
            'max_iter': kwargs.get('max_iter', 1000),
            'random_state': kwargs.get('random_state', 42),
            'solver': kwargs.get('solver', 'lbfgs'),
            'class_weight': kwargs.get('class_weight', 'balanced')
        }
        
        return LogisticRegression(**params)