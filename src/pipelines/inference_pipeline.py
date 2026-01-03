from src.core.data_fetcher import fetch_stock_data
from src.core.indicators import add_indicators
from src.core.feature_engineering import add_ml_features
from src.core.probability_model import train_probability_model
from src.visualization.plots import plot_price_with_predictions


def run_inference_pipeline(ticker: str, start=None, end=None):
    print(f"[INFO] Running inference pipeline for {ticker}")

    df = fetch_stock_data(ticker, start=start, end=end)

    if df.empty or len(df) < 100:
        raise ValueError("Not enough data to run inference")

    df = add_indicators(df)
    X, y = add_ml_features(df)

    model, predictions = train_probability_model(X, y)

    df["signal_probability"] = predictions

    plot_price_with_predictions(df, ticker)

    print("[SUCCESS] Inference completed")
