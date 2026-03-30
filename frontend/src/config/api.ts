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
  searchSymbols: (query: string, market: string, limit: number = 8) =>
    `/api/market/search?q=${encodeURIComponent(query)}&market=${encodeURIComponent(market)}&limit=${limit}`,
  technicalIndicators: (ticker: string) => `/api/market/technical-indicators/${ticker}`,
  historicalPrices: (ticker: string, period: string) => `/api/market/historical-prices/${ticker}?period=${period}`,
  latestNews: (market: string, limit: number = 10) =>
    `/api/news/latest?market=${encodeURIComponent(market)}&limit=${limit}`,
  trendingNews: (market: string, limit: number = 10) =>
    `/api/news/trending?market=${encodeURIComponent(market)}&limit=${limit}`,
  stockNews: (ticker: string, limit: number = 6) =>
    `/api/news/stock/${encodeURIComponent(ticker)}?limit=${limit}`,
  highConfidenceDashboard: (
    market: string,
    limit: number = 10,
    watchlist?: string,
    includeNews: boolean = false,
    confidenceThreshold?: number,
    minAuc?: number,
    refresh: boolean = false
  ) => {
    const watchlistQuery = watchlist ? `&watchlist=${encodeURIComponent(watchlist)}` : '';
    const confidenceQuery =
      confidenceThreshold !== undefined ? `&confidence_threshold=${confidenceThreshold}` : '';
    const aucQuery = minAuc !== undefined ? `&min_auc=${minAuc}` : '';
    const refreshQuery = `&refresh=${refresh}`;
    return `/api/dashboard/high-confidence?market=${encodeURIComponent(market)}&limit=${limit}&include_news=${includeNews}${watchlistQuery}${confidenceQuery}${aucQuery}${refreshQuery}`;
  },
  refreshHighConfidenceDashboard: (
    market: string,
    limit: number = 10,
    watchlist?: string,
    includeNews: boolean = false,
    confidenceThreshold?: number,
    minAuc?: number
  ) => {
    const watchlistQuery = watchlist ? `&watchlist=${encodeURIComponent(watchlist)}` : '';
    const confidenceQuery =
      confidenceThreshold !== undefined ? `&confidence_threshold=${confidenceThreshold}` : '';
    const aucQuery = minAuc !== undefined ? `&min_auc=${minAuc}` : '';
    return `/api/dashboard/high-confidence/refresh?market=${encodeURIComponent(market)}&limit=${limit}&include_news=${includeNews}${watchlistQuery}${confidenceQuery}${aucQuery}`;
  },
};
