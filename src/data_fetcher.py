import yfinance as yf
import pandas as pd
import os

def fetch_stock_data(ticker, period="1y", interval="1d"):
    """
    Fetch historical stock data using yfinance.
    """
    data = yf.download(ticker, period=period, interval=interval)

    if data.empty:
        raise ValueError("No data found. Check ticker symbol.")

    # Save for reference
    os.makedirs("data", exist_ok=True)
    save_path = f"data/{ticker}.csv"
    data.to_csv(save_path)

    return data
