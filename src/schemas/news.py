from pydantic import BaseModel, Field


class NewsItem(BaseModel):
    """Normalized news article schema."""

    title: str
    description: str | None = None
    url: str
    source: str
    published_at: str
    image_url: str | None = None
    tickers: list[str] = Field(default_factory=list)
    market: str = "ALL"


class TrendingTicker(BaseModel):
    """Ticker mention count in a trending-news window."""

    ticker: str
    mentions: int
