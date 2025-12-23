from src.core.data_fetcher import fetch_stock_data
from src.core.indicators import add_indicators
from src.core.feature_engineering import add_ml_features
from src.core.probability_model import train_probability_model, predict_probability
from src.core.prediction_payload import save_prediction_payload
from src.visualization.plots import (
plot_price_with_predictions,
    plot_probability_over_time,
)

def main():
    ticker = input("Enter stock symbol: ").upper()

    df = fetch_stock_data(ticker)
    df = add_indicators(df)
    df = add_ml_features(df)

    # Create target ONLY for training / evaluation
    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
    df = df.dropna()

    auc = train_probability_model(df, ticker)
    prob = predict_probability(df, ticker)

    save_prediction_payload(df, ticker, prob)

    print(f"AUC Score: {auc:.3f}")
    print(f"Probability UP tomorrow: {prob*100:.2f}%")

if __name__ == "__main__":
    main()


from src.backtest.backtester import walk_forward_backtest
from src.backtest.metrics import classification_metrics
from src.core.data_fetcher import fetch_stock_data

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

run_backtest()
