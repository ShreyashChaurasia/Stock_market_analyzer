import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Activity, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { stockApi } from '../services/api';
import type { TechnicalIndicators as TechnicalIndicatorsType } from '../types/stock';
import { formatCurrency } from '../utils/market';

interface TechnicalIndicatorsProps {
  ticker: string;
  currency: string;
}

export const TechnicalIndicators: React.FC<TechnicalIndicatorsProps> = ({ ticker, currency }) => {
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
      <div className="glass-panel p-4">
        <div className="animate-pulse">
          <div className="mb-3 h-5 w-1/2 rounded bg-gray-200 dark:bg-gray-700"></div>
          <div className="space-y-2.5">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-14 rounded bg-gray-200 dark:bg-gray-700"></div>
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
      value: `${formatCurrency(indicators.bollinger_bands.lower, currency)} - ${formatCurrency(indicators.bollinger_bands.upper, currency)}`,
      signal: indicators.bollinger_bands.signal,
    },
  ];

  return (
    <div className="glass-panel p-4">
      <div className="mb-3 flex items-center space-x-2">
        <Activity className="h-4 w-4 text-primary-600" />
        <h3 className="text-base font-semibold text-gray-900 dark:text-white">
          Technical Indicators
        </h3>
      </div>
      <div className="space-y-2.5">
        {indicatorsList.map((indicator, index) => (
          <div
            key={index}
            className="flex items-center justify-between rounded-md border border-gray-200 p-2.5 dark:border-gray-700"
          >
            <div className="flex-1">
              <p className="text-xs font-semibold text-gray-900 dark:text-white sm:text-sm">
                {indicator.name}
              </p>
              <p className="text-xs text-gray-600 dark:text-gray-400 sm:text-sm">
                {typeof indicator.value === 'number' && indicator.name !== 'RSI (14)' && indicator.name !== 'MACD'
                  ? formatCurrency(indicator.value, currency)
                  : typeof indicator.value === 'number'
                    ? indicator.value.toFixed(2)
                    : indicator.value}
              </p>
            </div>
            <div className={`flex items-center space-x-1 rounded-full px-2.5 py-1 text-xs font-semibold ${getSignalColor(indicator.signal)}`}>
              {getSignalIcon(indicator.signal)}
              <span>{indicator.signal}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
