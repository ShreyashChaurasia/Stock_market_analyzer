import pandas as pd
from src.core.data_fetcher import fetch_stock_data
from src.core.indicators import add_indicators
from src.core.feature_engineering import add_ml_features
from src.core.probability_model import train_probability_model, predict_probability
from src.core.prediction_payload import save_prediction_payload
from src.config.features import FEATURE_COLUMNS
from src.visualization.plots import (
    plot_price_with_predictions,
    plot_probability_over_time,
)
from src.backtest.backtester import walk_forward_backtest
from src.backtest.metrics import classification_metrics
from src.core.data_fetcher import flatten_columns


def main():
    ticker = input("Enter stock symbol: ").upper()

    df = fetch_stock_data(ticker)

    df = add_indicators(df)
    df = add_ml_features(df)

    # FIX: flatten MultiIndex columns
    df = flatten_columns(df)

    # Create target
    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)

    # Determine usable features dynamically
    usable_features = get_usable_features(df, FEATURE_COLUMNS)

    print("Usable features:", usable_features)

    if len(usable_features) < 5:
        raise ValueError(
            f"Too few usable features for training: {usable_features}"
        )

    # Drop rows where THESE features are missing
    feature_df = df.dropna(subset=usable_features).copy()

    # Remove last row (future target unknown)
    feature_df = feature_df.iloc[:-1]

    if len(feature_df) < 200:
        raise ValueError(
            f"Not enough usable rows after feature engineering: {len(feature_df)}"
        )

    train_df = feature_df
    latest_df = df.dropna(subset=usable_features).tail(1)

    auc = train_probability_model(train_df, ticker)
    prob = predict_probability(latest_df, ticker)

    save_prediction_payload(latest_df, ticker, prob)

    print(f"AUC Score: {auc:.3f}")
    print(f"Probability UP tomorrow: {prob*100:.2f}%")

def get_usable_features(df, feature_cols):
    """
    Keep only feature columns that are not entirely NaN.
    """
    usable = []
    for col in feature_cols:
        if col in df.columns and not df[col].isna().all():
            usable.append(col)
    return usable

def run_backtest():
    ticker = input("Enter stock symbol for backtest: ").upper()
    df = fetch_stock_data(ticker)

    print("Fetched rows:", len(df))
    print("Date range:", df.index.min(), "→", df.index.max())

    results = walk_forward_backtest(df, ticker)
    metrics = classification_metrics(results)

    plot_price_with_predictions(df, results, ticker)
    plot_probability_over_time(results, ticker)

    print("\nBacktest Results")
    print("----------------")
    for k, v in metrics.items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
    run_backtest()
