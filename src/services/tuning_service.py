from typing import Dict, Any
import numpy as np
from sklearn.model_selection import GridSearchCV

from src.models.base_model import BaseMLModel
from src.core.logger import get_logger
from src.core.config import settings

logger = get_logger(__name__)


class TuningService:
    """
    Service for hyperparameter tuning
    """
    
    PARAM_GRIDS = {
        'random_forest': {
            'n_estimators': [50, 100, 200],
            'max_depth': [5, 10, 15],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        },
        'xgboost': {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 6, 9],
            'learning_rate': [0.01, 0.1, 0.3],
            'subsample': [0.6, 0.8, 1.0]
        },
        'gradient_boosting': {
            'n_estimators': [50, 100, 200],
            'max_depth': [3, 5, 7],
            'learning_rate': [0.01, 0.1, 0.2],
            'subsample': [0.6, 0.8, 1.0]
        },
        'logistic': {
            'C': [0.1, 1.0, 10.0],
            'solver': ['lbfgs', 'liblinear'],
            'max_iter': [1000, 2000]
        }
    }
    
    def tune_model(
        self,
        model: BaseMLModel,
        X_train: np.ndarray,
        y_train: np.ndarray,
        param_grid: Dict[str, list] = None,
        cv: int = 3,
        scoring: str = 'roc_auc'
    ) -> Dict[str, Any]:
        """
        Tune model hyperparameters using GridSearchCV
        
        Args:
            model: Model instance to tune
            X_train: Training features
            y_train: Training labels
            param_grid: Parameter grid (uses default if None)
            cv: Number of cross-validation folds
            scoring: Scoring metric
            
        Returns:
            Tuning results
        """
        logger.info(f"Tuning {model.name}")
        
        # Get default param grid if not provided
        if param_grid is None:
            model_type = model.name.lower().replace(' ', '_')
            param_grid = self.PARAM_GRIDS.get(model_type, {})
        
        if not param_grid:
            logger.warning(f"No param grid for {model.name}")
            return {
                'status': 'skipped',
                'reason': 'No parameter grid available'
            }
        
        # Build model for tuning
        base_model = model.build_model()
        
        # Grid search
        grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=param_grid,
            cv=cv,
            scoring=scoring,
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        logger.info(f"Best params: {grid_search.best_params_}")
        logger.info(f"Best score: {grid_search.best_score_:.4f}")
        
        # Update model with best parameters
        model.set_params(**grid_search.best_params_)
        
        return {
            'status': 'success',
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': {
                'mean_test_score': grid_search.cv_results_['mean_test_score'].tolist(),
                'std_test_score': grid_search.cv_results_['std_test_score'].tolist(),
                'params': grid_search.cv_results_['params']
            }
        }