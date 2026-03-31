import json
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import app
from src.core.config import settings
from src.core.prediction_data import prepare_prediction_frames

client = TestClient(app)


@pytest.fixture
def verification_tmp_path() -> Path:
    base_dir = Path("outputs") / "test_artifacts" / "verification" / "api"
    base_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="run-", dir=str(base_dir))).resolve()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


def _build_sample_ohlcv(periods: int = 280) -> pd.DataFrame:
    dates = pd.bdate_range("2024-01-02", periods=periods)
    wave = np.sin(np.arange(periods) / 5.0) * 2.5
    trend = np.linspace(0, 20, periods)
    close = 120 + trend + wave

    return pd.DataFrame(
        {
            "Open": close - 0.35,
            "High": close + 0.95,
            "Low": close - 1.05,
            "Close": close,
            "Volume": 1_200_000 + (np.arange(periods) % 11) * 3_000,
        },
        index=dates,
    )


def _configure_verification_paths(monkeypatch, tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    verification_dir = output_dir / "verification"
    ledger_path = tmp_path / "data" / "verification" / "predictions.jsonl"

    output_dir.mkdir(parents=True, exist_ok=True)
    verification_dir.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(settings, "OUTPUT_DIR", str(output_dir), raising=False)
    monkeypatch.setattr(app_module.verification_service, "output_dir", verification_dir)
    monkeypatch.setattr(app_module.verification_service, "live_predictions_path", ledger_path)


def test_backtest_verification_endpoint_success(monkeypatch, verification_tmp_path: Path):
    _configure_verification_paths(monkeypatch, verification_tmp_path)
    frames = prepare_prediction_frames(_build_sample_ohlcv())

    monkeypatch.setattr(
        "src.verification.service.fetch_prepared_prediction_frames",
        lambda **_: frames,
    )

    response = client.get("/api/verification/backtest/AAPL?model_type=logistic&refresh=true")

    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["model_type"] == "logistic"
    assert data["metrics"]["sample_count"] > 0


def test_live_verification_endpoint_resolves_pending_record(monkeypatch, verification_tmp_path: Path):
    _configure_verification_paths(monkeypatch, verification_tmp_path)
    raw_df = pd.DataFrame(
        {
            "Open": [100.0, 101.0, 102.0],
            "High": [101.0, 102.0, 103.0],
            "Low": [99.0, 100.0, 101.0],
            "Close": [100.0, 102.0, 101.0],
            "Volume": [1_000_000, 1_010_000, 1_020_000],
        },
        index=pd.to_datetime(["2026-03-27", "2026-03-30", "2026-03-31"]),
    )

    app_module.verification_service.upsert_live_prediction(
        {
            "ticker": "AAPL",
            "model_type": "logistic",
            "prediction_date": "2026-03-27 16:00:00",
            "latest_data_date": "2026-03-27",
            "threshold": 0.5,
            "probability_up": 0.72,
            "prediction": "UP",
            "confidence": 0.44,
            "latest_close": 100.0,
        }
    )

    monkeypatch.setattr(
        "src.verification.service.fetch_prepared_prediction_frames",
        lambda **_: SimpleNamespace(raw_df=raw_df),
    )

    response = client.get("/api/verification/live/AAPL?model_type=logistic")

    assert response.status_code == 200
    data = response.json()
    assert data["resolved_predictions"] == 1
    assert data["pending_predictions"] == 0
    assert data["metrics"]["sample_count"] == 1


def test_predict_route_records_live_prediction(monkeypatch, verification_tmp_path: Path):
    _configure_verification_paths(monkeypatch, verification_tmp_path)
    frames = prepare_prediction_frames(_build_sample_ohlcv())

    monkeypatch.setattr(
        "src.verification.service.fetch_prepared_prediction_frames",
        lambda **_: frames,
    )

    response = client.post(
        "/api/predict",
        json={"ticker": "AAPL", "period": "1y"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["prediction_id"]
    assert data["verification_status"] == "pending"

    ledger_path = app_module.verification_service.live_predictions_path
    stored_records = [json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines() if line]

    assert len(stored_records) == 1
    assert stored_records[0]["ticker"] == "AAPL"
    assert stored_records[0]["latest_data_date"] == data["latest_data_date"]
