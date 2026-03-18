import yfinance as yf
import pandas as pd
import os
from datetime import datetime

from src.core.config import settings
from src.core.logger import get_logger
from src.core.exceptions import DataFetchError, InsufficientDataError
from src.core.yfinance_config import configure_yfinance

logger = get_logger(__name__)

configure_yfinance()


def _normalize_ohlcv_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns and hasattr(df[col], "squeeze"):
            df[col] = df[col].squeeze()

    return df


def _fetch_history_with_fallback(
    ticker: str,
    period: str = "5y",
    interval: str = "1d",
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    history_kwargs = {
        "interval": interval,
        "auto_adjust": False,
        "actions": False,
    }

    if start:
        history_kwargs["start"] = start
        history_kwargs["end"] = end or datetime.now().strftime("%Y-%m-%d")
    else:
        history_kwargs["period"] = period

    try:
        df = stock.history(**history_kwargs)
        df = _normalize_ohlcv_columns(df)
        if not df.empty:
            return df
        logger.warning(f"Ticker.history returned empty data for {ticker}: {history_kwargs}")
    except Exception as exc:
        logger.warning(
            f"Ticker.history failed for {ticker}. kwargs={history_kwargs}, error={exc}"
        )

    download_kwargs = {
        "tickers": ticker,
        "interval": interval,
        "auto_adjust": False,
        "actions": False,
        "progress": False,
        "threads": False,
    }
    if start:
        download_kwargs["start"] = history_kwargs["start"]
        download_kwargs["end"] = history_kwargs["end"]
    else:
        download_kwargs["period"] = period

    try:
        df = yf.download(**download_kwargs)
        df = _normalize_ohlcv_columns(df)
        if not df.empty:
            logger.info(f"Fetched data for {ticker} using yf.download fallback")
            return df
        logger.warning(f"yf.download returned empty data for {ticker}: {download_kwargs}")
    except Exception as exc:
        logger.error(
            f"yf.download failed for {ticker}. kwargs={download_kwargs}, error={exc}",
            exc_info=True,
        )

    return pd.DataFrame()


def fetch_stock_data(ticker, period="5y", interval="1d", start=None, end=None):
    """
    Fetch stock data from Yahoo Finance with improved error handling
    
    Args:
        ticker: Stock symbol
        period: Time period if start/end not specified
        interval: Data interval
        start: Start date
        end: End date
    
    Returns:
        pandas.DataFrame: Stock data with OHLCV columns
        
    Raises:
        DataFetchError: If data cannot be fetched
        InsufficientDataError: If insufficient data points
    """
    logger.info(f"Fetching data for {ticker} (period={period}, start={start}, end={end})")
    
    try:
        df = _fetch_history_with_fallback(
            ticker=ticker,
            period=period,
            interval=interval,
            start=start,
            end=end,
        )

        if df.empty:
            raise DataFetchError(
                ticker,
                f"No data returned from Yahoo Finance (period={period}, start={start}, end={end}, interval={interval})",
            )

        validate_data(df, ticker)

        os.makedirs(settings.DATA_DIR, exist_ok=True)
        csv_path = os.path.join(settings.DATA_DIR, f"{ticker}.csv")
        df.to_csv(csv_path)

        logger.info(f"Successfully fetched {len(df)} rows for {ticker}")
        
        return df
        
    except DataFetchError:
        raise
    except InsufficientDataError:
        raise
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}", exc_info=True)
        raise DataFetchError(ticker, str(e))


def validate_data(df, ticker):
    """Validate the fetched stock data"""
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise DataFetchError(ticker, f"Missing columns: {missing_cols}")
    
    null_cols = [col for col in required_cols if df[col].isnull().all()]
    if null_cols:
        raise DataFetchError(ticker, f"Null columns: {null_cols}")
    
    if len(df) < settings.MIN_DATA_POINTS:
        raise InsufficientDataError(ticker, len(df), settings.MIN_DATA_POINTS)
    
    return True


def load_stock_data(ticker):
    """Load previously saved stock data from CSV"""
    csv_path = os.path.join(settings.DATA_DIR, f"{ticker}.csv")
    
    if not os.path.exists(csv_path):
        logger.warning(f"No saved data found for {ticker}")
        raise DataFetchError(ticker, "No saved data available")
    
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    logger.info(f"Loaded {len(df)} rows for {ticker} from cache")
    
    return df
