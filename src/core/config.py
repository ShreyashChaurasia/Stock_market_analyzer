from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


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
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
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
    
    # Stock Data Configuration
    DEFAULT_PERIOD: str = "5y"
    DEFAULT_INTERVAL: str = "1d"
    MIN_DATA_POINTS: int = 50
    
    # Cache Configuration
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600
    
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