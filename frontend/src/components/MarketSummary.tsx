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
      className={`w-full rounded-md border p-3 text-left transition-colors ${
        isSelected
          ? 'border-brand-accent bg-blue-50/40 ring-1 ring-brand-accent/30 dark:bg-brand-dark/60'
          : 'border-gray-200 bg-white hover:border-gray-300 dark:border-gray-800 dark:bg-brand-dark/50 dark:hover:border-gray-700'
      }`}
    >
      <p className="text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">{name}</p>
      <p className="mt-1 text-base font-semibold text-gray-900 dark:text-white md:text-lg">
        {marketData
          ? marketData.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
          : '--'}
      </p>
      {marketData ? (
        <div className={`mt-1.5 flex items-center space-x-1 text-xs font-medium ${isPositive ? 'text-financial-green' : 'text-financial-red'}`}>
          {isPositive ? <TrendingUp className="h-3.5 w-3.5" /> : <TrendingDown className="h-3.5 w-3.5" />}
          <span>
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
      <div className="glass-panel p-4">
        <div className="mb-2 flex items-center space-x-2 text-gray-900 dark:text-white">
          <Globe className="h-5 w-5 animate-pulse text-brand-accent" />
          <h3 className="text-base font-semibold tracking-tight">Loading Market Data...</h3>
        </div>
      </div>
    );
  }

  if (!data?.data) return null;

  const marketData = data.data;

  return (
    <div className="glass-panel p-4">
      <div className="mb-4 flex flex-col items-start justify-between gap-2 sm:flex-row sm:items-center">
        <div className="flex items-center space-x-2">
          <Globe className="h-4 w-4 text-gray-700 dark:text-gray-300" />
          <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-gray-900 dark:text-white">Live Market Overview</h3>
        </div>
        <div className="flex items-center space-x-1 rounded-full border border-brand-accent/20 bg-brand-accent/5 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.1em] text-brand-accent dark:bg-brand-accent/10 dark:border-brand-accent/20">
          <Clock className="h-3 w-3" />
          <span>Real-time</span>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2.5 lg:grid-cols-4 2xl:grid-cols-7">
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
