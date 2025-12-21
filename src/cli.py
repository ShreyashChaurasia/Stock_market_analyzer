import sys
from data_fetcher import fetch_stock_data
from indicators import add_indicators
from feature_engineering import add_ml_features
from probability_model import train_probability_model, predict_probability

def main():
    print("=== Stock Probability Predictor ===")
    
    ticker = input("Enter stock symbol (e.g., AAPL, TSLA, INFY): ").upper()
    
    print("\nFetching data...")
    df = fetch_stock_data(ticker)

    print("Adding indicators...")
    df = add_indicators(df)

    print("Generating ML features...")
    df = add_ml_features(df)

    print("Training model...")
    accuracy = train_probability_model(df, ticker)
    print(f"Model accuracy: {accuracy:.2f}")

    print("Predicting probability...")
    prob = predict_probability(df, ticker)

    print(f"\nProbability {ticker} will go UP tomorrow: {prob*100:.2f}%\n")

if __name__ == "__main__":
    main()
