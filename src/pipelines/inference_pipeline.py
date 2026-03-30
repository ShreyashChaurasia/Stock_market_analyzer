from src.core.data_fetcher import fetch_stock_data
from src.core.indicators import add_indicators
from src.core.feature_engineering import add_ml_features
from src.core.probability_model import train_probability_model, predict_probability
import pandas as pd
import json
import os
from datetime import datetime

from src.core.config import settings


def infer_currency_from_ticker(ticker: str) -> str:
    if ticker.endswith((".NS", ".BO")):
        return "INR"
    return "USD"


def get_confidence_signal(confidence: float, model_auc: float) -> tuple[str, bool]:
    """Classify prediction confidence for dashboard filtering."""
    very_high = (
        confidence >= settings.HIGH_CONFIDENCE_THRESHOLD
        and model_auc >= settings.HIGH_CONFIDENCE_MIN_AUC
    )
    if very_high:
        return "very_high", True
    if confidence >= 0.25 and model_auc >= 0.52:
        return "high", False
    if confidence >= 0.15:
        return "medium", False
    return "low", False


def run_inference_pipeline(ticker: str, start=None, end=None):
    """
    Run complete inference pipeline for stock prediction
    
    This pipeline:
    1. Fetches stock data
    2. Adds technical indicators
    3. Engineers ML features
    4. Creates target variable
    5. Trains model
    6. Makes prediction
    7. Saves results
    
    Args:
        ticker (str): Stock symbol (e.g., 'AAPL', 'NVDA', 'TSLA')
        start (str, optional): Start date in 'YYYY-MM-DD' format
        end (str, optional): End date in 'YYYY-MM-DD' format
    
    Returns:
        dict: Prediction results including probability, direction, and confidence
    """
    print(f"\n{'='*60}")
    print(f"INFERENCE PIPELINE - {ticker}")
    print(f"{'='*60}\n")

    # Step 1: Fetch stock data
    print("Step 1/7: Fetching stock data...")
    df = fetch_stock_data(ticker, start=start, end=end)

    if df.empty or len(df) < 100:
        raise ValueError(
            f"Insufficient data for {ticker}: {len(df)} rows. Need at least 100 days."
        )
    
    print(f"   Data range: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"   Total rows: {len(df)}\n")

    # Step 2: Add technical indicators
    print("Step 2/7: Adding technical indicators...")
    df = add_indicators(df)
    print("   Added: SMA, EMA, RSI, MACD, Bollinger Bands\n")

    # Step 3: Add ML features
    print("Step 3/7: Engineering ML features...")
    df = add_ml_features(df)
    print("   Added: Returns, Volatility, Trend features\n")

    # Step 4: Create target variable (UP/DOWN next day)
    print("Step 4/7: Creating target variable...")
    df["Target"] = (df["Close"].shift(-1) > df["Close"]).astype(int)
    print("   Target: 1 = Price UP next day, 0 = Price DOWN next day\n")

    # Step 5: Clean data
    print("Step 5/7: Cleaning data...")
    rows_before = len(df)
    df = df.dropna()
    rows_after = len(df)
    print(f"   Removed {rows_before - rows_after} rows with NaN values")
    print(f"   Clean data: {rows_after} rows\n")

    if len(df) < 50:
        raise ValueError(
            f"Insufficient clean data after feature engineering: {len(df)} rows"
        )

    # Step 6: Train model
    print("Step 6/7: Training ML model...")
    auc = train_probability_model(df, ticker)
    print("   Model: Logistic Regression")
    print(f"   Test AUC Score: {auc:.4f}")
    print(f"   Model saved to: models/{ticker}_model.pkl\n")

    # Step 7: Get latest prediction
    print("Step 7/7: Making prediction...")
    probability_up = predict_probability(df, ticker)
    
    # Calculate prediction details
    prediction_direction = "UP" if probability_up > 0.5 else "DOWN"
    confidence = abs(probability_up - 0.5) * 2  # Scale to 0-1
    
    print(f"   Probability UP: {probability_up:.2%}")
    print(f"   Prediction: {prediction_direction}")
    print(f"   Confidence: {confidence:.2%}\n")

    confidence_tier, is_very_high_confidence = get_confidence_signal(confidence, auc)

    # Prepare output
    latest_date = df.index[-1].strftime("%Y-%m-%d")
    latest_close = float(df["Close"].iloc[-1])

    result = {
        "ticker": ticker,
        "prediction_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "latest_data_date": latest_date,
        "latest_close": round(latest_close, 2),
        "currency": infer_currency_from_ticker(ticker),
        "probability_up": round(probability_up, 4),
        "probability_down": round(1 - probability_up, 4),
        "prediction": "UP" if probability_up > 0.5 else "DOWN",
        "confidence": round(confidence, 4),
        "confidence_percent": f"{confidence * 100:.1f}%",
        "confidence_tier": confidence_tier,
        "is_very_high_confidence": is_very_high_confidence,
        "model_auc": round(auc, 4),
        "data_points_used": len(df),
        "interpretation": get_interpretation(probability_up, confidence)
    }

    # Save results
    os.makedirs("outputs", exist_ok=True)
    output_path = f"outputs/{ticker}.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=4)
    
    print(f"Saved results to: {output_path}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"PREDICTION COMPLETE")
    print(f"{'='*60}")
    print(f"Ticker: {ticker}")
    print(f"Latest Price: {infer_currency_from_ticker(ticker)} {latest_close:.2f}")
    print(f"Prediction: {result['prediction']} with {result['confidence_percent']} confidence")
    print(f"Interpretation: {result['interpretation']}")
    print(f"{'='*60}\n")

    return result


def get_interpretation(probability_up, confidence):
    """
    Get human-readable interpretation of the prediction
    
    Args:
        probability_up: Probability of price going up
        confidence: Confidence level (0-1)
    
    Returns:
        str: Interpretation message
    """
    direction = "increase" if probability_up > 0.5 else "decrease"
    
    if confidence > 0.7:
        strength = "Strong"
    elif confidence > 0.4:
        strength = "Moderate"
    else:
        strength = "Weak"
    
    return f"{strength} signal for price to {direction}"
