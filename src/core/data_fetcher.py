import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

from src.core.config import settings
from src.core.logger import get_logger
from src.core.exceptions import DataFetchError, InsufficientDataError

logger = get_logger(__name__)


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
        stock = yf.Ticker(ticker)
        
        if start and end:
            df = stock.history(
                start=start,
                end=end,
                interval=interval,
                auto_adjust=False,
                actions=False
            )
        elif start and not end:
            df = stock.history(
                start=start,
                end=datetime.now().strftime("%Y-%m-%d"),
                interval=interval,
                auto_adjust=False,
                actions=False
            )
        else:
            df = stock.history(
                period=period,
                interval=interval,
                auto_adjust=False,
                actions=False
            )

        if df.empty:
            raise DataFetchError(ticker, "No data returned from Yahoo Finance")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in df.columns:
                if hasattr(df[col], 'squeeze'):
                    df[col] = df[col].squeeze()

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