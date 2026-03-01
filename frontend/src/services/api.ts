import axios from 'axios';
import { API_BASE_URL, API_ENDPOINTS } from '../config/api';
import type { PredictionRequest, PredictionResponse, ModelVersion, HealthResponse } from '../types/stock';

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
};