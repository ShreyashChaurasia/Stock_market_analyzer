import pandas as pd
import ta

def add_indicators(df):
    """
    Adds RSI, MACD, EMA, SMA, Bollinger Bands.
    """
    df = df.copy()

    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["EMA_20"] = df["Close"].ewm(span=20).mean()

    df["RSI"] = ta.momentum.RSIIndicator(df["Close"]).rsi()
    
    macd = ta.trend.MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    
    bb = ta.volatility.BollingerBands(df["Close"])
    df["BB_high"] = bb.bollinger_hband()
    df["BB_low"] = bb.bollinger_lband()

    df.dropna(inplace=True)
    return df
