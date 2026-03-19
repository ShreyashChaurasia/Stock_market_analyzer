import React from 'react';
import { TrendingUp, TrendingDown, Activity, Calendar } from 'lucide-react';
import type { PredictionResponse } from '../types/stock';
import { formatCurrency } from '../utils/market';

interface PredictionCardProps {
  prediction: PredictionResponse;
  currency: string;
}

export const PredictionCard: React.FC<PredictionCardProps> = ({ prediction, currency }) => {
  const isUp = prediction.prediction === 'UP';
  const confidencePercent = (prediction.confidence * 100).toFixed(1);

  return (
    <div className="glass-panel relative p-4">
      <div className={`absolute left-0 top-0 h-1 w-full ${isUp ? 'bg-financial-green' : 'bg-financial-red'}`} />
      <div className="mb-4 mt-1 flex items-center justify-between">
        <h2 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">{prediction.ticker}</h2>
        <div className={`flex items-center space-x-1.5 rounded-full border px-3 py-1.5 ${
          isUp 
            ? 'bg-financial-green/10 border-financial-green/20' 
            : 'bg-financial-red/10 border-financial-red/20'
        }`}>
          {isUp ? (
            <TrendingUp className="h-4 w-4 text-financial-green" />
          ) : (
            <TrendingDown className="h-4 w-4 text-financial-red" />
          )}
          <span className={`text-sm font-semibold uppercase tracking-[0.1em] ${
            isUp ? 'text-financial-green' : 'text-financial-red'
          }`}>
            {prediction.prediction}
          </span>
        </div>
      </div>

      <div className="mb-5 grid grid-cols-2 gap-3">
        <div>
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">Current Price</p>
          <p className="text-xl font-semibold tracking-tight text-gray-900 dark:text-white">
            {formatCurrency(prediction.latest_close, currency)}
          </p>
        </div>
        <div>
          <p className="mb-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">Probability Up</p>
          <p className="text-xl font-semibold tracking-tight text-brand-accent">
            {(prediction.probability_up * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-xs font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">Confidence</span>
          <span className="text-xs font-medium text-gray-900 dark:text-white">{confidencePercent}%</span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full border border-gray-200 bg-gray-100 dark:border-gray-700 dark:bg-gray-800">
          <div
            className={`h-full rounded-full transition-all duration-1000 ease-out ${
              isUp ? 'bg-financial-green' : 'bg-financial-red'
            }`}
            style={{ width: `${confidencePercent}%` }}
          />
        </div>

        <div className="mt-4 flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
          <Activity className="h-3.5 w-3.5 text-brand-accent" />
          <span>Model AUC: <span className="font-medium text-gray-900 dark:text-white">{prediction.model_auc.toFixed(4)}</span></span>
        </div>

        <div className="flex items-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
          <Calendar className="h-3.5 w-3.5 text-brand-accent" />
          <span>Data points: <span className="font-medium text-gray-900 dark:text-white">{prediction.data_points_used}</span></span>
        </div>
      </div>

      <div className="mt-5 rounded-md border border-gray-200 bg-gray-50 p-3.5 dark:border-gray-800 dark:bg-brand-surfaceHover">
        <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
          <span className="mb-1 block text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-900 dark:text-white">Interpretation</span> 
          {prediction.interpretation}
        </p>
      </div>
    </div>
  );
};
