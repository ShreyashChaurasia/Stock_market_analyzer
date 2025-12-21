from src.core.data_fetcher import fetch_stock_data
from src.core.indicators import add_indicators
from src.core.feature_engineering import add_ml_features
from src.core.probability_model import train_probability_model, predict_probability
from src.core.prediction_payload import save_prediction_payload

def main():
    ticker = input("Enter stock symbol: ").upper()

    df = fetch_stock_data(ticker)
    df = add_indicators(df)
    df = add_ml_features(df)

    auc = train_probability_model(df, ticker)
    prob = predict_probability(df, ticker)

    save_prediction_payload(df, ticker, prob)

    print(f"AUC Score: {auc:.3f}")
    print(f"Probability UP tomorrow: {prob*100:.2f}%")

if __name__ == "__main__":
    main()
