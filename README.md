# Stock Market Analyzer

A full-stack stock analysis platform combining machine learning predictions, real-time market data, technical indicators, and interactive dashboards for both US and Indian equity markets.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Machine Learning Pipeline](#machine-learning-pipeline)
- [Supported Markets and Tickers](#supported-markets-and-tickers)
- [Running Tests](#running-tests)
- [License](#license)

---

## Overview

Stock Market Analyzer is a research-oriented platform that applies supervised machine learning to classify next-day stock price direction (UP or DOWN). The backend exposes a REST API built with FastAPI, and the frontend provides an interactive React dashboard with candlestick charting, live index data, technical indicator panels, a model comparison view, and a watchlist.

---

## Features

**Predictions and ML**
- Next-day price direction prediction (UP / DOWN) with model confidence and probability scores
- Inference pipeline: data fetch, indicator calculation, feature engineering, model training, and prediction in a single call
- Support for training and comparing four model types per ticker: Logistic Regression, Random Forest, Gradient Boosting, and XGBoost
- Model versioning and registry with best-model selection by AUC, accuracy, F1, precision, or recall
- Hyperparameter tuning support

**Market Data**
- Live snapshot of major global indices: NASDAQ, Dow Jones, NIFTY 50, SENSEX
- Historical OHLCV price data with SMA-20 and SMA-50 overlays for any ticker
- Historical chart data for supported indices across configurable time periods
- Stock fundamentals: market cap, P/E ratio, 52-week high/low, dividend yield, beta, sector, industry, company logo
- Technical indicators with buy/sell/neutral signals: RSI, MACD, SMA-20, SMA-50, Bollinger Bands
- Latest and trending market news feeds with market filtering (ALL / US / INDIA)
- Stock-specific headlines available when a ticker is selected

**Signal Discovery Dashboard**
- Separate Quant Discovery dashboard for symbols that pass confidence and model-quality thresholds
- Dashboard universe combines predefined symbols and user watchlist tickers
- Optional news enrichment for each Quant Discovery signal

**Frontend Dashboard**
- Candlestick and line charts powered by lightweight-charts
- Interactive stock search with market filter (US / India / All)
- Watchlist with persistent state via Zustand
- Model comparison charts using Recharts
- Dark and light theme toggle

---

## Architecture

```
Client (React + Vite)
        |
        | HTTP (REST)
        v
FastAPI Application (app.py)
        |
        |-- Middleware: CORS, Request Logging, Error Handling
        |
        |-- Prediction API
        |       |-- InferencePipeline
        |               |-- DataFetcher (yfinance)
        |               |-- Indicators (ta library)
        |               |-- FeatureEngineering
        |               |-- ProbabilityModel (sklearn)
        |
        |-- Models API
        |       |-- ModelService
        |       |       |-- ModelFactory (Logistic, RF, XGBoost, GBM)
        |       |       |-- HyperparameterTuning
        |       |       |-- ComparisonService
        |       |-- ModelRegistry (pkl + JSON metadata)
        |
        |-- Market Data API
                |-- MarketDataService
                        |-- yfinance (indices, historical, fundamentals)
                        |-- SymbolSearch
```

---

## Tech Stack

**Backend**

| Component | Library / Version |
|---|---|
| API Framework | FastAPI 0.115.0 |
| ASGI Server | Uvicorn 0.32.0 |
| Data Validation | Pydantic 2.9.0 |
| Data Fetching | yfinance 0.2.66 |
| Data Processing | pandas 2.2.3, numpy 2.1.3 |
| Machine Learning | scikit-learn 1.5.2, XGBoost 2.1.2 |
| Technical Indicators | ta 0.11.0 |
| Visualization (server) | Matplotlib 3.9.2, Plotly 5.24.1 |
| Logging | Loguru 0.7.2 |
| Configuration | pydantic-settings 2.5.0, python-dotenv 1.0.1 |

**Frontend**

| Component | Library / Version |
|---|---|
| Framework | React 19, TypeScript |
| Build Tool | Vite 7 |
| Styling | Tailwind CSS 3 |
| State Management | Zustand 5 |
| Server State | TanStack Query (React Query) 5 |
| Charting | lightweight-charts 5, Recharts 3 |
| HTTP Client | Axios |
| Icons | Lucide React |

---

## Project Structure

```text
Stock_market_analyzer/
|
|-- app.py                      # FastAPI application entry point; all route definitions
|-- requirements.txt            # Python dependencies
|-- test_setup.py               # Setup verification and smoke test script
|-- Procfile                    # Process declaration for deployment
|-- configs/
|   |-- model_configs.yaml      # Model configuration file
|
|-- src/
|   |-- core/
|   |   |-- config.py           # Application settings (pydantic-settings)
|   |   |-- logger.py           # Centralized logger setup
|   |   |-- data_fetcher.py     # yfinance data retrieval
|   |   |-- indicators.py       # Technical indicator computation
|   |   |-- feature_engineering.py  # ML feature construction
|   |   |-- probability_model.py    # Logistic regression probability model
|   |   |-- validators.py       # Input validation utilities
|   |   |-- exceptions.py       # Custom exception types
|   |   |-- yfinance_config.py  # yfinance session configuration
|   |
|   |-- models/
|   |   |-- base_model.py       # Abstract base class for all ML models
|   |   |-- logistic_model.py   # Logistic Regression implementation
|   |   |-- random_forest_model.py  # Random Forest implementation
|   |   |-- gradient_boosting_model.py  # Gradient Boosting implementation
|   |   |-- xgboost_model.py    # XGBoost implementation
|   |   |-- model_factory.py    # Factory for model instantiation
|   |
|   |-- pipelines/
|   |   |-- inference_pipeline.py   # End-to-end prediction pipeline
|   |   |-- backtest_pipeline.py    # Backtesting pipeline
|   |
|   |-- services/
|   |   |-- model_service.py        # Train, compare, and serve models
|   |   |-- market_data_service.py  # Fetch live and historical market data
|   |   |-- comparison_service.py   # Multi-model comparison logic
|   |   |-- tuning_service.py       # Hyperparameter tuning
|   |
|   |-- registry/
|   |   |-- model_registry.py   # Model versioning and persistence
|   |
|   |-- schemas/
|   |   |-- prediction.py       # Request/response Pydantic schemas
|   |   |-- stock.py            # Stock-related schemas
|   |
|   |-- middleware/
|   |   |-- error_handler.py    # Global exception handlers
|   |   |-- logging_middleware.py   # Request/response logging
|   |
|   |-- evaluation/
|   |   |-- metrics.py          # Evaluation metric utilities
|   |   |-- feature_importance.py  # Feature importance extraction
|   |
|   |-- backtest/               # Backtesting utilities
|   |-- utils/                  # General utility functions
|   |-- tests/                  # Unit and integration tests
|
|-- frontend/
|   |-- index.html
|   |-- package.json
|   |-- vite.config.ts
|   |-- tailwind.config.js
|   |-- src/
|       |-- App.tsx             # Root component and routing
|       |-- main.tsx            # Application entry point
|       |-- pages/
|       |   |-- Dashboard.tsx       # Main analysis dashboard
|       |   |-- ModelComparison.tsx # Multi-model comparison view
|       |
|       |-- components/
|       |   |-- Layout.tsx          # Application shell and navigation
|       |   |-- StockSearch.tsx     # Ticker search with market filter
|       |   |-- PriceChart.tsx      # Candlestick / line chart
|       |   |-- MarketSummary.tsx   # Global index summary cards
|       |   |-- IndicesCharts.tsx   # Historical index charts
|       |   |-- StockOverview.tsx   # Fundamentals panel
|       |   |-- PredictionCard.tsx  # ML prediction result display
|       |   |-- TechnicalIndicators.tsx  # RSI, MACD, SMA, BB panel
|       |   |-- Watchlist.tsx       # Saved tickers list
|       |   |-- ModelComparisonChart.tsx # Metric bar charts
|       |   |-- ProbabilityChart.tsx # Prediction probability gauge
|       |   |-- ThemeToggle.tsx     # Dark/light mode switch
|       |   |-- ...                 # Additional utility components
|       |
|       |-- services/           # Axios API client functions
|       |-- store/              # Zustand state stores
|       |-- types/              # TypeScript type definitions
|       |-- utils/              # Frontend utility functions
|       |-- config/             # Frontend configuration (API base URL etc.)
|
|-- models/                     # Trained model artifacts (.pkl files)
|-- data/                       # Raw and cached market data
|-- outputs/                    # Prediction result JSON files
|-- logs/                       # Application log files
|-- model_artifacts/            # Additional model metadata
```

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher and npm
- An AlphaVantage API key (optional; market data is primarily sourced from Yahoo Finance via yfinance)

### Backend Setup

**1. Create and activate a virtual environment**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:
```bash
python -m venv venv
source venv/bin/activate
```

**2. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

Copy or edit the `.env` file in the project root. Key variables are described in the [Environment Variables](#environment-variables) section below.

**4. Start the backend server**

```bash
python app.py
```

The API will be available at:
- Base URL: `http://localhost:8000`
- Interactive docs (Swagger UI): `http://localhost:8000/docs`
- Alternative docs (ReDoc): `http://localhost:8000/redoc`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Environment Variables

The following variables are read from the `.env` file in the project root:

| Variable | Default | Description |
|---|---|---|
| `API_HOST` | `0.0.0.0` | Host address for the API server |
| `API_PORT` | `8000` | Port for the API server |
| `DEBUG` | `False` | Enable debug mode and auto-reload |
| `SECRET_KEY` | — | Secret key; must be changed in production |
| `ENVIRONMENT` | `development` | Runtime environment label |
| `CORS_ORIGINS` | `[*]` | Allowed frontend origins as JSON array or comma-separated list |
| `CORS_ALLOW_ORIGIN_REGEX` | — | Optional regex for dynamic origins (for example Vercel preview URLs) |
| `CORS_ALLOW_CREDENTIALS` | `False` | Keep `False` unless browser cookies/auth headers are required |
| `MODEL_DIR` | `models` | Directory for saved model artifacts |
| `DATA_DIR` | `data/raw` | Directory for raw data files |
| `OUTPUT_DIR` | `outputs` | Directory for prediction output JSON files |
| `LOG_DIR` | `logs` | Directory for log files |
| `LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DEFAULT_PERIOD` | `5y` | Default historical data period for training |
| `TEST_SIZE` | `0.2` | Fraction of data used for model evaluation |
| `MIN_TRAINING_SAMPLES` | `100` | Minimum rows required to train a model |
| `CACHE_ENABLED` | `True` | Enable in-memory caching for stock info |
| `CACHE_TTL` | `3600` | Cache time-to-live in seconds |
| `NEWS_PROVIDER` | `gnews` | News provider (`gnews` or `newsapi`) |
| `GNEWS_API_KEY` | — | API key for GNews |
| `NEWSAPI_API_KEY` | — | API key for NewsAPI |
| `NEWS_CACHE_TTL` | `900` | News response cache TTL in seconds |
| `HIGH_CONFIDENCE_THRESHOLD` | `0.30` | Minimum confidence for the Quant Discovery filter |
| `HIGH_CONFIDENCE_MIN_AUC` | `0.50` | Minimum model AUC for the Quant Discovery filter |
| `HIGH_CONFIDENCE_DEFAULT_LIMIT` | `10` | Default number of dashboard rows returned |
| `HIGH_CONFIDENCE_CACHE_TTL` | `1800` | Cache TTL (seconds) for dashboard prediction snapshots |
| `HIGH_CONFIDENCE_OUTPUT_MAX_AGE_HOURS` | `24` | Max age of `outputs/*.json` snapshots before refresh |
| `HIGH_CONFIDENCE_SNAPSHOT_TTL` | `300` | Cache TTL (seconds) for full dashboard response snapshots |
| `HIGH_CONFIDENCE_MAX_WORKERS` | `4` | Worker threads for batched prediction refresh |
| `HIGH_CONFIDENCE_NEWS_MAX_WORKERS` | `4` | Worker threads for parallel dashboard news enrichment |
| `HIGH_CONFIDENCE_LIVE_FALLBACK` | `False` | When `False`, non-refresh requests avoid slow live retraining fallback |
| `DATABASE_URL` | — | Optional PostgreSQL connection string (future use) |
| `REDIS_URL` | — | Optional Redis connection URL (future use) |

Frontend environment variables (`frontend/.env` or Vercel project settings):

| Variable | Example | Description |
|---|---|---|
| `VITE_API_URL` | `https://stockmarketanalyzer-production-e498.up.railway.app` | Base URL used by the frontend for all API requests |

---

## API Reference

### Health

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API welcome message and status |
| `GET` | `/api/health` | Detailed health check with uptime and model count |

### Predictions

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/predict` | Run inference pipeline and return next-day direction prediction |
| `POST` | `/api/predict-with-version` | Predict using a specific registered model version |

**POST /api/predict** — Request body:
```json
{
  "ticker": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01"
}
```

Response includes: `ticker`, `prediction` (UP/DOWN), `probability_up`, `probability_down`, `confidence`, `confidence_percent`, `model_auc`, `latest_close`, `currency`, `interpretation`.

### Model Training and Registry

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/train-model` | Train a single model type for a ticker |
| `POST` | `/api/compare-models` | Train and compare all model types for a ticker |
| `GET` | `/api/models` | List all trained models across all tickers |
| `GET` | `/api/best-model/{ticker}` | Retrieve the best model for a ticker by a given metric |
| `GET` | `/api/model-versions/{ticker}` | List all versioned models for a ticker |
| `DELETE` | `/api/model-versions/{version_id}` | Delete a specific model version |

**POST /api/train-model** — Query parameters:
- `ticker` (required): Stock symbol
- `model_type` (default: `logistic`): One of `logistic`, `random_forest`, `xgboost`, `gradient_boosting`
- `tune` (default: `false`): Whether to apply hyperparameter tuning

**GET /api/best-model/{ticker}** — Query parameter:
- `metric` (default: `auc`): One of `auc`, `accuracy`, `f1_score`, `precision`, `recall`

### Market Data

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/market/indices` | Live snapshot of all major market indices |
| `GET` | `/api/market/historical-prices/{ticker}` | Historical OHLCV data with moving averages |
| `GET` | `/api/market/index-historical/{market}` | Historical chart data for a supported index |
| `GET` | `/api/market/stock-info/{ticker}` | Stock fundamentals and quote details |
| `GET` | `/api/market/technical-indicators/{ticker}` | RSI, MACD, SMA, and Bollinger Band values with signals |
| `GET` | `/api/market/search` | Search for stocks by symbol or company name |

**GET /api/market/historical-prices/{ticker}** — Query parameter:
- `period`: `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`, `all` (default: `1m`)

**GET /api/market/index-historical/{market}** — Path parameter:
- `market`: `nasdaq`, `dowjones`, `nifty50`, `sensex` (aliases: `nse`, `bse`)

Query parameter:
- `period`: `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`, `all` (default: `1m`)

Example:
```bash
curl "http://localhost:8000/api/market/index-historical/dowjones?period=6m"
```

**GET /api/market/search** — Query parameters:
- `q` (required): Ticker symbol or company name
- `market` (default: `ALL`): `ALL`, `US`, or `INDIA`
- `limit` (default: `8`, max: `20`): Maximum number of results

### News

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/news/latest` | Latest market headlines with market filter |
| `GET` | `/api/news/trending` | Trending headlines plus ticker mention counts |
| `GET` | `/api/news/stock/{ticker}` | Latest news for a specific ticker |

**GET /api/news/latest** — Query parameters:
- `market` (default: `ALL`): `ALL`, `US`, or `INDIA`
- `limit` (default: `10`, max: `30`): Maximum number of articles

**GET /api/news/trending** — Query parameters:
- `market` (default: `ALL`): `ALL`, `US`, or `INDIA`
- `limit` (default: `10`, max: `20`): Maximum number of returned articles and trending ticker rows

**GET /api/news/stock/{ticker}** — Query parameters:
- `limit` (default: `10`, max: `20`): Maximum number of ticker-specific articles

### Quant Discovery

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/dashboard/high-confidence` | Ranked list of Quant Discovery prediction signals |
| `POST` | `/api/dashboard/high-confidence/refresh` | Force-refresh Quant Discovery snapshot cache in batched mode |

**GET /api/dashboard/high-confidence** — Query parameters:
- `market` (default: `ALL`): `ALL`, `US`, or `INDIA`
- `limit` (default: `10`, max: `20`): Maximum rows returned
- `watchlist` (optional): Comma-separated ticker symbols to merge with default universe
- `include_news` (default: `false`): Include top 2 related articles per stock
- `refresh` (default: `false`): Force fresh predictions and bypass cache
- `confidence_threshold` (optional): Override confidence threshold in range [0, 1]
- `min_auc` (optional): Override model AUC threshold in range [0, 1]

**POST /api/dashboard/high-confidence/refresh** — Query parameters:
- Same parameters as `GET /api/dashboard/high-confidence`, excluding `refresh`
- Always performs batched refresh and updates snapshot cache

---

## Machine Learning Pipeline

The inference pipeline (`src/pipelines/inference_pipeline.py`) executes the following steps in sequence:

1. **Data Fetch** — Retrieves historical OHLCV data via yfinance for the specified ticker and date range.
2. **Indicator Calculation** — Computes SMA, EMA, RSI, MACD, and Bollinger Bands using the `ta` library.
3. **Feature Engineering** — Derives additional ML features: price returns, rolling volatility, and trend indicators.
4. **Target Variable** — Labels each trading day as `1` (Close next day > Close today) or `0` otherwise.
5. **Data Cleaning** — Drops rows with NaN values introduced by rolling calculations.
6. **Model Training** — Trains a Logistic Regression classifier and saves the model and scaler to `models/`.
7. **Prediction** — Applies the trained model to the most recent data point to produce a probability estimate for price going UP.

The multi-model training path (`ModelService`) follows the same data preparation steps and evaluates all four model types (Logistic Regression, Random Forest, Gradient Boosting, XGBoost) with identical train/test splits.

Evaluation metrics reported per model: accuracy, precision, recall, F1 score, AUC-ROC, and confusion matrix values (TP, TN, FP, FN).

---

## Supported Markets and Tickers

**US Equities** — Any valid Yahoo Finance symbol (e.g., `AAPL`, `MSFT`, `NVDA`, `TSLA`, `GOOGL`).

**Indian Equities** — NSE-listed stocks use the `.NS` suffix and BSE-listed stocks use the `.BO` suffix (e.g., `RELIANCE.NS`, `TCS.NS`, `SBIN.NS`, `ICICIBANK.NS`, `ADANIPOWER.NS`).

**Market Indices**

| Key | Index | Symbol |
|---|---|---|
| `nasdaq` | NASDAQ Composite | `^IXIC` |
| `dowjones` | Dow Jones Industrial Average | `^DJI` |
| `nifty50` / `nse` | NIFTY 50 | `^NSEI` |
| `sensex` / `bse` | BSE SENSEX | `^BSESN` |

Currency is inferred automatically: tickers ending in `.NS` or `.BO` are treated as INR; all others as USD.

---

## Running Tests

**Setup verification** — Runs smoke tests for imports, file structure, data fetching, inference pipeline, and FastAPI app initialization:

```bash
python test_setup.py
```

**Unit and integration tests** — Requires pytest:

```bash
pytest src/tests/ -v
```

To generate a coverage report:

```bash
pytest src/tests/ --cov=src --cov-report=html
```

---

## Notes

- Market data is sourced from Yahoo Finance via the yfinance library and is subject to Yahoo Finance availability and rate limits.
- Some technical indicators require a minimum number of historical data points to produce valid values (for example, SMA-50 requires at least 50 trading days of history).
- The first prediction request for a ticker may be slower because the full data pipeline and model training are executed from scratch.
- Model artifacts are persisted as `.pkl` files under the `models/` directory. These files are excluded from version control via `.gitignore`.
- Redis, Celery, SQLAlchemy, and MLflow are listed in `requirements.txt` as dependencies intended for future functionality (caching, background task queues, persistent storage, and experiment tracking, respectively).

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
