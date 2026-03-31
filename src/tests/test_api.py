import pytest
from fastapi.testclient import TestClient
from app import app
from src.core.exceptions import DataFetchError

client = TestClient(app)


def _mock_prediction_response(ticker: str) -> dict:
    return {
        "ticker": ticker,
        "prediction_date": "2026-03-31 10:00:00",
        "latest_data_date": "2026-03-30",
        "latest_close": 210.25,
        "currency": "USD",
        "probability_up": 0.64,
        "probability_down": 0.36,
        "prediction": "UP",
        "confidence": 0.28,
        "confidence_percent": "28.0%",
        "confidence_tier": "high",
        "is_very_high_confidence": False,
        "model_auc": 0.58,
        "data_points_used": 128,
        "interpretation": "Moderate signal for price to increase",
        "model_type": "logistic",
        "prediction_id": "pred-123",
        "verification_status": "pending",
        "verification_balanced_accuracy": 0.56,
        "verification_sample_count": 128,
    }


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_check():
    """Test health endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_predict_valid_ticker(monkeypatch):
    """Test prediction with valid ticker"""
    monkeypatch.setattr("app.run_inference_pipeline", lambda **_: _mock_prediction_response("AAPL"))

    response = client.post(
        "/api/predict",
        json={"ticker": "AAPL", "period": "1y"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "prediction" in data
    assert data["prediction_id"] == "pred-123"
    assert data["verification_balanced_accuracy"] == 0.56


def test_predict_invalid_ticker(monkeypatch):
    """Test prediction with invalid ticker"""
    def _raise_invalid(**_):
        raise DataFetchError("INVALID123", "Ticker not found")

    monkeypatch.setattr("app.run_inference_pipeline", _raise_invalid)

    response = client.post(
        "/api/predict",
        json={"ticker": "INVALID123", "period": "1y"}
    )
    assert response.status_code == 400


def test_predict_missing_ticker():
    """Test prediction without ticker"""
    response = client.post(
        "/api/predict",
        json={"period": "1y"}
    )
    assert response.status_code == 422


def test_news_latest_invalid_market():
    """News endpoint validates market filter values."""
    response = client.get("/api/news/latest?market=INVALID")
    assert response.status_code == 400


def test_news_latest_success(monkeypatch):
    """Latest news endpoint returns normalized payload."""
    mock_articles = [
        {
            "title": "Apple extends AI roadmap",
            "description": "The company shared new updates for investors.",
            "url": "https://example.com/article-1",
            "source": "Example",
            "published_at": "2026-03-30T10:00:00",
            "image_url": None,
            "tickers": ["AAPL"],
            "market": "US",
        }
    ]
    monkeypatch.setattr("app.news_service.get_latest_news", lambda limit, market: mock_articles)

    response = client.get("/api/news/latest?market=US&limit=5")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["market"] == "US"
    assert data["total"] == 1
    assert data["data"][0]["title"] == "Apple extends AI roadmap"


def test_stock_news_success(monkeypatch):
    """Stock-specific news endpoint returns ticker-linked articles."""
    mock_articles = [
        {
            "title": "Reliance plans capex expansion",
            "description": "Analysts expect stronger growth in FY27.",
            "url": "https://example.com/reliance-news",
            "source": "Example",
            "published_at": "2026-03-30T09:00:00",
            "image_url": None,
            "tickers": ["RELIANCE.NS"],
            "market": "INDIA",
        }
    ]
    monkeypatch.setattr("app.news_service.get_stock_news", lambda ticker, limit: mock_articles)

    response = client.get("/api/news/stock/RELIANCE.NS?limit=3")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["ticker"] == "RELIANCE.NS"
    assert data["total"] == 1


def test_high_confidence_dashboard_success(monkeypatch):
    """High-confidence dashboard endpoint returns aggregated payload."""
    mock_response = {
        "items": [
            {
                "ticker": "TSLA",
                "prediction": "DOWN",
                "confidence": 0.41,
                "confidence_percent": "41.0%",
                "confidence_tier": "very_high",
                "is_very_high_confidence": True,
                "model_auc": 0.59,
                "probability_up": 0.29,
                "probability_down": 0.71,
                "latest_close": 210.0,
                "currency": "USD",
                "prediction_date": "2026-03-30 10:20:00",
                "latest_data_date": "2026-03-30",
                "interpretation": "Strong signal for price to decrease",
                "source": "pipeline",
                "news": [],
            }
        ],
        "evaluated_tickers": 8,
        "qualified_count": 1,
        "market": "ALL",
        "thresholds": {"confidence": 0.3, "model_auc": 0.5},
        "generated_at": "2026-03-30T10:20:30",
    }
    monkeypatch.setattr(
        "app.dashboard_service.get_high_confidence_predictions",
        lambda **_: mock_response,
    )

    response = client.get("/api/dashboard/high-confidence?market=ALL&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["qualified_count"] == 1
    assert data["items"][0]["ticker"] == "TSLA"


def test_high_confidence_dashboard_custom_thresholds(monkeypatch):
    """High-confidence endpoint forwards custom threshold query params."""
    captured: dict[str, object] = {}

    def _mock_get_high_confidence_predictions(**kwargs):
        captured.update(kwargs)
        return {
            "items": [],
            "evaluated_tickers": 0,
            "qualified_count": 0,
            "market": kwargs.get("market", "ALL"),
            "thresholds": {
                "confidence": kwargs.get("confidence_threshold", 0.3),
                "model_auc": kwargs.get("min_auc", 0.5),
            },
            "generated_at": "2026-03-30T11:00:00",
            "cache_hit": False,
        }

    monkeypatch.setattr(
        "app.dashboard_service.get_high_confidence_predictions",
        _mock_get_high_confidence_predictions,
    )

    response = client.get(
        "/api/dashboard/high-confidence?market=US&limit=5&confidence_threshold=0.4&min_auc=0.6"
    )

    assert response.status_code == 200
    assert captured["market"] == "US"
    assert captured["limit"] == 5
    assert captured["confidence_threshold"] == 0.4
    assert captured["min_auc"] == 0.6


def test_high_confidence_dashboard_refresh_success(monkeypatch):
    """Refresh endpoint triggers batched snapshot refresh service call."""
    monkeypatch.setattr(
        "app.dashboard_service.refresh_high_confidence_snapshot",
        lambda **_: {
            "items": [],
            "evaluated_tickers": 5,
            "qualified_count": 0,
            "market": "ALL",
            "thresholds": {"confidence": 0.3, "model_auc": 0.5},
            "generated_at": "2026-03-30T11:10:00",
            "cache_hit": False,
        },
    )

    response = client.post("/api/dashboard/high-confidence/refresh?market=ALL&limit=8")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Quant Discovery snapshot refreshed"
