from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import json
import os
import traceback

from src.pipelines.inference_pipeline import run_inference_pipeline
from src.pipelines.backtest_pipeline import run_backtest_pipeline

# ============================================================================
# FastAPI App Initialization
# ============================================================================

app = FastAPI(
    title="Stock Market ML API",
    description="Machine Learning API for stock market predictions using technical analysis",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================================
# CORS Configuration
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["http://localhost:3000", "https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Pydantic Models (Request/Response Schemas)
# ============================================================================

class PredictionRequest(BaseModel):
    """Request model for stock prediction"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA)", example="AAPL")
    start_date: Optional[str] = Field(None, description="Start date in YYYY-MM-DD format", example="2023-01-01")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format", example="2024-12-31")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "NVDA",
                "start_date": "2023-01-01",
                "end_date": "2024-12-31"
            }
        }


class BacktestRequest(BaseModel):
    """Request model for backtesting"""
    ticker: str = Field(..., description="Stock ticker symbol", example="TSLA")
    start_date: Optional[str] = Field(None, description="Start date for backtest", example="2022-01-01")
    end_date: Optional[str] = Field(None, description="End date for backtest", example="2024-12-31")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "TSLA",
                "start_date": "2022-01-01",
                "end_date": "2024-12-31"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str
    models_available: int


class APIResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None


# ============================================================================
# Root & Health Check Endpoints
# ============================================================================

@app.get("/", tags=["Health"])
def read_root():
    """
    Root endpoint - API welcome message
    """
    return {
        "message": "🚀 Welcome to Stock Market ML API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "predict": "POST /api/predict",
            "backtest": "POST /api/backtest",
            "stock_info": "GET /api/stock/{ticker}",
            "models": "GET /api/models",
            "health": "GET /api/health"
        }
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Detailed health check endpoint
    
    Returns system status and available models count
    """
    try:
        models_count = 0
        if os.path.exists("models"):
            model_files = [f for f in os.listdir("models") if f.endswith("_model.pkl")]
            models_count = len(model_files)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "models_available": models_count
        }
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "models_available": 0
        }


# ============================================================================
# Prediction Endpoints
# ============================================================================

@app.post("/api/predict", tags=["Predictions"])
async def predict_stock(request: PredictionRequest):
    """
    Get ML prediction for a stock ticker
    
    **This endpoint:**
    - Fetches historical stock data
    - Calculates technical indicators
    - Trains ML model
    - Returns probability of price going UP next day
    
    **Parameters:**
    - ticker: Stock symbol (e.g., AAPL, NVDA, TSLA)
    - start_date: Optional start date (YYYY-MM-DD)
    - end_date: Optional end date (YYYY-MM-DD)
    
    **Returns:**
    - Prediction with probability, confidence, and interpretation
    """
    try:
        # Validate ticker
        ticker = request.ticker.upper().strip()
        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker symbol is required")
        
        # Run inference pipeline
        result = run_inference_pipeline(
            ticker=ticker,
            start=request.start_date,
            end=request.end_date
        )
        
        return {
            "success": True,
            "message": f"Prediction generated successfully for {ticker}",
            "data": result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in predict endpoint: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/stock/{ticker}", tags=["Predictions"])
def get_stock_prediction(ticker: str):
    """
    Get latest saved prediction for a ticker
    
    **Parameters:**
    - ticker: Stock symbol
    
    **Returns:**
    - Latest prediction from outputs folder (if available)
    
    **Note:** Run `/api/predict` first to generate prediction
    """
    try:
        ticker = ticker.upper().strip()
        output_file = f"outputs/{ticker}.json"
        
        if not os.path.exists(output_file):
            raise HTTPException(
                status_code=404,
                detail=f"No prediction found for {ticker}. Run POST /api/predict first."
            )
        
        with open(output_file, "r") as f:
            data = json.load(f)
        
        return {
            "success": True,
            "message": f"Retrieved prediction for {ticker}",
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reading prediction: {str(e)}"
        )


# ============================================================================
# Backtest Endpoints
# ============================================================================

@app.post("/api/backtest", tags=["Backtesting"])
async def backtest_stock(request: BacktestRequest):
    """
    Run walk-forward backtesting on a stock
    
    **This endpoint:**
    - Performs walk-forward validation
    - Tests model on historical data
    - Returns accuracy metrics
    
    **Parameters:**
    - ticker: Stock symbol
    - start_date: Optional start date
    - end_date: Optional end date
    
    **Returns:**
    - Backtest results with accuracy metrics
    """
    try:
        ticker = request.ticker.upper().strip()
        
        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker symbol is required")
        
        # Run backtest pipeline
        results = run_backtest_pipeline(
            ticker=ticker,
            start=request.start_date,
            end=request.end_date
        )
        
        return {
            "success": True,
            "message": f"Backtest completed for {ticker}",
            "data": results
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in backtest endpoint: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# ============================================================================
# Model Management Endpoints
# ============================================================================

@app.get("/api/models", tags=["Models"])
def list_trained_models():
    """
    List all trained models
    
    **Returns:**
    - List of ticker symbols with trained models
    - Count of available models
    """
    try:
        if not os.path.exists("models"):
            return {
                "success": True,
                "message": "No models directory found",
                "data": {
                    "models": [],
                    "count": 0
                }
            }
        
        # Find all model files
        model_files = [f for f in os.listdir("models") if f.endswith("_model.pkl")]
        tickers = [f.replace("_model.pkl", "") for f in model_files]
        
        # Get model details
        models_info = []
        for ticker in tickers:
            model_path = f"models/{ticker}_model.pkl"
            scaler_path = f"models/{ticker}_scaler.pkl"
            
            model_stat = os.stat(model_path)
            
            models_info.append({
                "ticker": ticker,
                "model_file": model_path,
                "has_scaler": os.path.exists(scaler_path),
                "created_at": datetime.fromtimestamp(model_stat.st_mtime).isoformat(),
                "size_kb": round(model_stat.st_size / 1024, 2)
            })
        
        return {
            "success": True,
            "message": f"Found {len(tickers)} trained models",
            "data": {
                "models": models_info,
                "count": len(tickers)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing models: {str(e)}"
        )


@app.delete("/api/models/{ticker}", tags=["Models"])
def delete_model(ticker: str):
    """
    Delete a trained model
    
    **Parameters:**
    - ticker: Stock symbol
    
    **Returns:**
    - Deletion confirmation
    """
    try:
        ticker = ticker.upper().strip()
        
        model_path = f"models/{ticker}_model.pkl"
        scaler_path = f"models/{ticker}_scaler.pkl"
        
        deleted_files = []
        
        if os.path.exists(model_path):
            os.remove(model_path)
            deleted_files.append(model_path)
        
        if os.path.exists(scaler_path):
            os.remove(scaler_path)
            deleted_files.append(scaler_path)
        
        if not deleted_files:
            raise HTTPException(
                status_code=404,
                detail=f"No model found for {ticker}"
            )
        
        return {
            "success": True,
            "message": f"Model deleted for {ticker}",
            "data": {
                "ticker": ticker,
                "deleted_files": deleted_files
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting model: {str(e)}"
        )


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Endpoint not found",
            "detail": str(exc.detail) if hasattr(exc, 'detail') else "Not found"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "detail": "An unexpected error occurred"
        }
    )


# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Stock Market ML API Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("📊 ReDoc: http://localhost:8000/redoc")
    print("💚 Health Check: http://localhost:8000/api/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (disable in production)
    )