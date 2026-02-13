from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

from src.core.validators import TickerValidator, DateValidator, PeriodValidator


class PredictionRequest(BaseModel):
    """Request schema for stock prediction"""
    
    ticker: str = Field(
        ...,
        description="Stock ticker symbol",
        example="AAPL",
        min_length=1,
        max_length=5
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
        description="Time period (used if start_date and end_date not provided)",
        example="1y"
    )
    
    @validator('ticker')
    def validate_ticker(cls, v):
        return TickerValidator.validate(v)
    
    @validator('start_date', 'end_date')
    def validate_dates(cls, v):
        if v:
            DateValidator.validate_date(v)
        return v
    
    @validator('period')
    def validate_period(cls, v):
        if v:
            return PeriodValidator.validate(v)
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "NVDA",
                "start_date": "2023-01-01",
                "end_date": "2024-12-31"
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for stock prediction"""
    
    ticker: str
    prediction_date: str
    latest_data_date: str
    latest_close: float
    probability_up: float
    probability_down: float
    prediction: str
    confidence: float
    confidence_percent: str
    model_auc: float
    data_points_used: int
    interpretation: str
    
    class Config:
        schema_extra = {
            "example": {
                "ticker": "AAPL",
                "prediction_date": "2024-02-10 12:00:00",
                "latest_data_date": "2024-02-10",
                "latest_close": 185.50,
                "probability_up": 0.6234,
                "probability_down": 0.3766,
                "prediction": "UP",
                "confidence": 0.2468,
                "confidence_percent": "24.7%",
                "model_auc": 0.5456,
                "data_points_used": 1256,
                "interpretation": "Moderate signal for price to increase"
            }
        }


class BacktestRequest(BaseModel):
    """Request schema for backtesting"""
    
    ticker: str = Field(..., description="Stock ticker symbol", example="TSLA")
    start_date: Optional[str] = Field(None, description="Start date", example="2022-01-01")
    end_date: Optional[str] = Field(None, description="End date", example="2024-12-31")
    
    @validator('ticker')
    def validate_ticker(cls, v):
        return TickerValidator.validate(v)


class BacktestResponse(BaseModel):
    """Response schema for backtest results"""
    
    ticker: str
    start_date: str
    end_date: str
    total_predictions: int
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    predictions_up: int
    predictions_down: int
    correct_predictions: int