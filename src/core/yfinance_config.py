from pathlib import Path

import yfinance as yf

from src.core.config import settings
from src.core.logger import get_logger

logger = get_logger(__name__)

_configured = False


def configure_yfinance() -> None:
    global _configured

    if _configured:
        return

    cache_dir = Path(settings.YFINANCE_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    yf.set_tz_cache_location(str(cache_dir))

    logger.info(f"Configured yfinance cache directory: {cache_dir}")
    _configured = True
