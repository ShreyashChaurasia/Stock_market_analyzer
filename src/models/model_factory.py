from typing import Dict, List
from src.models.base_model import BaseMLModel
from src.models.logistic_model import LogisticModel
from src.models.random_forest_model import RandomForestModel
from src.models.xgboost_model import XGBoostModel
from src.models.gradient_boosting_model import GradientBoostingModel


class ModelFactory:
    """
    Factory for creating ML models
    """
    
    _models = {
        'logistic': LogisticModel,
        'random_forest': RandomForestModel,
        'xgboost': XGBoostModel,
        'gradient_boosting': GradientBoostingModel
    }
    
    @classmethod
    def create_model(cls, model_type: str) -> BaseMLModel:
        """
        Create a model instance
        
        Args:
            model_type: Type of model to create
            
        Returns:
            Model instance
            
        Raises:
            ValueError: If model_type is invalid
        """
        model_type = model_type.lower()
        
        if model_type not in cls._models:
            raise ValueError(
                f"Invalid model type: {model_type}. "
                f"Available: {list(cls._models.keys())}"
            )
        
        return cls._models[model_type]()
    
    @classmethod
    def create_all_models(cls) -> Dict[str, BaseMLModel]:
        """
        Create instances of all available models
        
        Returns:
            Dictionary mapping model type to model instance
        """
        return {
            model_type: model_class()
            for model_type, model_class in cls._models.items()
        }
    
    @classmethod
    def get_available_models(cls) -> List[str]:
        """Get list of available model types"""
        return list(cls._models.keys())