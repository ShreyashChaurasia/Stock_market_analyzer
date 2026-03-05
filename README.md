# 📈 Stock Market Analyzer

A full-stack stock market analysis tool with ML-powered price movement predictions.

---

## Overview

- **Backend**: FastAPI REST API with multiple ML models (Logistic Regression, Random Forest, XGBoost, Gradient Boosting)
- **Frontend**: React + TypeScript dashboard with interactive charts
- **Data**: Pulled live from Yahoo Finance via `yfinance`
- **Indicators**: RSI, MACD, SMA, Bollinger Bands, and more

---

## Features

- 🔮 **Stock Price Prediction** — ML models predict the probability of a stock going UP the next trading day
- 🤖 **Model Training & Comparison** — Train and compare multiple model types per ticker
- 📊 **Technical Indicators** — Real-time RSI, MACD, Bollinger Bands with buy/sell signals
- 🌐 **Market Indices** — Live data for S&P 500, NASDAQ, Dow Jones, NIFTY 50, SENSEX
- 📁 **Model Registry** — Track, compare, and manage trained model versions

---

## Project Structure

```
Stock_market_analyzer/
├── app.py              # FastAPI app entry point
├── src/
│   ├── core/           # Data fetching, indicators, feature engineering
│   ├── models/         # ML model definitions
│   ├── pipelines/      # Training & inference pipelines
│   ├── services/       # Model & market data services
│   ├── registry/       # Model versioning & registry
│   ├── schemas/        # Pydantic request/response schemas
│   └── middleware/     # Error handling & logging
├── frontend/           # React + Vite frontend
├── model_artifacts/    # Saved trained models
└── configs/            # App configuration
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend Setup

```bash
# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/macOS

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env         # Edit as needed

# Run the API server
python app.py
```

API will be available at `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/health` | Health check |
| `POST` | `/api/predict` | Predict stock movement |
| `POST` | `/api/train-model` | Train a specific model |
| `POST` | `/api/compare-models` | Train & compare all models |
| `GET`  | `/api/models` | List all trained models |
| `GET`  | `/api/best-model/{ticker}` | Get best model for a ticker |
| `GET`  | `/api/market/indices` | Live market indices |
| `GET`  | `/api/market/stock-info/{ticker}` | Stock details & fundamentals |
| `GET`  | `/api/market/technical-indicators/{ticker}` | Technical indicators |
| `GET`  | `/api/market/historical-prices/{ticker}` | Historical price data |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI, Uvicorn, Pydantic |
| ML | scikit-learn, XGBoost |
| Data | yfinance, pandas, numpy |
| Indicators | `ta` library |
| Frontend | React 19, TypeScript, Vite, Tailwind CSS |
| Charts | Recharts |
| State | Zustand, TanStack Query |

---

## License

MIT — see [LICENSE](LICENSE)
