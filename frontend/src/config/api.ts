export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  health: '/api/health',
  predict: '/api/predict',
  trainModel: '/api/train-model',
  compareModels: '/api/compare-models',
  modelVersions: (ticker: string) => `/api/model-versions/${ticker}`,
  bestModel: (ticker: string) => `/api/best-model/${ticker}`,
  allModels: '/api/models',
  marketIndices: '/api/market/indices',
  indexHistorical: (market: string, period: string) => `/api/market/index-historical/${market}?period=${period}`,
  stockInfo: (ticker: string) => `/api/market/stock-info/${ticker}`,
  technicalIndicators: (ticker: string) => `/api/market/technical-indicators/${ticker}`,
  historicalPrices: (ticker: string, period: string) => `/api/market/historical-prices/${ticker}?period=${period}`,
};
