from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class StockInfo(BaseModel):
    """Stock information schema"""
    
    ticker: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None


class ModelInfo(BaseModel):
    """Model information schema"""
    
    ticker: str
    model_file: str
    has_scaler: bool
    created_at: str
    size_kb: float


class HealthResponse(BaseModel):
    """Health check response schema"""
    
    status: str
    timestamp: str
    version: str
    models_available: int
    uptime_seconds: Optional[float] = None


class ErrorResponse(BaseModel):
    """Error response schema"""
    
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: str = datetime.now().isoformat()