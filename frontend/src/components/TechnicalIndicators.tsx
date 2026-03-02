import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { stockApi } from '../services/api';
import type { TechnicalIndicators as TechnicalIndicatorsType } from '../types/stock';

interface TechnicalIndicatorsProps {
  ticker: string;
}

export const TechnicalIndicators: React.FC<TechnicalIndicatorsProps> = ({ ticker }) => {
  const { data, isLoading } = useQuery<{ data: TechnicalIndicatorsType }>({
    queryKey: ['technical-indicators', ticker],
    queryFn: () => stockApi.getTechnicalIndicators(ticker),
    enabled: !!ticker,
  });

  const getSignalIcon = (signal: string) => {
    if (signal === 'Buy' || signal === 'Oversold') return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (signal === 'Sell' || signal === 'Overbought') return <TrendingDown className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-gray-600" />;
  };

  const getSignalColor = (signal: string) => {
    if (signal === 'Buy' || signal === 'Oversold') return 'text-green-600 bg-green-50 dark:bg-green-900/20';
    if (signal === 'Sell' || signal === 'Overbought') return 'text-red-600 bg-red-50 dark:bg-red-900/20';
    return 'text-gray-600 bg-gray-50 dark:bg-gray-900/20';
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-16 bg-gray-200 dark:bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!data?.data) return null;

  const indicators = data.data;

  const indicatorsList = [
    {
      name: 'RSI (14)',
      value: indicators.rsi.value,
      signal: indicators.rsi.signal,
    },
    {
      name: 'MACD',
      value: indicators.macd.value,
      signal: indicators.macd.signal,
    },
    {
      name: 'SMA (20)',
      value: indicators.sma_20.value,
      signal: indicators.sma_20.signal,
    },
    ...(indicators.sma_50 ? [{
      name: 'SMA (50)',
      value: indicators.sma_50.value,
      signal: indicators.sma_50.signal,
    }] : []),
    {
      name: 'Bollinger Bands',
      value: `${indicators.bollinger_bands.lower.toFixed(2)} - ${indicators.bollinger_bands.upper.toFixed(2)}`,
      signal: indicators.bollinger_bands.signal,
    },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Activity className="h-5 w-5 text-primary-600" />
        <h3 className="text-xl font-bold text-gray-900 dark:text-white">
          Technical Indicators
        </h3>
      </div>
      <div className="space-y-3">
        {indicatorsList.map((indicator, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-3 border border-gray-200 dark:border-gray-700 rounded-lg"
          >
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {indicator.name}
              </p>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {typeof indicator.value === 'number' ? indicator.value.toFixed(2) : indicator.value}
              </p>
            </div>
            <div className={`flex items-center space-x-1 px-3 py-1 rounded-full ${getSignalColor(indicator.signal)}`}>
              {getSignalIcon(indicator.signal)}
              <span className="text-sm font-medium">{indicator.signal}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};