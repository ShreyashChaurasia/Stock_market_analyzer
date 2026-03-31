from typing import Optional

from pydantic import BaseModel, Field


class VerificationMetricSummary(BaseModel):
    sample_count: int
    balanced_accuracy: float
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    up_prediction_rate: float
    true_positives: int
    true_negatives: int
    false_positives: int
    false_negatives: int


class BacktestResultRecord(BaseModel):
    prediction_date: str
    target_date: Optional[str] = None
    probability_up: float
    prediction: int
    actual: int
    correct: int
    confidence: float


class BacktestVerificationResponse(BaseModel):
    ticker: str
    model_type: str
    model_name: str
    generated_at: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    latest_data_date: str
    latest_close: float
    threshold: float
    min_train_size: int
    metrics: VerificationMetricSummary
    results: list[BacktestResultRecord] = Field(default_factory=list)
    report_path: str

    class Config:
        protected_namespaces = ()


class LiveVerificationSummaryResponse(BaseModel):
    ticker: str
    model_type: str
    generated_at: str
    total_predictions: int
    resolved_predictions: int
    pending_predictions: int
    metrics: VerificationMetricSummary

    class Config:
        protected_namespaces = ()
