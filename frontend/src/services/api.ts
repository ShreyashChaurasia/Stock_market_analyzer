import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';
import type {
  PredictionRequest,
  PredictionResponse,
  ModelVersion,
  HealthResponse,
  MarketIndices,
  StockInfo,
  StockSuggestion,
  TechnicalIndicators,
  HistoricalPricesResponse,
  IndexHistoricalResponse,
  MarketIndexKey,
} from '../types/stock';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const stockApi = {
  getHealth: async (): Promise<HealthResponse> => {
    const response = await api.get(API_ENDPOINTS.health);
    return response.data;
  },

  getPrediction: async (request: PredictionRequest): Promise<PredictionResponse> => {
    const response = await api.post(API_ENDPOINTS.predict, request);
    return response.data;
  },

  trainModel: async (ticker: string, modelType: string, tune: boolean = false) => {
    const response = await api.post(
      `${API_ENDPOINTS.trainModel}?ticker=${ticker}&model_type=${modelType}&tune=${tune}`
    );
    return response.data;
  },

  compareModels: async (ticker: string) => {
    const response = await api.post(`${API_ENDPOINTS.compareModels}?ticker=${ticker}`);
    return response.data;
  },

  getModelVersions: async (ticker: string): Promise<{ models: ModelVersion[] }> => {
    const response = await api.get(API_ENDPOINTS.modelVersions(ticker));
    return response.data;
  },

  getBestModel: async (ticker: string, metric: string = 'auc') => {
    const response = await api.get(`${API_ENDPOINTS.bestModel(ticker)}?metric=${metric}`);
    return response.data;
  },

  getAllModels: async () => {
    const response = await api.get(API_ENDPOINTS.allModels);
    return response.data;
  },
  getMarketIndices: async (): Promise<{ data: MarketIndices }> => {
    const response = await api.get(API_ENDPOINTS.marketIndices);
    return response.data;
  },

  getStockInfo: async (ticker: string): Promise<{ data: StockInfo }> => {
    const response = await api.get(API_ENDPOINTS.stockInfo(ticker));
    return response.data;
  },

  searchSymbols: async (
    query: string,
    market: 'US' | 'INDIA' | 'ALL' = 'ALL',
    limit: number = 8
  ): Promise<{ results: StockSuggestion[] }> => {
    const response = await api.get(API_ENDPOINTS.searchSymbols(query, market, limit));
    return response.data;
  },

  getTechnicalIndicators: async (ticker: string): Promise<{ data: TechnicalIndicators }> => {
    const response = await api.get(API_ENDPOINTS.technicalIndicators(ticker));
    return response.data;
  },

  getHistoricalPrices: async (ticker: string, period: string = '1m'): Promise<HistoricalPricesResponse> => {
    const response = await api.get(API_ENDPOINTS.historicalPrices(ticker, period));
    return response.data;
  },

  getIndexHistorical: async (
    market: MarketIndexKey | 'nse' | 'bse',
    period: string = '1m'
  ): Promise<IndexHistoricalResponse> => {
    const response = await api.get(API_ENDPOINTS.indexHistorical(market, period));
    return response.data;
  },
};
