import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.config.features import FEATURE_COLUMNS, TARGET_COLUMN
from src.core.config import settings
from src.core.logger import get_logger
from src.core.prediction_data import (
    TARGET_DATE_COLUMN,
    fetch_prepared_prediction_frames,
)
from src.models.model_factory import ModelFactory
from src.verification.metrics import summarize_classification_results

logger = get_logger(__name__)


class SharedModelAdapter:
    """Train and score model types through a consistent preprocessing path."""

    def __init__(self, model_type: str):
        self.model_type = model_type.lower()
        model_wrapper = ModelFactory.create_model(self.model_type)
        self.model_name = model_wrapper.name
        self.model = model_wrapper.build_model()
        self.imputer = SimpleImputer(strategy="median")
        self.scaler = StandardScaler()

    def fit(self, df: pd.DataFrame) -> "SharedModelAdapter":
        X = df[FEATURE_COLUMNS]
        y = df[TARGET_COLUMN].astype(int)

        X_imputed = self.imputer.fit_transform(X)
        X_scaled = self.scaler.fit_transform(X_imputed)
        self.model.fit(X_scaled, y)
        return self

    def predict_probabilities(self, df: pd.DataFrame) -> np.ndarray:
        X = df[FEATURE_COLUMNS]
        X_imputed = self.imputer.transform(X)
        X_scaled = self.scaler.transform(X_imputed)

        if hasattr(self.model, "predict_proba"):
            return self.model.predict_proba(X_scaled)[:, 1]

        scores = self.model.decision_function(X_scaled)
        return 1.0 / (1.0 + np.exp(-scores))


class VerificationService:
    def __init__(self) -> None:
        self.output_dir = Path(settings.OUTPUT_DIR) / "verification"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.live_predictions_path = Path("data/verification/predictions.jsonl")
        self.live_predictions_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def normalize_model_type(model_type: str | None) -> str:
        normalized = (model_type or "logistic").strip().lower()
        ModelFactory.create_model(normalized)
        return normalized

    @staticmethod
    def _prediction_label(probability_up: float, threshold: float) -> int:
        return int(float(probability_up) >= float(threshold))

    @staticmethod
    def _confidence(probability_up: float) -> float:
        return round(abs(float(probability_up) - 0.5) * 2, 4)

    @staticmethod
    def _serialize_date(value: Any) -> str | None:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")
        return str(value)

    def _build_backtest_report_path(
        self,
        ticker: str,
        model_type: str,
        start_date: str | None,
        end_date: str | None,
    ) -> Path:
        if not start_date and not end_date:
            return self.output_dir / f"{ticker}_{model_type}.json"

        start_part = start_date or "default_start"
        end_part = end_date or "default_end"
        return self.output_dir / f"{ticker}_{model_type}_{start_part}_{end_part}.json"

    def _read_json_file(self, path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None

        with open(path, "r", encoding="utf-8") as file_obj:
            return json.load(file_obj)

    def get_cached_backtest_report(
        self,
        ticker: str,
        model_type: str = "logistic",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Any] | None:
        normalized_model_type = self.normalize_model_type(model_type)
        report_path = self._build_backtest_report_path(
            ticker=ticker,
            model_type=normalized_model_type,
            start_date=start_date,
            end_date=end_date,
        )
        return self._read_json_file(report_path)

    def _split_holdout_frames(self, training_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        if len(training_df) < 2:
            raise ValueError("Need at least two labeled rows for holdout evaluation")

        train_df, test_df = train_test_split(
            training_df,
            test_size=settings.TEST_SIZE,
            shuffle=False,
            random_state=settings.RANDOM_STATE,
        )

        if len(train_df) == 0 or len(test_df) == 0:
            train_df = training_df.iloc[:-1].copy()
            test_df = training_df.iloc[-1:].copy()

        return train_df, test_df

    def build_prediction_snapshot(
        self,
        ticker: str,
        model_type: str = "logistic",
        start_date: str | None = None,
        end_date: str | None = None,
        period: str | None = None,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        normalized_model_type = self.normalize_model_type(model_type)
        resolved_threshold = settings.MODEL_THRESHOLD if threshold is None else float(threshold)
        frames = fetch_prepared_prediction_frames(
            ticker=ticker,
            period=period,
            start=start_date,
            end=end_date,
        )

        if len(frames.training_df) < settings.MIN_TRAINING_SAMPLES:
            raise ValueError(
                f"Insufficient clean data after feature engineering: {len(frames.training_df)} rows"
            )

        holdout_train_df, holdout_test_df = self._split_holdout_frames(frames.training_df)
        holdout_adapter = SharedModelAdapter(normalized_model_type).fit(holdout_train_df)
        holdout_probabilities = holdout_adapter.predict_probabilities(holdout_test_df)
        holdout_results = pd.DataFrame(
            {
                "actual": holdout_test_df[TARGET_COLUMN].astype(int).values,
                "prediction": [
                    self._prediction_label(probability, resolved_threshold)
                    for probability in holdout_probabilities
                ],
                "probability_up": holdout_probabilities,
            }
        )
        holdout_metrics = summarize_classification_results(holdout_results)

        latest_adapter = SharedModelAdapter(normalized_model_type).fit(frames.training_df)
        latest_probability_up = float(latest_adapter.predict_probabilities(frames.latest_row)[0])

        historical_report = None
        if start_date or end_date or period in {None, settings.DEFAULT_PERIOD}:
            historical_report = self.get_cached_backtest_report(
                ticker=ticker,
                model_type=normalized_model_type,
                start_date=start_date,
                end_date=end_date,
            )
        historical_metrics = historical_report.get("metrics") if historical_report else holdout_metrics

        return {
            "ticker": ticker,
            "model_type": normalized_model_type,
            "model_name": latest_adapter.model_name,
            "latest_data_date": frames.latest_data_date,
            "latest_close": round(frames.latest_close, 2),
            "training_rows": int(len(frames.training_df)),
            "probability_up": round(latest_probability_up, 4),
            "prediction": "UP"
            if self._prediction_label(latest_probability_up, resolved_threshold) == 1
            else "DOWN",
            "confidence": self._confidence(latest_probability_up),
            "holdout_metrics": holdout_metrics,
            "historical_metrics": historical_metrics,
            "historical_report_available": historical_report is not None,
            "threshold": round(resolved_threshold, 4),
        }

    def _walk_forward_results(
        self,
        training_df: pd.DataFrame,
        model_type: str,
        threshold: float,
        min_train_size: int,
    ) -> pd.DataFrame:
        results: list[dict[str, Any]] = []

        for index in range(min_train_size, len(training_df)):
            train_df = training_df.iloc[:index].copy()
            test_row = training_df.iloc[index : index + 1].copy()
            adapter = SharedModelAdapter(model_type).fit(train_df)
            probability_up = float(adapter.predict_probabilities(test_row)[0])
            prediction = self._prediction_label(probability_up, threshold)
            actual = int(test_row[TARGET_COLUMN].iloc[0])

            results.append(
                {
                    "prediction_date": test_row.index[0].strftime("%Y-%m-%d"),
                    "target_date": self._serialize_date(test_row[TARGET_DATE_COLUMN].iloc[0]),
                    "probability_up": round(probability_up, 4),
                    "prediction": prediction,
                    "actual": actual,
                    "correct": int(prediction == actual),
                    "confidence": self._confidence(probability_up),
                }
            )

        return pd.DataFrame(results)

    def get_backtest_report(
        self,
        ticker: str,
        model_type: str = "logistic",
        start_date: str | None = None,
        end_date: str | None = None,
        refresh: bool = False,
        min_train_size: int = 200,
        threshold: float | None = None,
    ) -> dict[str, Any]:
        normalized_model_type = self.normalize_model_type(model_type)
        report_path = self._build_backtest_report_path(
            ticker=ticker,
            model_type=normalized_model_type,
            start_date=start_date,
            end_date=end_date,
        )

        if not refresh:
            cached_report = self._read_json_file(report_path)
            if cached_report is not None:
                return cached_report

        resolved_threshold = settings.MODEL_THRESHOLD if threshold is None else float(threshold)
        frames = fetch_prepared_prediction_frames(
            ticker=ticker,
            start=start_date,
            end=end_date,
        )

        if len(frames.training_df) <= min_train_size:
            raise ValueError(
                f"Not enough labeled rows for walk-forward validation: {len(frames.training_df)} available, {min_train_size + 1} required"
            )

        adapter = SharedModelAdapter(normalized_model_type)
        results_df = self._walk_forward_results(
            training_df=frames.training_df,
            model_type=normalized_model_type,
            threshold=resolved_threshold,
            min_train_size=min_train_size,
        )
        metrics = summarize_classification_results(results_df)

        report = {
            "ticker": ticker,
            "model_type": normalized_model_type,
            "model_name": adapter.model_name,
            "generated_at": datetime.now().isoformat(),
            "start_date": start_date,
            "end_date": end_date,
            "latest_data_date": frames.latest_data_date,
            "latest_close": round(frames.latest_close, 2),
            "threshold": round(resolved_threshold, 4),
            "min_train_size": int(min_train_size),
            "metrics": metrics,
            "results": results_df.to_dict("records"),
            "report_path": str(report_path),
        }

        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as file_obj:
            json.dump(report, file_obj, indent=2)

        return report

    def _load_live_predictions(self) -> list[dict[str, Any]]:
        if not self.live_predictions_path.exists():
            return []

        records: list[dict[str, Any]] = []
        with open(self.live_predictions_path, "r", encoding="utf-8") as file_obj:
            for line in file_obj:
                raw_line = line.strip()
                if not raw_line:
                    continue
                records.append(json.loads(raw_line))

        return records

    def _save_live_predictions(self, records: list[dict[str, Any]]) -> None:
        self.live_predictions_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.live_predictions_path, "w", encoding="utf-8") as file_obj:
            for record in records:
                file_obj.write(json.dumps(record))
                file_obj.write("\n")

    def upsert_live_prediction(
        self,
        prediction_payload: dict[str, Any],
    ) -> dict[str, Any]:
        records = self._load_live_predictions()
        ticker = str(prediction_payload["ticker"]).upper()
        model_type = str(prediction_payload["model_type"]).lower()
        latest_data_date = str(prediction_payload["latest_data_date"])

        existing_record: dict[str, Any] | None = None
        existing_index: int | None = None
        for index, record in enumerate(records):
            if (
                record.get("ticker") == ticker
                and record.get("model_type") == model_type
                and record.get("latest_data_date") == latest_data_date
            ):
                existing_record = record
                existing_index = index
                break

        record = dict(existing_record or {})
        record.update(
            {
                "prediction_id": record.get("prediction_id") or str(uuid.uuid4()),
                "ticker": ticker,
                "model_type": model_type,
                "prediction_date": prediction_payload["prediction_date"],
                "latest_data_date": latest_data_date,
                "target_date": record.get("target_date"),
                "threshold": float(prediction_payload["threshold"]),
                "probability_up": float(prediction_payload["probability_up"]),
                "prediction": prediction_payload["prediction"],
                "prediction_value": self._prediction_label(
                    float(prediction_payload["probability_up"]),
                    float(prediction_payload["threshold"]),
                ),
                "confidence": float(prediction_payload["confidence"]),
                "status": record.get("status", "pending"),
                "actual": record.get("actual"),
                "resolved_at": record.get("resolved_at"),
                "resolution_source": record.get("resolution_source"),
                "base_close": record.get("base_close", round(float(prediction_payload["latest_close"]), 2)),
                "actual_close": record.get("actual_close"),
            }
        )

        if existing_index is None:
            records.append(record)
        else:
            records[existing_index] = record

        self._save_live_predictions(records)
        return record

    def resolve_live_predictions(
        self,
        ticker: str,
        model_type: str | None = None,
        refresh: bool = False,
    ) -> list[dict[str, Any]]:
        normalized_ticker = ticker.upper()
        normalized_model_type = (
            self.normalize_model_type(model_type)
            if model_type is not None
            else None
        )
        records = self._load_live_predictions()
        scoped_records = [
            record
            for record in records
            if record.get("ticker") == normalized_ticker
            and (
                normalized_model_type is None
                or record.get("model_type") == normalized_model_type
            )
        ]

        pending_records = [record for record in scoped_records if record.get("status") != "resolved"]
        if not pending_records and not refresh:
            return records

        if not scoped_records:
            return records

        raw_df = fetch_prepared_prediction_frames(ticker=normalized_ticker).raw_df
        date_keys = [timestamp.strftime("%Y-%m-%d") for timestamp in raw_df.index]
        closes = raw_df["Close"].astype(float).tolist()
        index_by_date = {date_key: index for index, date_key in enumerate(date_keys)}

        updated = False
        for record in records:
            if record.get("ticker") != normalized_ticker:
                continue
            if normalized_model_type is not None and record.get("model_type") != normalized_model_type:
                continue
            if record.get("status") == "resolved":
                continue

            base_date = str(record.get("latest_data_date") or "")
            base_index = index_by_date.get(base_date)
            if base_index is None or base_index >= len(date_keys) - 1:
                continue

            next_index = base_index + 1
            base_close = closes[base_index]
            actual_close = closes[next_index]
            record["target_date"] = date_keys[next_index]
            record["actual"] = int(actual_close > base_close)
            record["status"] = "resolved"
            record["resolved_at"] = datetime.now().isoformat()
            record["resolution_source"] = "market_data"
            record["base_close"] = round(float(base_close), 2)
            record["actual_close"] = round(float(actual_close), 2)
            updated = True

        if updated:
            self._save_live_predictions(records)

        return records

    def get_live_verification_summary(
        self,
        ticker: str,
        model_type: str | None = None,
        refresh: bool = False,
    ) -> dict[str, Any]:
        normalized_ticker = ticker.upper()
        normalized_model_type = (
            self.normalize_model_type(model_type)
            if model_type is not None
            else None
        )
        records = self.resolve_live_predictions(
            ticker=normalized_ticker,
            model_type=normalized_model_type,
            refresh=refresh,
        )

        scoped_records = [
            record
            for record in records
            if record.get("ticker") == normalized_ticker
            and (
                normalized_model_type is None
                or record.get("model_type") == normalized_model_type
            )
        ]
        resolved_records = [record for record in scoped_records if record.get("status") == "resolved"]
        pending_records = [record for record in scoped_records if record.get("status") != "resolved"]

        resolved_df = pd.DataFrame(resolved_records)
        if not resolved_df.empty:
            resolved_df = resolved_df.copy()
            resolved_df["prediction_numeric"] = resolved_df["prediction_value"].astype(int)
            metrics = summarize_classification_results(
                resolved_df,
                prediction_col="prediction_numeric",
            )
        else:
            metrics = summarize_classification_results(pd.DataFrame())

        return {
            "ticker": normalized_ticker,
            "model_type": normalized_model_type or "all",
            "generated_at": datetime.now().isoformat(),
            "total_predictions": len(scoped_records),
            "resolved_predictions": len(resolved_records),
            "pending_predictions": len(pending_records),
            "metrics": metrics,
        }


verification_service = VerificationService()
