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