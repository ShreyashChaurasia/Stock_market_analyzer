import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def summarize_classification_results(
    results_df: pd.DataFrame,
    actual_col: str = "actual",
    prediction_col: str = "prediction",
    probability_col: str = "probability_up",
) -> dict[str, float | int]:
    total = len(results_df)
    if total == 0:
        return {
            "sample_count": 0,
            "balanced_accuracy": 0.0,
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "roc_auc": 0.0,
            "up_prediction_rate": 0.0,
            "true_positives": 0,
            "true_negatives": 0,
            "false_positives": 0,
            "false_negatives": 0,
        }

    y_true = results_df[actual_col].astype(int)
    y_pred = results_df[prediction_col].astype(int)
    y_proba = (
        results_df[probability_col].astype(float)
        if probability_col in results_df.columns
        else pd.Series(y_pred, index=results_df.index, dtype=float)
    )

    unique_classes = len(np.unique(y_true))
    balanced_accuracy = (
        balanced_accuracy_score(y_true, y_pred)
        if unique_classes > 1
        else accuracy_score(y_true, y_pred)
    )
    roc_auc = (
        roc_auc_score(y_true, y_proba)
        if unique_classes > 1
        else 0.5
    )

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    return {
        "sample_count": int(total),
        "balanced_accuracy": round(float(balanced_accuracy), 4),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc), 4),
        "up_prediction_rate": round(float(y_pred.mean()), 4),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
    }
