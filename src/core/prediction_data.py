from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.config.features import FEATURE_COLUMNS, TARGET_COLUMN
from src.core.config import settings
from src.core.data_fetcher import fetch_stock_data
from src.core.feature_engineering import add_ml_features
from src.core.indicators import add_indicators

TARGET_DATE_COLUMN = "TargetDate"


@dataclass
class PreparedPredictionFrames:
    raw_df: pd.DataFrame
    feature_df: pd.DataFrame
    prediction_df: pd.DataFrame
    training_df: pd.DataFrame
    latest_row: pd.DataFrame

    @property
    def latest_data_date(self) -> str:
        return self.latest_row.index[-1].strftime("%Y-%m-%d")

    @property
    def latest_close(self) -> float:
        return float(self.latest_row["Close"].iloc[-1])


def infer_currency_from_ticker(ticker: str) -> str:
    if ticker.endswith((".NS", ".BO")):
        return "INR"
    return "USD"


def prepare_prediction_frames(raw_df: pd.DataFrame) -> PreparedPredictionFrames:
    if raw_df.empty:
        raise ValueError("Cannot prepare prediction data from an empty dataframe")

    feature_df = add_indicators(raw_df.copy())
    feature_df = add_ml_features(feature_df)
    feature_df[TARGET_DATE_COLUMN] = feature_df.index.to_series().shift(-1)
    feature_df[TARGET_COLUMN] = (feature_df["Close"].shift(-1) > feature_df["Close"]).astype(float)

    # The latest row has no known next-day outcome yet, so it is prediction-only.
    feature_df.loc[feature_df.index[-1], TARGET_COLUMN] = np.nan

    prediction_df = feature_df.dropna(subset=FEATURE_COLUMNS).copy()
    if prediction_df.empty:
        raise ValueError("Insufficient clean rows after feature engineering")

    training_df = prediction_df[prediction_df[TARGET_COLUMN].notna()].copy()
    if training_df.empty:
        raise ValueError("Insufficient labeled rows after feature engineering")

    training_df[TARGET_COLUMN] = training_df[TARGET_COLUMN].astype(int)
    latest_row = prediction_df.tail(1).copy()

    return PreparedPredictionFrames(
        raw_df=raw_df,
        feature_df=feature_df,
        prediction_df=prediction_df,
        training_df=training_df,
        latest_row=latest_row,
    )


def fetch_prepared_prediction_frames(
    ticker: str,
    period: str | None = None,
    start: str | None = None,
    end: str | None = None,
) -> PreparedPredictionFrames:
    raw_df = fetch_stock_data(
        ticker=ticker,
        period=period or settings.DEFAULT_PERIOD,
        start=start,
        end=end,
    )
    return prepare_prediction_frames(raw_df)
