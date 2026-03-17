# Stock Market Analyzer

Full-stack stock analysis platform with machine-learning predictions, technical indicators, and interactive market dashboards.

## What It Does

- Predicts next-day direction (`UP` / `DOWN`) with model confidence
- Trains and compares multiple ML models per ticker
- Visualizes stock history with candlestick/line charts and moving averages
- Shows live global indices with click-to-view historical charts for:
  - NASDAQ, Dow Jones
  - NSE (`NIFTY 50`), BSE (`SENSEX`)
- Provides technical indicators (RSI, MACD, SMA, Bollinger Bands)

## Tech Stack

- Backend: FastAPI, scikit-learn, XGBoost, yfinance, pandas
- Frontend: React 19, TypeScript, Vite, Tailwind CSS
- Charts: lightweight-charts, Recharts
- State/Data: Zustand, TanStack Query

## Project Structure

```text
Stock_market_analyzer/
├── app.py
├── src/
│   ├── core/
│   ├── models/
│   ├── pipelines/
│   ├── services/
│   ├── registry/
│   ├── schemas/
│   └── middleware/
├── frontend/
├── configs/
├── data/
├── models/
└── outputs/
```

## Backend Setup

### 1) Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

This repo includes a `.env` file. Update it for your environment (host/port, logging, model dirs, etc.) before running in production.

### 4) Run backend

```bash
python app.py
```

API base URL: `http://localhost:8000`  
Docs: `http://localhost:8000/docs`

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

## Main API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health |
| `POST` | `/api/predict` | Predict stock movement |
| `POST` | `/api/train-model` | Train one model for a ticker |
| `POST` | `/api/compare-models` | Train and compare all models |
| `GET` | `/api/models` | List all trained models |
| `GET` | `/api/best-model/{ticker}` | Best model by metric |
| `GET` | `/api/model-versions/{ticker}` | Model versions for a ticker |
| `GET` | `/api/market/indices` | Live market indices snapshot |
| `GET` | `/api/market/historical-prices/{ticker}` | Historical OHLC + MAs for stocks |
| `GET` | `/api/market/index-historical/{market}` | Historical index data for supported index keys |
| `GET` | `/api/market/stock-info/{ticker}` | Stock fundamentals and quote details |
| `GET` | `/api/market/technical-indicators/{ticker}` | RSI, MACD, SMA, Bollinger Bands |

### Index Historical Endpoint

`GET /api/market/index-historical/{market}?period=1m`

- `market`: `nasdaq`, `dowjones`, `nifty50`, `sensex`
- aliases: `nse` (for `nifty50`) and `bse` (for `sensex`)
- `period`: `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`, `all`
- `period`: `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, `5y`

Example:

```bash
curl "http://localhost:8000/api/market/index-historical/dowjones?period=6m"
```

## Notes

- Data comes from Yahoo Finance and may vary by market hours.
- Some indicators require enough history to populate (for example SMA windows).
- First request for a ticker can be slower because model/data pipelines need to initialize.

## License

MIT License. See [LICENSE](LICENSE).
