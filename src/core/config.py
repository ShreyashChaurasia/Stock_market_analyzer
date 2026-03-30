import json
from pathlib import Path
from typing import Optional
from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # API Configuration
    API_TITLE: str = "Stock Market ML API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Machine Learning API for stock market predictions"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # Security Configuration (ADD THESE TWO LINES)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ENVIRONMENT: str = "development"
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_ORIGIN_REGEX: Optional[str] = None
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # ML Model Configuration
    MIN_TRAINING_SAMPLES: int = 100
    TEST_SIZE: float = 0.2
    RANDOM_STATE: int = 42
    MODEL_THRESHOLD: float = 0.5
    
    # Data Configuration
    MODEL_DIR: str = "models"
    DATA_DIR: str = "data/raw"
    OUTPUT_DIR: str = "outputs"
    LOG_DIR: str = "logs"
    YFINANCE_CACHE_DIR: str = "data/cache/yfinance"
    
    # Stock Data Configuration
    DEFAULT_PERIOD: str = "5y"
    DEFAULT_INTERVAL: str = "1d"
    MIN_DATA_POINTS: int = 50
    
    # Cache Configuration
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600

    # News Configuration
    NEWS_PROVIDER: str = "gnews"
    GNEWS_API_KEY: Optional[str] = None
    NEWSAPI_API_KEY: Optional[str] = None
    NEWS_CACHE_TTL: int = 900
    NEWS_DEFAULT_LIMIT: int = 10

    # Quant discovery dashboard configuration
    HIGH_CONFIDENCE_THRESHOLD: float = 0.30
    HIGH_CONFIDENCE_MIN_AUC: float = 0.50
    HIGH_CONFIDENCE_DEFAULT_LIMIT: int = 10
    HIGH_CONFIDENCE_MAX_RESULTS: int = 100
    HIGH_CONFIDENCE_CACHE_TTL: int = 1800
    HIGH_CONFIDENCE_OUTPUT_MAX_AGE_HOURS: int = 24
    HIGH_CONFIDENCE_SNAPSHOT_TTL: int = 300
    HIGH_CONFIDENCE_MAX_WORKERS: int = 4
    HIGH_CONFIDENCE_NEWS_MAX_WORKERS: int = 4
    HIGH_CONFIDENCE_LIVE_FALLBACK: bool = False
    HIGH_CONFIDENCE_DISCOVERY_TARGET: int = 600
    HIGH_CONFIDENCE_DISCOVERY_QUERY_LIMIT: int = 35
    HIGH_CONFIDENCE_DISCOVERY_CACHE_TTL: int = 21600
    HIGH_CONFIDENCE_UNIVERSE: list[str] = [
        "AAPL",
        "GOOGL",
        "MSFT",
        "NVDA",
        "TSLA",
        "RELIANCE.NS",
        "TCS.NS",
        "ICICIBANK.NS",
        "SBIN.NS",
        "TRENT.NS",
    ]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE_MAX_BYTES: int = 10485760
    LOG_FILE_BACKUP_COUNT: int = 5
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_CALLS: int = 100
    RATE_LIMIT_PERIOD: int = 3600
    
    # Database
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, bool):
            return value

        if value is None:
            return False

        normalized = str(value).strip().lower()
        if normalized in {"1", "true", "yes", "on", "debug", "development", "dev"}:
            return True
        if normalized in {"0", "false", "no", "off", "release", "production", "prod"}:
            return False

        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, list):
            normalized = [str(origin).strip().rstrip("/") for origin in value if str(origin).strip()]
            return normalized or ["*"]

        if value is None:
            return ["*"]

        raw = str(value).strip()
        if not raw:
            return ["*"]

        parsed_origins: list[str] = []
        if raw.startswith("["):
            try:
                decoded = json.loads(raw)
                if isinstance(decoded, list):
                    parsed_origins = [
                        str(origin).strip().rstrip("/")
                        for origin in decoded
                        if str(origin).strip()
                    ]
            except json.JSONDecodeError:
                parsed_origins = []

        if not parsed_origins:
            parsed_origins = [segment.strip().rstrip("/") for segment in raw.split(",") if segment.strip()]

        return parsed_origins or ["*"]

    @field_validator("CORS_ALLOW_ORIGIN_REGEX", mode="before")
    @classmethod
    def normalize_cors_origin_regex(cls, value):
        if value is None:
            return None

        normalized = str(value).strip()
        return normalized or None

    @field_validator("YFINANCE_CACHE_DIR", mode="after")
    @classmethod
    def normalize_cache_dir(cls, value: str) -> str:
        return str(Path(value))

    @field_validator("NEWS_PROVIDER", mode="before")
    @classmethod
    def normalize_news_provider(cls, value: str) -> str:
        return str(value or "gnews").strip().lower()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    Returns singleton settings object
    """
    return Settings()


settings = get_settings()
