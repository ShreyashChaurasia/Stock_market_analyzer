import json
import os
from datetime import datetime

from src.core.config import settings
from src.core.prediction_data import infer_currency_from_ticker
from src.verification.service import verification_service


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


def run_inference_pipeline(
    ticker: str,
    start: str | None = None,
    end: str | None = None,
    period: str | None = None,
    model_type: str = "logistic",
):
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

    print("Step 1/4: Preparing prediction dataset...")
    prediction_snapshot = verification_service.build_prediction_snapshot(
        ticker=ticker,
        model_type=model_type,
        start_date=start,
        end_date=end,
        period=period,
    )
    print(f"   Model: {prediction_snapshot['model_name']}")
    print(f"   Latest data date: {prediction_snapshot['latest_data_date']}")
    print("   Shared feature engineering and verification path loaded\n")

    print("Step 2/4: Resolving any pending live verification records...")
    verification_service.resolve_live_predictions(ticker=ticker, model_type=model_type)
    print("   Live verification ledger refreshed\n")

    print("Step 3/4: Recording prediction for future live verification...")
    prediction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    live_record = verification_service.upsert_live_prediction(
        {
            "ticker": ticker,
            "model_type": prediction_snapshot["model_type"],
            "prediction_date": prediction_date,
            "latest_data_date": prediction_snapshot["latest_data_date"],
            "threshold": prediction_snapshot["threshold"],
            "probability_up": prediction_snapshot["probability_up"],
            "prediction": prediction_snapshot["prediction"],
            "confidence": prediction_snapshot["confidence"],
            "latest_close": prediction_snapshot["latest_close"],
        }
    )
    print(f"   Prediction ID: {live_record['prediction_id']}")
    print(f"   Verification status: {live_record['status']}\n")

    print("Step 4/4: Building response payload...")
    probability_up = prediction_snapshot["probability_up"]
    confidence = prediction_snapshot["confidence"]
    model_metrics = prediction_snapshot["historical_metrics"]
    model_auc = float(model_metrics.get("roc_auc", prediction_snapshot["holdout_metrics"]["roc_auc"]))
    confidence_tier, is_very_high_confidence = get_confidence_signal(confidence, model_auc)

    result = {
        "ticker": ticker,
        "prediction_date": prediction_date,
        "latest_data_date": prediction_snapshot["latest_data_date"],
        "latest_close": prediction_snapshot["latest_close"],
        "currency": infer_currency_from_ticker(ticker),
        "probability_up": round(probability_up, 4),
        "probability_down": round(1 - probability_up, 4),
        "prediction": prediction_snapshot["prediction"],
        "confidence": round(confidence, 4),
        "confidence_percent": f"{confidence * 100:.1f}%",
        "confidence_tier": confidence_tier,
        "is_very_high_confidence": is_very_high_confidence,
        "model_auc": round(model_auc, 4),
        "data_points_used": int(prediction_snapshot["training_rows"]),
        "interpretation": get_interpretation(probability_up, confidence),
        "model_type": prediction_snapshot["model_type"],
        "prediction_id": live_record["prediction_id"],
        "verification_status": live_record["status"],
        "verification_balanced_accuracy": round(
            float(model_metrics.get("balanced_accuracy", prediction_snapshot["holdout_metrics"]["balanced_accuracy"])),
            4,
        ),
        "verification_sample_count": int(
            model_metrics.get("sample_count", prediction_snapshot["holdout_metrics"]["sample_count"])
        ),
    }

    # Save results
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(settings.OUTPUT_DIR, f"{ticker}.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
    
    print(f"Saved results to: {output_path}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"PREDICTION COMPLETE")
    print(f"{'='*60}")
    print(f"Ticker: {ticker}")
    print(f"Latest Price: {infer_currency_from_ticker(ticker)} {prediction_snapshot['latest_close']:.2f}")
    print(f"Prediction: {result['prediction']} with {result['confidence_percent']} confidence")
    print(f"Interpretation: {result['interpretation']}")
    print(f"Verification BA: {result['verification_balanced_accuracy']:.4f}")
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
