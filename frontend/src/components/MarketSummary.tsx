import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Globe, Clock, TrendingUp, TrendingDown } from 'lucide-react';
import { stockApi } from '../services/api';
import type { MarketIndex, MarketIndices, MarketIndexKey } from '../types/stock';
import { INDEX_CONFIG } from '../config/indices';

interface IndexCardProps {
  name: string;
  marketData?: MarketIndex;
  isSelected: boolean;
  onClick?: () => void;
}

const IndexCard: React.FC<IndexCardProps> = ({ name, marketData, isSelected, onClick }) => {
  const isPositive = (marketData?.change ?? 0) >= 0;

  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-lg border p-4 text-left transition-colors ${
        isSelected
          ? 'border-brand-accent ring-1 ring-brand-accent/30 bg-white dark:bg-brand-dark/60'
          : 'border-gray-200 bg-white hover:border-gray-300 dark:border-gray-800 dark:bg-brand-dark/50 dark:hover:border-gray-700'
      }`}
    >
      <p className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">{name}</p>
      <p className="text-xl font-mono font-bold text-gray-900 dark:text-white mt-1">
        {marketData
          ? marketData.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
          : '--'}
      </p>
      {marketData ? (
        <div className={`flex items-center space-x-1 mt-2 text-sm font-mono ${isPositive ? 'text-financial-green' : 'text-financial-red'}`}>
          {isPositive ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
          <span className="font-medium">
            {isPositive ? '+' : ''}{marketData.change.toFixed(2)}
          </span>
          <span>
            ({isPositive ? '+' : ''}{marketData.change_percent.toFixed(2)}%)
          </span>
        </div>
      ) : (
        <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">Data temporarily unavailable</p>
      )}
    </button>
  );
};

interface MarketSummaryProps {
  selectedIndex: MarketIndexKey | null;
  onSelectIndex: (indexKey: MarketIndexKey) => void;
}

export const MarketSummary: React.FC<MarketSummaryProps> = ({ selectedIndex, onSelectIndex }) => {
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
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4 2xl:grid-cols-7">
        {INDEX_CONFIG.map((indexItem) => (
          <IndexCard
            key={indexItem.key}
            name={indexItem.label}
            marketData={marketData[indexItem.key]}
            isSelected={selectedIndex === indexItem.key}
            onClick={() => onSelectIndex(indexItem.key)}
          />
        ))}
      </div>
    </div>
  );
};
