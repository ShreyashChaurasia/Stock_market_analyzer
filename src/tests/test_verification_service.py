import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from src.core.prediction_data import prepare_prediction_frames
from src.verification.metrics import summarize_classification_results
from src.verification.service import VerificationService


@pytest.fixture
def verification_tmp_path() -> Path:
    base_dir = Path("outputs") / "test_artifacts" / "verification" / "service"
    base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="run-", dir=str(base_dir))).resolve()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def _build_sample_ohlcv(periods: int = 260) -> pd.DataFrame:
    dates = pd.bdate_range("2024-01-02", periods=periods)
    wave = np.sin(np.arange(periods) / 4.0) * 3.0
    trend = np.linspace(0, 18, periods)
    close = 100 + trend + wave

    return pd.DataFrame(
        {
            "Open": close - 0.4,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": 1_000_000 + (np.arange(periods) % 7) * 5_000,
        },
        index=dates,
    )


def _build_service(tmp_path: Path) -> VerificationService:
    service = VerificationService()
    service.output_dir = tmp_path / "outputs" / "verification"
    service.output_dir.mkdir(parents=True, exist_ok=True)
    service.live_predictions_path = tmp_path / "data" / "verification" / "predictions.jsonl"
    service.live_predictions_path.parent.mkdir(parents=True, exist_ok=True)
    return service


def test_prepare_prediction_frames_excludes_latest_unlabeled_row():
    frames = prepare_prediction_frames(_build_sample_ohlcv())

    assert len(frames.prediction_df) == len(frames.training_df) + 1
    assert frames.latest_row.index[-1] == frames.prediction_df.index[-1]
    assert frames.latest_row.index[-1] not in frames.training_df.index
    assert frames.latest_data_date == frames.prediction_df.index[-1].strftime("%Y-%m-%d")


def test_summarize_classification_results_handles_class_imbalance():
    results_df = pd.DataFrame(
        {
            "actual": [1, 1, 1, 0],
            "prediction": [1, 0, 1, 0],
            "probability_up": [0.92, 0.45, 0.77, 0.18],
        }
    )

    metrics = summarize_classification_results(results_df)

    assert metrics["sample_count"] == 4
    assert metrics["accuracy"] == 0.75
    assert metrics["balanced_accuracy"] == 0.8333
    assert metrics["true_positives"] == 2
    assert metrics["true_negatives"] == 1


def test_live_prediction_upsert_and_resolve_next_trading_day(monkeypatch, verification_tmp_path: Path):
    service = _build_service(verification_tmp_path)
    raw_df = pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0],
            "High": [101.0, 102.0, 103.0],
            "Low": [99.0, 100.5, 101.5],
            "Close": [100.0, 102.0, 101.0],
            "Volume": [1_000_000, 1_100_000, 1_050_000],
        },
        index=pd.to_datetime(["2026-03-27", "2026-03-30", "2026-03-31"]),
    )

    monkeypatch.setattr(
        "src.verification.service.fetch_prepared_prediction_frames",
        lambda **_: SimpleNamespace(raw_df=raw_df),
    )

    record = service.upsert_live_prediction(
        {
            "ticker": "AAPL",
            "model_type": "logistic",
            "prediction_date": "2026-03-27 16:00:00",
            "latest_data_date": "2026-03-27",
            "threshold": 0.5,
            "probability_up": 0.68,
            "prediction": "UP",
            "confidence": 0.36,
            "latest_close": 100.0,
        }
    )

    service.resolve_live_predictions("AAPL", model_type="logistic")
    summary = service.get_live_verification_summary("AAPL", model_type="logistic")
    stored_records = service._load_live_predictions()

    assert record["prediction_id"] == stored_records[0]["prediction_id"]
    assert stored_records[0]["status"] == "resolved"
    assert stored_records[0]["target_date"] == "2026-03-30"
    assert stored_records[0]["actual"] == 1
    assert summary["resolved_predictions"] == 1
    assert summary["pending_predictions"] == 0
    assert summary["metrics"]["sample_count"] == 1


def test_backtest_report_writes_expected_shape(monkeypatch, verification_tmp_path: Path):
    service = _build_service(verification_tmp_path)
    frames = prepare_prediction_frames(_build_sample_ohlcv(280))

    monkeypatch.setattr(
        "src.verification.service.fetch_prepared_prediction_frames",
        lambda **_: frames,
    )

    report = service.get_backtest_report(
        ticker="AAPL",
        model_type="logistic",
        refresh=True,
        min_train_size=60,
    )

    assert report["ticker"] == "AAPL"
    assert report["model_type"] == "logistic"
    assert report["metrics"]["sample_count"] == len(report["results"])
    assert report["metrics"]["sample_count"] > 0
    assert Path(report["report_path"]).exists()
