import ta

def add_indicators(df):
    df = df.copy()

    close = df["Close"]
    close = close.squeeze()  # final safety guard

    df["SMA_20"] = close.rolling(20).mean()
    df["EMA_20"] = close.ewm(span=20).mean()
    df["RSI"] = ta.momentum.RSIIndicator(close).rsi()

    macd = ta.trend.MACD(close)
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()

    bb = ta.volatility.BollingerBands(close)
    df["BB_high"] = bb.bollinger_hband()
    df["BB_low"] = bb.bollinger_lband()

    return df
