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
    <div className="glass-panel p-6 relative">
      {/* Subtle top glow based on prediction */}
      <div className={`absolute top-0 left-0 w-full h-1 ${isUp ? 'bg-financial-green' : 'bg-financial-red'}`} />
      <div className="flex items-center justify-between mb-6 mt-2">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">{prediction.ticker}</h2>
        <div className={`flex items-center space-x-2 px-4 py-2 rounded-full border ${
          isUp 
            ? 'bg-financial-green/10 border-financial-green/20' 
            : 'bg-financial-red/10 border-financial-red/20'
        }`}>
          {isUp ? (
            <TrendingUp className="h-5 w-5 text-financial-green" />
          ) : (
            <TrendingDown className="h-5 w-5 text-financial-red" />
          )}
          <span className={`text-lg font-bold uppercase tracking-wider ${
            isUp ? 'text-financial-green text-glow-green' : 'text-financial-red text-glow-red'
          }`}>
            {prediction.prediction}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wider">Current Price</p>
          <p className="text-3xl font-mono font-bold text-gray-900 dark:text-white tracking-tight">
            {formatCurrency(prediction.latest_close, currency)}
          </p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wider">Probability Up</p>
          <p className="text-3xl font-mono font-bold text-brand-accent tracking-tight">
            {(prediction.probability_up * 100).toFixed(1)}%
          </p>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <span className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Confidence</span>
          <span className="text-sm font-mono font-medium text-gray-900 dark:text-white">{confidencePercent}%</span>
        </div>
        <div className="w-full bg-gray-100 dark:bg-gray-800 rounded-full h-2 overflow-hidden border border-gray-200 dark:border-gray-700">
          <div
            className={`h-full rounded-full transition-all duration-1000 ease-out ${
              isUp ? 'bg-financial-green' : 'bg-financial-red'
            }`}
            style={{ width: `${confidencePercent}%` }}
          />
        </div>

        <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 mt-6 font-mono">
          <Activity className="h-4 w-4 text-brand-accent" />
          <span>Model AUC: <span className="text-gray-900 dark:text-white font-medium">{prediction.model_auc.toFixed(4)}</span></span>
        </div>

        <div className="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 font-mono">
          <Calendar className="h-4 w-4 text-brand-accent" />
          <span>Data points: <span className="text-gray-900 dark:text-white font-medium">{prediction.data_points_used}</span></span>
        </div>
      </div>

      <div className="mt-8 p-5 bg-gray-50 dark:bg-brand-surfaceHover rounded-xl border border-gray-100 dark:border-gray-800">
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
          <span className="font-semibold text-gray-900 dark:text-white block mb-1 uppercase tracking-wider text-xs">Interpretation</span> 
          {prediction.interpretation}
        </p>
      </div>
    </div>
  );
};
