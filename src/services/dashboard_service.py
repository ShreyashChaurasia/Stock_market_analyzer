import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import Any

from src.core.config import settings
from src.core.logger import get_logger
from src.pipelines.inference_pipeline import (
    get_confidence_signal,
    infer_currency_from_ticker,
    run_inference_pipeline,
)
from src.services.market_data_service import market_service
from src.services.news_service import news_service
from src.utils.cache import cache

logger = get_logger(__name__)


class DashboardService:
    """Build data for dashboard views that aggregate multiple tickers."""

    @staticmethod
    def _normalize_ticker(ticker: str) -> str:
        return (ticker or "").strip().upper()

    @staticmethod
    def _normalize_market(market: str | None) -> str:
        normalized = (market or "ALL").strip().upper()
        if normalized not in {"ALL", "US", "INDIA"}:
            raise ValueError("market must be one of: ALL, US, INDIA")
        return normalized

    @staticmethod
    def _market_matches_ticker(ticker: str, market: str) -> bool:
        if market == "ALL":
            return True
        is_indian = ticker.endswith((".NS", ".BO"))
        if market == "INDIA":
            return is_indian
        return not is_indian

    @staticmethod
    def _parse_watchlist(watchlist: str | None) -> list[str]:
        if not watchlist:
            return []
        parsed = []
        for raw in watchlist.split(","):
            cleaned = raw.strip().upper()
            if cleaned:
                parsed.append(cleaned)
        return parsed

    @staticmethod
    def _snapshot_cache_key(
        market: str,
        limit: int,
        watchlist: str | None,
        include_news: bool,
        confidence_threshold: float,
        min_auc: float,
    ) -> str:
        watchlist_key = (watchlist or "").replace(" ", "")
        return (
            "dashboard:snapshot:"
            f"{market}:{limit}:{int(include_news)}:{confidence_threshold:.4f}:{min_auc:.4f}:{watchlist_key}"
        )

    @staticmethod
    def _parse_prediction_timestamp(value: str) -> datetime | None:
        raw = (value or "").strip()
        if not raw:
            return None

        for parser in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(raw[:19], parser)
            except ValueError:
                continue

        try:
            return datetime.fromisoformat(raw)
        except ValueError:
            return None

    def _resolve_thresholds(
        self,
        confidence_threshold: float | None,
        min_auc: float | None,
    ) -> tuple[float, float]:
        resolved_confidence = (
            settings.HIGH_CONFIDENCE_THRESHOLD
            if confidence_threshold is None
            else float(confidence_threshold)
        )
        resolved_min_auc = (
            settings.HIGH_CONFIDENCE_MIN_AUC if min_auc is None else float(min_auc)
        )

        if not 0.0 <= resolved_confidence <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1")
        if not 0.0 <= resolved_min_auc <= 1.0:
            raise ValueError("min_auc must be between 0 and 1")

        return round(resolved_confidence, 4), round(resolved_min_auc, 4)

    def _read_output_file(self, ticker: str) -> dict[str, Any] | None:
        output_path = os.path.join(settings.OUTPUT_DIR, f"{ticker}.json")
        if not os.path.exists(output_path):
            return None

        try:
            with open(output_path, "r", encoding="utf-8") as file_obj:
                payload = json.load(file_obj)
        except Exception as exc:
            logger.warning(f"Could not read output file for {ticker}: {exc}")
            return None

        prediction_date = payload.get("prediction_date")
        if not prediction_date:
            return None

        parsed_date = self._parse_prediction_timestamp(str(prediction_date))
        if not parsed_date:
            return None

        max_age = timedelta(hours=settings.HIGH_CONFIDENCE_OUTPUT_MAX_AGE_HOURS)
        if datetime.now() - parsed_date > max_age:
            return None

        payload["source"] = "output_file"
        return self._normalize_prediction_payload(payload, ticker)

    def _normalize_prediction_payload(self, payload: dict[str, Any], ticker: str) -> dict[str, Any]:
        normalized = dict(payload)
        normalized["ticker"] = self._normalize_ticker(normalized.get("ticker") or ticker)

        confidence = float(normalized.get("confidence") or 0.0)
        model_auc = float(normalized.get("model_auc") or 0.0)
        confidence_tier, is_very_high_confidence = get_confidence_signal(confidence, model_auc)

        normalized.setdefault("prediction", "UP")
        normalized.setdefault("confidence_percent", f"{confidence * 100:.1f}%")
        normalized.setdefault("probability_up", 0.5)
        normalized.setdefault("probability_down", round(1 - float(normalized["probability_up"]), 4))
        normalized.setdefault("latest_close", 0.0)
        normalized.setdefault("prediction_date", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        normalized.setdefault("latest_data_date", datetime.now().strftime("%Y-%m-%d"))
        normalized.setdefault("interpretation", "Prediction generated")
        normalized.setdefault("currency", infer_currency_from_ticker(normalized["ticker"]))
        normalized["confidence"] = round(confidence, 4)
        normalized["model_auc"] = round(model_auc, 4)
        normalized["confidence_tier"] = confidence_tier
        normalized["is_very_high_confidence"] = is_very_high_confidence
        normalized.setdefault("source", "pipeline")

        return normalized

    def _run_live_prediction(self, ticker: str) -> dict[str, Any] | None:
        try:
            pipeline_result = run_inference_pipeline(ticker)
            normalized = self._normalize_prediction_payload(pipeline_result, ticker)
            normalized["source"] = "pipeline"
            cache.set(
                f"dashboard:prediction:{ticker}",
                normalized,
                ttl=settings.HIGH_CONFIDENCE_CACHE_TTL,
            )
            return normalized
        except Exception as exc:
            logger.warning(f"Failed to generate prediction for {ticker}: {exc}")
            return None

    def _predict_ticker(self, ticker: str, refresh: bool) -> dict[str, Any] | None:
        cache_key = f"dashboard:prediction:{ticker}"
        if not refresh:
            cache_hit = cache.get(cache_key)
            if cache_hit is not None:
                return cache_hit

        output_result = self._read_output_file(ticker)
        if output_result is not None:
            cache.set(cache_key, output_result, ttl=settings.HIGH_CONFIDENCE_CACHE_TTL)
            if not refresh:
                return output_result
            if not settings.HIGH_CONFIDENCE_LIVE_FALLBACK:
                return output_result

        if not settings.HIGH_CONFIDENCE_LIVE_FALLBACK:
            return None

        return self._run_live_prediction(ticker)

    def _build_universe(self, market: str, watchlist: str | None) -> list[str]:
        discovered: list[str] = []
        try:
            discovered = market_service.discover_liquid_symbols(
                market=market,
                target_count=settings.HIGH_CONFIDENCE_DISCOVERY_TARGET,
                per_query_limit=settings.HIGH_CONFIDENCE_DISCOVERY_QUERY_LIMIT,
            )
        except Exception as exc:
            logger.warning(f"Symbol universe discovery failed; falling back to static list: {exc}")

        candidates: list[str] = []
        seen: set[str] = set()

        for ticker in discovered + settings.HIGH_CONFIDENCE_UNIVERSE + self._parse_watchlist(watchlist):
            normalized = self._normalize_ticker(ticker)
            if not normalized or normalized in seen:
                continue
            if not self._market_matches_ticker(normalized, market):
                continue
            seen.add(normalized)
            candidates.append(normalized)

        return candidates

    def _collect_predictions_batch(
        self,
        tickers: list[str],
        refresh: bool,
    ) -> list[dict[str, Any]]:
        if not tickers:
            return []

        max_workers = max(1, min(settings.HIGH_CONFIDENCE_MAX_WORKERS, len(tickers)))
        if max_workers == 1:
            collected = [self._predict_ticker(ticker, refresh=refresh) for ticker in tickers]
            return [item for item in collected if item is not None]

        predictions: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(self._predict_ticker, ticker, refresh): ticker
                for ticker in tickers
            }

            for future in as_completed(future_map):
                ticker = future_map[future]
                try:
                    prediction = future.result()
                except Exception as exc:
                    logger.warning(f"Batch prediction failed for {ticker}: {exc}")
                    continue

                if prediction is not None:
                    predictions.append(prediction)

        return predictions

    @staticmethod
    def _dynamic_confidence_tier(
        confidence: float,
        model_auc: float,
        confidence_threshold: float,
        min_auc: float,
    ) -> tuple[str, bool]:
        if confidence >= confidence_threshold and model_auc >= min_auc:
            return "very_high", True
        if confidence >= max(0.20, confidence_threshold * 0.75) and model_auc >= max(0.50, min_auc * 0.9):
            return "high", False
        if confidence >= max(0.12, confidence_threshold * 0.5):
            return "medium", False
        return "low", False

    def _apply_thresholds(
        self,
        predictions: list[dict[str, Any]],
        confidence_threshold: float,
        min_auc: float,
    ) -> list[dict[str, Any]]:
        scored: list[dict[str, Any]] = []
        for prediction in predictions:
            item = dict(prediction)
            confidence = float(item.get("confidence", 0.0))
            model_auc = float(item.get("model_auc", 0.0))
            tier, is_very_high = self._dynamic_confidence_tier(
                confidence,
                model_auc,
                confidence_threshold,
                min_auc,
            )
            item["confidence_tier"] = tier
            item["is_very_high_confidence"] = is_very_high
            scored.append(item)
        return scored

    def _attach_news_batch(self, items: list[dict[str, Any]]) -> None:
        if not items:
            return

        max_workers = max(1, min(settings.HIGH_CONFIDENCE_NEWS_MAX_WORKERS, len(items)))
        if max_workers == 1:
            for item in items:
                item["news"] = news_service.get_stock_news(item["ticker"], limit=2)
            return

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(news_service.get_stock_news, item["ticker"], 2): index
                for index, item in enumerate(items)
            }

            for future in as_completed(future_map):
                index = future_map[future]
                try:
                    items[index]["news"] = future.result()
                except Exception as exc:
                    logger.warning(f"Failed to fetch dashboard news for {items[index]['ticker']}: {exc}")
                    items[index]["news"] = []

    def get_high_confidence_predictions(
        self,
        *,
        market: str = "ALL",
        limit: int | None = None,
        watchlist: str | None = None,
        include_news: bool = False,
        refresh: bool = False,
        confidence_threshold: float | None = None,
        min_auc: float | None = None,
    ) -> dict[str, Any]:
        normalized_market = self._normalize_market(market)
        bounded_limit = max(
            1,
            min(limit or settings.HIGH_CONFIDENCE_DEFAULT_LIMIT, settings.HIGH_CONFIDENCE_MAX_RESULTS),
        )
        resolved_confidence, resolved_min_auc = self._resolve_thresholds(
            confidence_threshold,
            min_auc,
        )

        snapshot_key = self._snapshot_cache_key(
            normalized_market,
            bounded_limit,
            watchlist,
            include_news,
            resolved_confidence,
            resolved_min_auc,
        )

        if not refresh:
            snapshot = cache.get(snapshot_key)
            if snapshot is not None:
                cached_response = dict(snapshot)
                cached_response["cache_hit"] = True
                return cached_response

        tickers = self._build_universe(normalized_market, watchlist)
        all_predictions = self._collect_predictions_batch(tickers, refresh=refresh)
        scored_predictions = self._apply_thresholds(
            all_predictions,
            resolved_confidence,
            resolved_min_auc,
        )

        qualified = [item for item in scored_predictions if item.get("is_very_high_confidence")]
        ranked = sorted(
            qualified,
            key=lambda item: (
                float(item.get("confidence", 0.0)),
                abs(float(item.get("probability_up", 0.5)) - 0.5),
                float(item.get("model_auc", 0.0)),
            ),
            reverse=True,
        )

        trimmed = [dict(item) for item in ranked[:bounded_limit]]
        if include_news:
            self._attach_news_batch(trimmed)

        result = {
            "items": trimmed,
            "evaluated_tickers": len(tickers),
            "qualified_count": len(qualified),
            "market": normalized_market,
            "thresholds": {
                "confidence": resolved_confidence,
                "model_auc": resolved_min_auc,
            },
            "generated_at": datetime.utcnow().isoformat(),
            "cache_hit": False,
        }

        cache.set(snapshot_key, result, ttl=settings.HIGH_CONFIDENCE_SNAPSHOT_TTL)
        return result

    def refresh_high_confidence_snapshot(
        self,
        *,
        market: str = "ALL",
        limit: int | None = None,
        watchlist: str | None = None,
        include_news: bool = False,
        confidence_threshold: float | None = None,
        min_auc: float | None = None,
    ) -> dict[str, Any]:
        return self.get_high_confidence_predictions(
            market=market,
            limit=limit,
            watchlist=watchlist,
            include_news=include_news,
            refresh=True,
            confidence_threshold=confidence_threshold,
            min_auc=min_auc,
        )


dashboard_service = DashboardService()
