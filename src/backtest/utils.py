import pandas as pd

def make_target(df: pd.DataFrame) -> pd.Series:
    """
    Binary classification target:
    1 → next day's close is higher
    0 → otherwise
    """
    return (df["Close"].shift(-1) > df["Close"]).astype(int)
