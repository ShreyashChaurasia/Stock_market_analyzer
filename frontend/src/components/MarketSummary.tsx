import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Globe, Clock, TrendingUp, TrendingDown } from 'lucide-react';
import { stockApi } from '../services/api';
import type { MarketIndices } from '../types/stock';

export const MarketSummary: React.FC = () => {
  const { data, isLoading } = useQuery<{ data: MarketIndices }>({
    queryKey: ['market-indices'],
    queryFn: stockApi.getMarketIndices,
    refetchInterval: 60000, // Refresh every minute
    staleTime: 30000, // Consider data stale after 30 seconds
  });

  const IndexCard = ({ name, marketData }: { name: string; marketData: any }) => {
    if (!marketData) return null;

    const isPositive = marketData.change >= 0;

    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{name}</p>
        <p className="text-xl font-bold text-gray-900 dark:text-white mt-1">
          {marketData.current_price.toLocaleString()}
        </p>
        <div className={`flex items-center space-x-1 mt-1 ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
          {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
          <span className="text-sm font-medium">
            {isPositive ? '+' : ''}{marketData.change.toFixed(2)}
          </span>
          <span className="text-sm">
            ({isPositive ? '+' : ''}{marketData.change_percent.toFixed(2)}%)
          </span>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-lg shadow-lg p-6 text-white">
        <div className="flex items-center space-x-2 mb-4">
          <Globe className="h-6 w-6 animate-pulse" />
          <h3 className="text-xl font-bold">Loading Market Data...</h3>
        </div>
      </div>
    );
  }

  if (!data?.data) return null;

  const marketData = data.data;

  return (
    <div className="bg-gradient-to-r from-primary-600 to-primary-800 rounded-lg shadow-lg p-6 text-white">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Globe className="h-6 w-6" />
          <h3 className="text-xl font-bold">Live Market Overview</h3>
        </div>
        <div className="flex items-center space-x-1 text-sm bg-white/20 px-3 py-1 rounded-full">
          <Clock className="h-4 w-4" />
          <span>Real-time</span>
        </div>
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <IndexCard name="S&P 500" marketData={marketData.sp500} />
        <IndexCard name="NASDAQ" marketData={marketData.nasdaq} />
        <IndexCard name="Dow Jones" marketData={marketData.dowjones} />
        <IndexCard name="NIFTY 50" marketData={marketData.nifty50} />
      </div>
    </div>
  );
};