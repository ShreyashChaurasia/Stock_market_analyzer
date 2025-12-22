import pandas as pd

from src.core.indicators import add_indicators
from src.core.feature_engineering import add_ml_features
from src.core.probability_model import train_model_in_memory, predict_with_model


def walk_forward_backtest(
    df: pd.DataFrame,
    ticker: str,
    min_train_size: int = 200,
    prob_threshold: float = 0.65
):
    results = []

    for i in range(min_train_size, len(df) - 1):
        hist = df.iloc[: i + 1].copy()

        # feature engineering grows over time
        hist = add_indicators(hist)
        hist = add_ml_features(hist)

        # target ONLY here
        hist["Target"] = (hist["Close"].shift(-1) > hist["Close"]).astype(int)
        hist = hist.dropna()

        if len(hist) < min_train_size:
            continue

        train_df = hist.iloc[:-1]

        model, scaler = train_model_in_memory(train_df)
        prob_up = predict_with_model(hist, model, scaler)

        prediction = int(prob_up >= prob_threshold)
        actual = int(hist["Target"].iloc[-1])

        results.append({
            "date": hist.index[-1],
            "probability_up": round(prob_up, 4),
            "prediction": prediction,
            "actual": actual,
            "correct": int(prediction == actual),
        })

    return pd.DataFrame(results)
