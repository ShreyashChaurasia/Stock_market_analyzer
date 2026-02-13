import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


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


def test_predict_valid_ticker():
    """Test prediction with valid ticker"""
    response = client.post(
        "/api/predict",
        json={"ticker": "AAPL", "period": "1y"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "prediction" in data


def test_predict_invalid_ticker():
    """Test prediction with invalid ticker"""
    response = client.post(
        "/api/predict",
        json={"ticker": "INVALID123", "period": "1y"}
    )
    assert response.status_code == 422


def test_predict_missing_ticker():
    """Test prediction without ticker"""
    response = client.post(
        "/api/predict",
        json={"period": "1y"}
    )
    assert response.status_code == 422