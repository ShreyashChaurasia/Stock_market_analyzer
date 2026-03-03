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
        self.scalers_dir = self.base_dir / "scalers"  # NEW: separate directory for scalers
        
        # Create directories
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.scalers_dir.mkdir(parents=True, exist_ok=True)  # NEW
    
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
        
        # Separate scaler from metadata if present
        scaler = None
        if metadata and 'scaler' in metadata:
            scaler = metadata.pop('scaler')  # Remove from metadata
            # Save scaler separately
            scaler_path = self.scalers_dir / f"{version_id}_scaler.pkl"
            with open(scaler_path, 'wb') as f:
                pickle.dump(scaler, f)
        
        # Create JSON-serializable metadata
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
            'file_size_kb': model_path.stat().st_size / 1024,
            'has_scaler': scaler is not None,  # Flag to indicate scaler exists
        }
        
        # Add remaining metadata (excluding non-serializable objects)
        if metadata:
            # Filter out any remaining non-serializable objects
            for key, value in metadata.items():
                try:
                    json.dumps(value)  # Test if serializable
                    meta[key] = value
                except (TypeError, ValueError):
                    logger.warning(f"Skipping non-serializable metadata field: {key}")
        
        # Save metadata as JSON
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
    
    def load_scaler(self, version_id: str):
        """
        Load scaler for a model version
        
        Args:
            version_id: Version identifier
            
        Returns:
            Loaded scaler or None if not found
        """
        scaler_path = self.scalers_dir / f"{version_id}_scaler.pkl"
        
        if not scaler_path.exists():
            return None
        
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        
        logger.info(f"Loaded scaler: {version_id}")
        
        return scaler
    
    def get_metadata(self, version_id: str) -> Dict[str, Any]:
        """
        Get model metadata
        
        Args:
            version_id: Version identifier
            
        Returns:
            Metadata dictionary with scaler loaded if available
        """
        metadata_path = self.metadata_dir / f"{version_id}.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata not found: {version_id}")
        
        with open(metadata_path, 'r') as f:
            meta = json.load(f)
        
        # Load scaler if it exists
        if meta.get('has_scaler'):
            meta['scaler'] = self.load_scaler(version_id)
        
        return meta
    
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
            try:
                with open(metadata_file, 'r') as f:
                    meta = json.load(f)
                
                # Apply filters
                if ticker and meta.get('ticker') != ticker:
                    continue
                if model_type and meta.get('model_type') != model_type:
                    continue
                
                models.append(meta)
            except Exception as e:
                logger.error(f"Error reading metadata file {metadata_file}: {str(e)}")
                continue
        
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
        """Delete model, scaler, and metadata"""
        model_path = self.versions_dir / f"{version_id}.pkl"
        metadata_path = self.metadata_dir / f"{version_id}.json"
        scaler_path = self.scalers_dir / f"{version_id}_scaler.pkl"
        
        if model_path.exists():
            model_path.unlink()
        if metadata_path.exists():
            metadata_path.unlink()
        if scaler_path.exists():
            scaler_path.unlink()
        
        logger.info(f"Deleted model: {version_id}")
    
    def _generate_version_id(self, ticker: str, model_name: str) -> str:
        """Generate unique version ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_slug = model_name.lower().replace(' ', '_')
        return f"{ticker}_{model_slug}_{timestamp}"


# Global registry instance
registry = ModelRegistry()