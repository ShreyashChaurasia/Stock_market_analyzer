import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Globe, Clock, TrendingUp, TrendingDown } from 'lucide-react';
import { stockApi } from '../services/api';
import type { MarketIndex, MarketIndices } from '../types/stock';

interface IndexCardProps {
  name: string;
  marketData?: MarketIndex;
}

const IndexCard: React.FC<IndexCardProps> = ({ name, marketData }) => {
  if (!marketData) return null;

  const isPositive = marketData.change >= 0;

  return (
    <div className="bg-white dark:bg-brand-dark/50 rounded-lg p-4 border border-gray-200 dark:border-gray-800 hover:border-gray-300 dark:hover:border-gray-700 transition-colors">
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{name}</p>
      <p className="text-xl font-mono font-bold text-gray-900 dark:text-white mt-1">
        {marketData.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
      </p>
      <div className={`flex items-center space-x-1 mt-2 text-sm font-mono ${isPositive ? 'text-financial-green' : 'text-financial-red'}`}>
        {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
        <span className="font-medium">
          {isPositive ? '+' : ''}{marketData.change.toFixed(2)}
        </span>
        <span>
          ({isPositive ? '+' : ''}{marketData.change_percent.toFixed(2)}%)
        </span>
      </div>
    </div>
  );
};

export const MarketSummary: React.FC = () => {
  const { data, isLoading } = useQuery<{ data: MarketIndices }>({
    queryKey: ['market-indices'],
    queryFn: stockApi.getMarketIndices,
    refetchInterval: 60000, // Refresh every minute
    staleTime: 30000, // Consider data stale after 30 seconds
  });

  if (isLoading) {
    return (
      <div className="glass-panel p-6">
        <div className="flex items-center space-x-2 mb-4 text-gray-900 dark:text-white">
          <Globe className="h-6 w-6 animate-pulse text-brand-accent" />
          <h3 className="text-lg font-bold tracking-tight">Loading Market Data...</h3>
        </div>
      </div>
    );
  }

  if (!data?.data) return null;

  const marketData = data.data;

  return (
    <div className="glass-panel p-5">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-6 gap-2">
        <div className="flex items-center space-x-2">
          <Globe className="h-5 w-5 text-gray-700 dark:text-gray-300" />
          <h3 className="text-lg font-bold text-gray-900 dark:text-white tracking-tight uppercase tracking-wider">Live Market Overview</h3>
        </div>
        <div className="flex items-center space-x-1 text-xs font-medium text-brand-accent bg-brand-accent/5 dark:bg-brand-accent/10 px-3 py-1.5 rounded-full border border-brand-accent/20 dark:border-brand-accent/20">
          <Clock className="h-3 w-3" />
          <span className="uppercase tracking-wider">Real-time</span>
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
