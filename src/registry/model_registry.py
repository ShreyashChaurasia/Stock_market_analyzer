import os
import json
import pickle
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from src.core.config import settings
from src.core.logger import get_logger
from src.models.base_model import BaseMLModel

logger = get_logger(__name__)


class ModelRegistry:
    """
    Registry for managing trained models and their metadata
    """
    
    def __init__(self, base_dir: str = "model_artifacts"):
        self.base_dir = Path(base_dir)
        self.metadata_dir = self.base_dir / "metadata"
        self.versions_dir = self.base_dir / "versions"
        
        # Create directories
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
    
    def save_model(
        self,
        model: BaseMLModel,
        ticker: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save model and metadata
        
        Args:
            model: Trained model instance
            ticker: Stock ticker
            metadata: Additional metadata
            
        Returns:
            Version ID
        """
        version_id = self._generate_version_id(ticker, model.name)
        
        # Save model file
        model_path = self.versions_dir / f"{version_id}.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        # Save metadata
        meta = {
            'version_id': version_id,
            'ticker': ticker,
            'model_name': model.name,
            'model_type': model.__class__.__name__,
            'timestamp': datetime.now().isoformat(),
            'metrics': model.metrics,
            'is_trained': model.is_trained,
            'params': model.get_params(),
            'file_path': str(model_path),
            'file_size_kb': model_path.stat().st_size / 1024
        }
        
        if metadata:
            meta.update(metadata)
        
        metadata_path = self.metadata_dir / f"{version_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(meta, f, indent=2)
        
        logger.info(f"Saved model: {version_id}")
        
        return version_id
    
    def load_model(self, version_id: str) -> BaseMLModel:
        """
        Load model by version ID
        
        Args:
            version_id: Version identifier
            
        Returns:
            Loaded model instance
        """
        model_path = self.versions_dir / f"{version_id}.pkl"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {version_id}")
        
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        logger.info(f"Loaded model: {version_id}")
        
        return model
    
    def get_metadata(self, version_id: str) -> Dict[str, Any]:
        """Get model metadata"""
        metadata_path = self.metadata_dir / f"{version_id}.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {version_id}")
        
        with open(metadata_path, 'r') as f:
            return json.load(f)
    
    def list_models(
        self,
        ticker: Optional[str] = None,
        model_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all registered models
        
        Args:
            ticker: Filter by ticker
            model_type: Filter by model type
            
        Returns:
            List of model metadata
        """
        models = []
        
        for metadata_file in self.metadata_dir.glob("*.json"):
            with open(metadata_file, 'r') as f:
                meta = json.load(f)
            
            # Apply filters
            if ticker and meta.get('ticker') != ticker:
                continue
            if model_type and meta.get('model_type') != model_type:
                continue
            
            models.append(meta)
        
        # Sort by timestamp (newest first)
        models.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return models
    
    def get_best_model(
        self,
        ticker: str,
        metric: str = 'auc'
    ) -> Optional[Dict[str, Any]]:
        """
        Get best performing model for a ticker
        
        Args:
            ticker: Stock ticker
            metric: Metric to optimize
            
        Returns:
            Best model metadata
        """
        models = self.list_models(ticker=ticker)
        
        if not models:
            return None
        
        # Sort by metric
        models.sort(
            key=lambda x: x.get('metrics', {}).get(metric, 0),
            reverse=True
        )
        
        return models[0]
    
    def delete_model(self, version_id: str) -> None:
        """Delete model and metadata"""
        model_path = self.versions_dir / f"{version_id}.pkl"
        metadata_path = self.metadata_dir / f"{version_id}.json"
        
        if model_path.exists():
            model_path.unlink()
        if metadata_path.exists():
            metadata_path.unlink()
        
        logger.info(f"Deleted model: {version_id}")
    
    def _generate_version_id(self, ticker: str, model_name: str) -> str:
        """Generate unique version ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_slug = model_name.lower().replace(' ', '_')
        return f"{ticker}_{model_slug}_{timestamp}"


# Global registry instance
registry = ModelRegistry()