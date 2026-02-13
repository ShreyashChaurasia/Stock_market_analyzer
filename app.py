from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time

from src.core.config import settings
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
from src.schemas.stock import HealthResponse, ModelInfo
from src.pipelines.inference_pipeline import run_inference_pipeline

logger = get_logger(__name__)

# Track startup time
startup_time = time.time()

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Register exception handlers
app.add_exception_handler(StockAnalyzerException, stock_analyzer_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")


# Routes
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
    import os
    
    models_count = 0
    if os.path.exists(settings.MODEL_DIR):
        model_files = [f for f in os.listdir(settings.MODEL_DIR) if f.endswith("_model.pkl")]
        models_count = len(model_files)
    
    uptime = time.time() - startup_time
    
    return {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "version": settings.API_VERSION,
        "models_available": models_count,
        "uptime_seconds": round(uptime, 2)
    }


@app.post("/api/predict", response_model=PredictionResponse, tags=["Predictions"])
async def predict_stock(request: PredictionRequest):
    """Get ML prediction for a stock ticker"""
    logger.info(f"Prediction request for {request.ticker}")
    
    result = run_inference_pipeline(
        ticker=request.ticker,
        start=request.start_date,
        end=request.end_date
    )
    
    return result


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