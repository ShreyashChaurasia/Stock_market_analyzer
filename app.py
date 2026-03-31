from contextlib import asynccontextmanager
from datetime import datetime
import os
import time

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config import settings
from src.core.prediction_data import fetch_prepared_prediction_frames
from src.core.logger import get_logger
from src.core.exceptions import StockAnalyzerException
from src.middleware.error_handler import (
    stock_analyzer_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from src.middleware.logging_middleware import LoggingMiddleware
from src.schemas.prediction import PredictionRequest, PredictionResponse
from src.schemas.stock import HealthResponse
from src.schemas.verification import (
    BacktestVerificationResponse,
    LiveVerificationSummaryResponse,
)
from src.pipelines.inference_pipeline import run_inference_pipeline
from src.services.model_service import ModelService
from src.registry.model_registry import registry
from src.services.market_data_service import market_service
from src.services.news_service import news_service
from src.services.dashboard_service import dashboard_service
from src.verification.service import verification_service

logger = get_logger(__name__)

# Track startup time
startup_time = time.time()

# Initialize services
model_service = ModelService()


def _load_training_dataframe(ticker: str):
    frames = fetch_prepared_prediction_frames(ticker=ticker)
    return frames.training_df


# Lifespan (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    yield
    # Shutdown
    logger.info("Shutting down application")


# App Initialization
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ALLOW_ORIGIN_REGEX,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_middleware(LoggingMiddleware)


# Exception Handlers
app.add_exception_handler(StockAnalyzerException, stock_analyzer_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# Health Routes
@app.get("/", tags=["Health"])
def read_root():
    """API welcome message"""
    return {
        "message": "Welcome to Stock Market ML API",
        "version": settings.API_VERSION,
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Detailed health check"""
    models_count = 0
    if os.path.exists(settings.MODEL_DIR):
        model_files = [
            f for f in os.listdir(settings.MODEL_DIR)
            if f.endswith("_model.pkl")
        ]
        models_count = len(model_files)

    uptime = time.time() - startup_time

    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": settings.API_VERSION,
        "models_available": models_count,
        "uptime_seconds": round(uptime, 2)
    }


# Prediction Routes
@app.post("/api/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_stock(request: PredictionRequest):
    """
    Get ML prediction for a stock ticker

    Fetches data, trains model, and returns probability of price
    going UP the next trading day.
    """
    logger.info(f"Prediction request for {request.ticker}")

    result = run_inference_pipeline(
        ticker=request.ticker,
        start=request.start_date,
        end=request.end_date,
        period=request.period,
    )

    return result


@app.post("/api/predict-with-version", tags=["Predictions"])
async def predict_with_version(version_id: str, ticker: str):
    """
    Make prediction using a specific trained model version

    Args:
        version_id: Model version ID from registry
        ticker: Stock symbol to fetch latest data for
    """
    logger.info(f"Predict with version {version_id} for {ticker}")

    frames = fetch_prepared_prediction_frames(ticker=ticker, period="1y")
    df = frames.prediction_df

    result = model_service.predict_with_model(version_id, df)

    return {
        "success": True,
        "ticker": ticker,
        "prediction": result
    }


@app.get(
    "/api/verification/backtest/{ticker}",
    response_model=BacktestVerificationResponse,
    tags=["Verification"],
)
async def get_backtest_verification(
    ticker: str,
    model_type: str = "logistic",
    start_date: str | None = None,
    end_date: str | None = None,
    refresh: bool = False,
):
    """Get or generate a historical walk-forward verification report."""
    try:
        return verification_service.get_backtest_report(
            ticker=ticker.upper(),
            model_type=model_type,
            start_date=start_date,
            end_date=end_date,
            refresh=refresh,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get(
    "/api/verification/live/{ticker}",
    response_model=LiveVerificationSummaryResponse,
    tags=["Verification"],
)
async def get_live_verification(
    ticker: str,
    model_type: str | None = None,
    refresh: bool = False,
):
    """Resolve and summarize live prediction accuracy for a ticker."""
    try:
        return verification_service.get_live_verification_summary(
            ticker=ticker.upper(),
            model_type=model_type,
            refresh=refresh,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


# Model Training Routes
@app.post("/api/train-model", tags=["Models"])
async def train_single_model(
    ticker: str,
    model_type: str = "logistic",
    tune: bool = False
):
    """
    Train a specific model type for a ticker

    Args:
        ticker: Stock symbol
        model_type: logistic, random_forest, xgboost, gradient_boosting
        tune: Whether to run hyperparameter tuning
    """
    logger.info(f"Training {model_type} for {ticker}")

    df = _load_training_dataframe(ticker)

    result = model_service.train_single_model(df, ticker, model_type, tune)

    return {
        "success": True,
        "message": f"Model {model_type} trained for {ticker}",
        "data": result
    }


@app.post("/api/compare-models", tags=["Models"])
async def compare_models(ticker: str):
    """
    Train and compare all available models for a ticker

    Args:
        ticker: Stock symbol
    """
    logger.info(f"Comparing all models for {ticker}")

    df = _load_training_dataframe(ticker)

    result = model_service.train_all_models(df, ticker)

    return {
        "success": True,
        "message": f"Trained and compared all models for {ticker}",
        "data": result
    }


# Model Registry Routes
@app.get("/api/model-versions/{ticker}", tags=["Models"])
async def list_model_versions(ticker: str):
    """
    List all trained model versions for a ticker

    Args:
        ticker: Stock symbol
    """
    models = registry.list_models(ticker=ticker)

    return {
        "success": True,
        "ticker": ticker,
        "total_models": len(models),
        "models": models
    }


@app.get("/api/best-model/{ticker}", tags=["Models"])
async def get_best_model(ticker: str, metric: str = "auc"):
    """
    Get the best performing model for a ticker

    Args:
        ticker: Stock symbol
        metric: Metric to rank by (auc, accuracy, f1_score, precision, recall)
    """
    best_model = registry.get_best_model(ticker, metric)

    if not best_model:
        raise HTTPException(
            status_code=404,
            detail=f"No trained models found for {ticker}"
        )

    return {
        "success": True,
        "ticker": ticker,
        "metric": metric,
        "best_model": best_model
    }


@app.get("/api/models", tags=["Models"])
def list_all_models():
    """
    List all trained models across all tickers
    """
    models = registry.list_models()

    return {
        "success": True,
        "total_models": len(models),
        "models": models
    }


@app.delete("/api/model-versions/{version_id}", tags=["Models"])
async def delete_model_version(version_id: str):
    """
    Delete a specific model version

    Args:
        version_id: Model version ID to delete
    """
    try:
        registry.delete_model(version_id)
        return {
            "success": True,
            "message": f"Model version {version_id} deleted"
        }
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Model version {version_id} not found"
        )

@app.get("/api/market/indices", tags=["Market Data"])
async def get_market_indices():
    """
    Get real-time data for major market indices
    
    Returns current prices and changes for:
    - NASDAQ
    - Dow Jones
    - NIFTY 50
    - SENSEX
    """
    logger.info("Fetching market indices data")
    
    try:
        indices = market_service.get_all_indices()
        
        return {
            "success": True,
            "data": indices,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching market indices: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch market data: {str(e)}"
        )


@app.get("/api/market/stock-info/{ticker}", tags=["Market Data"])
async def get_stock_info(ticker: str):
    """
    Get detailed information about a stock
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Company info, market cap, P/E ratio, 52-week high/low, etc.
    """
    logger.info(f"Fetching stock info for {ticker}")
    
    try:
        info = market_service.get_stock_info(ticker.upper())
        
        if not info:
            raise HTTPException(
                status_code=404,
                detail=f"Could not fetch info for {ticker}"
            )
        
        return {
            "success": True,
            "data": info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stock info: {str(e)}"
        )


@app.get("/api/market/technical-indicators/{ticker}", tags=["Market Data"])
async def get_technical_indicators(ticker: str):
    """
    Get real technical indicators for a stock
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        RSI, MACD, SMA, Bollinger Bands with buy/sell signals
    """
    logger.info(f"Calculating technical indicators for {ticker}")
    
    try:
        indicators = market_service.get_technical_indicators(ticker.upper())
        
        if not indicators:
            raise HTTPException(
                status_code=404,
                detail=f"Could not calculate indicators for {ticker}"
            )
        
        return {
            "success": True,
            "data": indicators
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating indicators: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate indicators: {str(e)}"
        )


@app.get("/api/market/historical-prices/{ticker}", tags=["Market Data"])
async def get_historical_prices(
    ticker: str,
    period: str = "1m"
):
    """
    Get historical price data for charting
    
    Args:
        ticker: Stock ticker symbol
        period: Time period key (1d, 1w, 1m, 3m, 6m, 1y, 5y, all)
        
    Returns:
        Historical prices with moving averages
    """
    logger.info(f"Fetching historical prices for {ticker} (period: {period})")
    
    try:
        prices = market_service.get_historical_prices(ticker.upper(), period)
        
        return {
            "success": True,
            "ticker": ticker.upper(),
            "period": period,
            "interval": prices["interval"],
            "currency": prices["currency"],
            "data": prices["data"],
        }
    except Exception as e:
        logger.error(f"Error fetching historical prices: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch historical prices: {str(e)}"
        )


@app.get("/api/market/index-historical/{market}", tags=["Market Data"])
async def get_index_historical_prices(
    market: str,
    period: str = "1m"
):
    """
    Get historical chart data for supported market indices.

    Args:
        market: Index key (nasdaq, dowjones, nifty50, sensex)
            aliases "nse" and "bse" are also supported
        period: Time period key (1d, 1w, 1m, 3m, 6m, 1y, 5y, all)
    """
    logger.info(f"Fetching index historical prices for {market} (period: {period})")

    try:
        prices = market_service.get_index_historical_prices(market, period)
        return {
            "success": True,
            "market": prices["market"],
            "name": prices["name"],
            "symbol": prices["symbol"],
            "period": prices["period"],
            "interval": prices["interval"],
            "currency": prices["currency"],
            "data": prices["data"],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching index historical prices: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch index historical prices: {str(e)}"
        )


@app.get("/api/market/search", tags=["Market Data"])
async def search_market_symbols(
    q: str,
    market: str = "ALL",
    limit: int = 8,
):
    """
    Search stocks by symbol or company name.

    Args:
        q: Query text (ticker or company name)
        market: ALL, US, or INDIA
        limit: Maximum results (1-20)
    """
    normalized_query = (q or "").strip()
    if not normalized_query:
        return {"success": True, "query": q, "results": []}

    bounded_limit = max(1, min(limit, 20))
    normalized_market = (market or "ALL").upper()
    if normalized_market not in {"ALL", "US", "INDIA"}:
        raise HTTPException(status_code=400, detail="market must be one of: ALL, US, INDIA")

    try:
        results = market_service.search_symbols(
            query=normalized_query,
            market=normalized_market,
            limit=bounded_limit,
        )
        return {
            "success": True,
            "query": normalized_query,
            "market": normalized_market,
            "results": results,
        }
    except Exception as e:
        logger.error(f"Error searching symbols for '{normalized_query}': {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search symbols: {str(e)}"
        )


@app.get("/api/news/latest", tags=["News"])
async def get_latest_news(limit: int = 10, market: str = "ALL"):
    """
    Get latest market news.

    Args:
        limit: Maximum number of articles (1-30)
        market: ALL, US, or INDIA
    """
    bounded_limit = max(1, min(limit, 30))
    normalized_market = (market or "ALL").upper()

    if normalized_market not in {"ALL", "US", "INDIA"}:
        raise HTTPException(status_code=400, detail="market must be one of: ALL, US, INDIA")

    try:
        articles = news_service.get_latest_news(limit=bounded_limit, market=normalized_market)
        return {
            "success": True,
            "provider": news_service.provider,
            "market": normalized_market,
            "total": len(articles),
            "data": articles,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error fetching latest news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest news: {str(e)}")


@app.get("/api/news/trending", tags=["News"])
async def get_trending_news(limit: int = 10, market: str = "ALL"):
    """
    Get trending market news and ticker mention counts.

    Args:
        limit: Maximum number of articles/tickers (1-20)
        market: ALL, US, or INDIA
    """
    bounded_limit = max(1, min(limit, 20))
    normalized_market = (market or "ALL").upper()

    if normalized_market not in {"ALL", "US", "INDIA"}:
        raise HTTPException(status_code=400, detail="market must be one of: ALL, US, INDIA")

    try:
        result = news_service.get_trending_news(limit=bounded_limit, market=normalized_market)
        return {
            "success": True,
            **result,
        }
    except Exception as e:
        logger.error(f"Error fetching trending news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending news: {str(e)}")


@app.get("/api/news/stock/{ticker}", tags=["News"])
async def get_stock_news(ticker: str, limit: int = 10):
    """
    Get latest news related to a specific stock ticker.

    Args:
        ticker: Stock ticker symbol
        limit: Maximum number of articles (1-20)
    """
    normalized_ticker = (ticker or "").strip().upper()
    if not normalized_ticker:
        raise HTTPException(status_code=400, detail="ticker is required")

    bounded_limit = max(1, min(limit, 20))

    try:
        articles = news_service.get_stock_news(normalized_ticker, limit=bounded_limit)
        return {
            "success": True,
            "provider": news_service.provider,
            "ticker": normalized_ticker,
            "total": len(articles),
            "data": articles,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error fetching stock news for {normalized_ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock news: {str(e)}")


@app.get("/api/dashboard/high-confidence", tags=["Dashboard"])
async def get_high_confidence_dashboard(
    market: str = "ALL",
    limit: int = settings.HIGH_CONFIDENCE_DEFAULT_LIMIT,
    watchlist: str | None = None,
    include_news: bool = False,
    refresh: bool = False,
    confidence_threshold: float | None = None,
    min_auc: float | None = None,
):
    """
    Get stocks ranked for Quant Discovery.

    Args:
        market: ALL, US, or INDIA
        limit: Maximum stocks to return (1-100)
        watchlist: Optional comma-separated symbols from user watchlist
        include_news: Include top 2 related articles for each stock
        refresh: Ignore cache and force fresh predictions
        confidence_threshold: Override confidence threshold (0-1)
        min_auc: Override minimum AUC threshold (0-1)
    """
    try:
        result = dashboard_service.get_high_confidence_predictions(
            market=market,
            limit=limit,
            watchlist=watchlist,
            include_news=include_news,
            refresh=refresh,
            confidence_threshold=confidence_threshold,
            min_auc=min_auc,
        )
        return {
            "success": True,
            **result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error building quant discovery dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build quant discovery dashboard: {str(e)}",
        )


@app.post("/api/dashboard/high-confidence/refresh", tags=["Dashboard"])
async def refresh_high_confidence_dashboard(
    market: str = "ALL",
    limit: int = settings.HIGH_CONFIDENCE_DEFAULT_LIMIT,
    watchlist: str | None = None,
    include_news: bool = False,
    confidence_threshold: float | None = None,
    min_auc: float | None = None,
):
    """
    Force-refresh Quant Discovery snapshot cache in batched mode.

    Args:
        market: ALL, US, or INDIA
        limit: Maximum stocks to return (1-100)
        watchlist: Optional comma-separated symbols from user watchlist
        include_news: Include top 2 related articles for each stock
        confidence_threshold: Override confidence threshold (0-1)
        min_auc: Override minimum AUC threshold (0-1)
    """
    try:
        result = dashboard_service.refresh_high_confidence_snapshot(
            market=market,
            limit=limit,
            watchlist=watchlist,
            include_news=include_news,
            confidence_threshold=confidence_threshold,
            min_auc=min_auc,
        )
        return {
            "success": True,
            "message": "Quant Discovery snapshot refreshed",
            **result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error refreshing quant discovery dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh quant discovery dashboard: {str(e)}",
        )

# Entry Point
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Stock Market ML API Server")
    logger.info(f"Documentation: http://{settings.API_HOST}:{settings.API_PORT}/docs")

    uvicorn.run(
        "app:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
