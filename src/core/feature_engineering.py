def add_ml_features(df):
    df = df.copy()

    # Returns
    df["Return_1d"] = df["Close"].pct_change()
    df["Return_5d"] = df["Close"].pct_change(5)

    # Volatility
    df["Volatility_20"] = df["Return_1d"].rolling(20).std()

    # === TREND FEATURES (CRITICAL) ===
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["SMA_50"] = df["Close"].rolling(50).mean()

    # Trend strength & direction
    df["Trend"] = df["SMA_20"] - df["SMA_50"]
    df["Trend_Slope"] = df["Trend"].diff()

    return df
