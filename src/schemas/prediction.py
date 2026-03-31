from typing import Optional

from pydantic import BaseModel, Field, field_validator

class PredictionRequest(BaseModel):
    """Request schema for stock prediction"""
    
    ticker: str = Field(
        ...,
        description="Stock ticker symbol (supports .NS/.BO suffix for Indian stocks)",
        example="AAPL",
        min_length=1,
        max_length=20  # Increased from 5 to support Indian stocks
    )
    start_date: Optional[str] = Field(
        None,
        description="Start date in YYYY-MM-DD format",
        example="2023-01-01"
    )
    end_date: Optional[str] = Field(
        None,
        description="End date in YYYY-MM-DD format",
        example="2024-12-31"
    )
    period: Optional[str] = Field(
        "5y",
        description="Time period",
        example="1y"
    )
    
    @field_validator('ticker')
    def validate_ticker(cls, v):
        return v.strip().upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "NVDA",
                "period": "1y"
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for stock prediction"""
    
    ticker: str
    prediction_date: str
    latest_data_date: str
    latest_close: float
    currency: str
    probability_up: float
    probability_down: float
    prediction: str
    confidence: float
    confidence_percent: str
    confidence_tier: str
    is_very_high_confidence: bool
    model_auc: float
    data_points_used: int
    interpretation: str
    model_type: Optional[str] = None
    prediction_id: Optional[str] = None
    verification_status: Optional[str] = None
    verification_balanced_accuracy: Optional[float] = None
    verification_sample_count: Optional[int] = None
    
    class Config:
        protected_namespaces = ()  # Allow model_ prefix
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "currency": "USD",
                "prediction": "UP",
                "probability_up": 0.65,
                "confidence_percent": "30%",
                "model_type": "logistic",
                "verification_balanced_accuracy": 0.56,
            }
        }
