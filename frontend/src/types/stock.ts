export interface PredictionRequest {
  ticker: string;
  start_date?: string;
  end_date?: string;
  period?: string;
}

export interface PredictionResponse {
  ticker: string;
  prediction_date: string;
  latest_data_date: string;
  latest_close: number;
  currency: string;
  probability_up: number;
  probability_down: number;
  prediction: string;
  confidence: number;
  confidence_percent: string;
  model_auc: number;
  data_points_used: number;
  interpretation: string;
}

export interface ModelVersion {
  version_id: string;
  ticker: string;
  model_name: string;
  model_type: string;
  timestamp: string;
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    auc: number;
  };
  is_trained: boolean;
  file_path: string;
  file_size_kb: number;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  version: string;
  models_available: number;
  uptime_seconds?: number;
}

export interface MarketIndex {
  symbol: string;
  current_price: number;
  change: number;
  change_percent: number;
  timestamp: string;
}

export type MarketIndexKey =
  | 'nasdaq'
  | 'dowjones'
  | 'nifty50'
  | 'sensex';

export type MarketIndices = Partial<Record<MarketIndexKey, MarketIndex>>;

export interface StockInfo {
  ticker: string;
  company_name: string;
  sector: string;
  industry: string;
  currency: string;
  exchange: string | null;
  current_price: number;
  previous_close: number | null;
  open_price: number | null;
  day_high: number | null;
  day_low: number | null;
  market_cap: number;
  enterprise_value: number | null;
  pe_ratio: number;
  dividend_yield: number;
  high_52week: number;
  low_52week: number;
  avg_volume: number;
  current_volume: number;
  shares_outstanding: number | null;
  beta: number;
  timestamp: string;
}

export interface TechnicalIndicator {
  value: number;
  signal: string;
  signal_line?: number;
}

export interface TechnicalIndicators {
  ticker: string;
  rsi: TechnicalIndicator;
  macd: TechnicalIndicator;
  sma_20: TechnicalIndicator;
  sma_50: TechnicalIndicator | null;
  bollinger_bands: {
    upper: number;
    lower: number;
    signal: string;
  };
  timestamp: string;
}

export interface HistoricalPrice {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  sma_20: number | null;
  sma_50: number | null;
  volume: number;
}

export interface HistoricalPricesResponse {
  ticker: string;
  period: string;
  interval: string;
  currency: string;
  data: HistoricalPrice[];
}

export interface IndexHistoricalResponse {
  market: MarketIndexKey | 'nse' | 'bse';
  name: string;
  symbol: string;
  period: string;
  interval: string;
  currency: string;
  data: HistoricalPrice[];
}
