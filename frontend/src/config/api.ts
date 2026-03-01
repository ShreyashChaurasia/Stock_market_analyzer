export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  health: '/api/health',
  predict: '/api/predict',
  trainModel: '/api/train-model',
  compareModels: '/api/compare-models',
  modelVersions: (ticker: string) => `/api/model-versions/${ticker}`,
  bestModel: (ticker: string) => `/api/best-model/${ticker}`,
  allModels: '/api/models',
};