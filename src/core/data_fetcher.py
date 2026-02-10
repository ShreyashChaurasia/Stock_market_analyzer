import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def fetch_stock_data(ticker, period="5y", interval="1d", start=None, end=None):
    """
    Fetch stock data from Yahoo Finance with improved error handling
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL', 'TSLA')
        period: Time period if start/end not specified (default: "5y")
        interval: Data interval - "1d", "1h", etc. (default: "1d")
        start: Start date (YYYY-MM-DD string or datetime object)
        end: End date (YYYY-MM-DD string or datetime object)
    
    Returns:
        pandas.DataFrame: Stock data with OHLCV columns
    """
    try:
        print(f"📊 Fetching data for {ticker}...")
        
        # Create ticker object
        stock = yf.Ticker(ticker)
        
        # Determine whether to use period or date range
        if start and end:
            df = stock.history(
                start=start,
                end=end,
                interval=interval,
                auto_adjust=False,
                actions=False
            )
        elif start and not end:
            # If only start is provided, fetch until today
            df = stock.history(
                start=start,
                end=datetime.now().strftime("%Y-%m-%d"),
                interval=interval,
                auto_adjust=False,
                actions=False
            )
        else:
            # Use period if no dates specified
            df = stock.history(
                period=period,
                interval=interval,
                auto_adjust=False,
                actions=False
            )

        if df.empty:
            raise ValueError(f"No data found for ticker: {ticker}")

        # CRITICAL FIX: Flatten MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Additional safety: squeeze any remaining multi-dimensional columns
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in df.columns:
                if hasattr(df[col], 'squeeze'):
                    df[col] = df[col].squeeze()

        # Validate data
        validate_data(df, ticker)

        # Save to CSV in data/raw/
        os.makedirs("data/raw", exist_ok=True)
        csv_path = f"data/raw/{ticker}.csv"
        df.to_csv(csv_path)

        print(f"✅ Successfully fetched {len(df)} rows for {ticker}")
        print(f"📁 Saved to: {csv_path}")
        print(f"📅 Date range: {df.index[0]} to {df.index[-1]}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error fetching data for {ticker}: {str(e)}")
        raise


def flatten_columns(df):
    """
    Flatten MultiIndex columns to single level
    
    Args:
        df: DataFrame with potentially multi-level columns
    
    Returns:
        DataFrame with flattened columns
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            col[0] if col[1] == "" else col[0]
            for col in df.columns
        ]
    return df


def validate_data(df, ticker):
    """
    Validate the fetched stock data
    
    Args:
        df: DataFrame to validate
        ticker: Stock ticker for error messages
    
    Raises:
        ValueError: If data validation fails
    """
    # Check for required columns
    required_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        raise ValueError(
            f"Missing required columns for {ticker}: {missing_cols}"
        )
    
    # Check for completely null columns
    null_cols = [col for col in required_cols if df[col].isnull().all()]
    if null_cols:
        raise ValueError(
            f"Columns contain only null values for {ticker}: {null_cols}"
        )
    
    # Check minimum data points
    if len(df) < 50:
        raise ValueError(
            f"Insufficient data for {ticker}: {len(df)} rows (minimum 50 required)"
        )
    
    return True


def load_stock_data(ticker):
    """
    Load previously saved stock data from CSV
    
    Args:
        ticker: Stock symbol
    
    Returns:
        DataFrame: Loaded stock data
    """
    csv_path = f"data/raw/{ticker}.csv"
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            f"No saved data found for {ticker}. Run fetch_stock_data() first."
        )
    
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    print(f"✅ Loaded {len(df)} rows for {ticker} from {csv_path}")
    
    return df