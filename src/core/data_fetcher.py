import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(ticker, period="5y", interval="1d"):
    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        raise ValueError("No data found")

    # CRITICAL FIX: flatten 2D OHLC columns
    for col in ["Open", "High", "Low", "Close", "Adj Close", "Volume"]:
        if col in df.columns:
            df[col] = df[col].squeeze()

    os.makedirs("data/raw", exist_ok=True)
    df.to_csv(f"data/raw/{ticker}.csv")

    return df

def flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            col[0] if col[1] == "" else col[0]
            for col in df.columns
        ]
    return df
