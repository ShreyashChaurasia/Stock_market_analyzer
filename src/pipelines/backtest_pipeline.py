from src.core.data_fetcher import fetch_stock_data
from src.core.indicators import add_indicators
from src.core.feature_engineering import add_ml_features
from src.core.probability_model import train_probability_model
from src.backtest.backtester import walk_forward_backtest
from src.backtest.metrics import classification_metrics


def run_backtest_pipeline(ticker: str, start=None, end=None):
    print(f"[INFO] Running backtest pipeline for {ticker}")

    df = fetch_stock_data(ticker, start=start, end=end)

    if df.empty or len(df) < 200:
        raise ValueError("Not enough data for backtesting")

    df = add_indicators(df)
    X, y = add_ml_features(df)

    model, predictions = train_probability_model(X, y)
    df["signal_probability"] = predictions

    results = walk_forward_backtest(df)
    metrics = classification_metrics(results)

    print("[BACKTEST RESULTS]")
    for k, v in metrics.items():
        print(f"{k}: {v}")

    print("[SUCCESS] Backtest completed")
