from pydantic import BaseModel, Field

from src.schemas.news import NewsItem


class HighConfidenceStock(BaseModel):
    """Stock prediction payload for the Quant Discovery dashboard."""

    ticker: str
    prediction: str
    confidence: float
    confidence_percent: str
    confidence_tier: str
    is_very_high_confidence: bool
    model_auc: float
    probability_up: float
    probability_down: float
    latest_close: float
    currency: str
    prediction_date: str
    latest_data_date: str
    interpretation: str
    source: str
    news: list[NewsItem] = Field(default_factory=list)
