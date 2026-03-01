import React from 'react';
import { TrendingUp, TrendingDown, Activity, Calendar } from 'lucide-react';
import type { PredictionResponse } from '../types/stock';

interface PredictionCardProps {
  prediction: PredictionResponse;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({ prediction }) => {
  const isUp = prediction.prediction === 'UP';
  const confidencePercent = (prediction.confidence * 100).toFixed(1);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-900">{prediction.ticker}</h2>
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-full ${
          isUp ? 'bg-green-100' : 'bg-red-100'
        }`}>
          {isUp ? (
            <TrendingUp className="h-6 w-6 text-green-600" />
          ) : (
            <TrendingDown className="h-6 w-6 text-red-600" />
          )}
          <span className={`text-lg font-bold ${
            isUp ? 'text-green-600' : 'text-red-600'
          }`}>
            {prediction.prediction}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div>
          <p className="text-sm text-gray-600 mb-1">Current Price</p>
          <p className="text-2xl font-bold text-gray-900">
            ${prediction.latest_close.toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-1">Probability Up</p>
          <p className="text-2xl font-bold text-primary-600">
            {(prediction.probability_up * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Confidence</span>
          <span className="text-sm font-medium text-gray-900">{confidencePercent}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${confidencePercent}%` }}
          />
        </div>

        <div className="flex items-center space-x-2 text-sm text-gray-600 mt-4">
          <Activity className="h-4 w-4" />
          <span>Model AUC: {prediction.model_auc.toFixed(4)}</span>
        </div>

        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <Calendar className="h-4 w-4" />
          <span>Data points: {prediction.data_points_used}</span>
        </div>
      </div>

      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-700">
          <span className="font-medium">Interpretation:</span> {prediction.interpretation}
        </p>
      </div>
    </div>
  );
};