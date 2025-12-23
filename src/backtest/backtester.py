import pandas as pd

from src.core.indicators import add_indicators
from src.core.feature_engineering import add_ml_features
from src.core.probability_model import train_model_in_memory, predict_with_model
from sklearn.metrics import balanced_accuracy_score

def walk_forward_backtest(
    df: pd.DataFrame,
    ticker: str,
    min_train_size: int = 200,
    prob_threshold: float = 0.5
):
    results = []

    # ✅ Compute expensive features ONCE
    df_feat = add_indicators(df.copy())
    df_feat = add_ml_features(df_feat)

    for i in range(min_train_size, len(df_feat) - 1):
        hist = df_feat.iloc[: i + 2].copy()

        # Target created here (safe)
        hist["Target"] = (hist["Close"].shift(-1) > hist["Close"]).astype(int)

        train_df = hist.iloc[:-1].dropna()
        test_row = hist.iloc[-2]

        if len(train_df) < min_train_size:
            continue

        model, scaler = train_model_in_memory(train_df)

        full_df = pd.concat([train_df, test_row.to_frame().T])
        prob_up = predict_with_model(full_df, model, scaler)
        prob_up = 1 - prob_up  # inversion experiment

        prediction = int(prob_up >= prob_threshold)
        actual = int(test_row["Target"].item())

        results.append({
            "date": test_row.name,
            "probability_up": round(prob_up, 4),
            "prediction": prediction,
            "actual": actual,
            "correct": int(prediction == actual),
        })

    results_df = pd.DataFrame(results)

    print(results_df["prediction"].value_counts())
    print(results_df["actual"].value_counts())

    from sklearn.metrics import balanced_accuracy_score
    print(
        "Balanced accuracy:",
        balanced_accuracy_score(results_df["actual"], results_df["prediction"])
    )
    print("UP prediction rate:", round(results_df["prediction"].mean(), 3))

    return results_df

    return pd.DataFrame(results)
