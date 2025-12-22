def classification_metrics(results_df):
    total = len(results_df)
    correct = results_df["correct"].sum()

    up_preds = results_df[results_df["prediction"] == 1]
    up_correct = up_preds["correct"].sum() if not up_preds.empty else 0

    return {
        "total_predictions": total,
        "accuracy": round(correct / total, 4) if total else 0,
        "up_prediction_accuracy": round(
            up_correct / len(up_preds), 4
        ) if len(up_preds) else 0,
    }
