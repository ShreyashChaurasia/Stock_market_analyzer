def add_ml_features(df):
    df = df.copy()

    df["Return_1d"] = df["Close"].pct_change()
    df["Return_5d"] = df["Close"].pct_change(5)
    df["Volatility"] = df["Return_1d"].rolling(20).std()

    return df
