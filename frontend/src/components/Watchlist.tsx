import React from 'react';
import { Star, Trash2, TrendingUp, TrendingDown } from 'lucide-react';
import { useWatchlistStore } from '../store/watchlistStore';
import { formatCurrency, inferCurrencyFromTicker } from '../utils/market';

interface WatchlistProps {
  onSelectStock: (ticker: string) => void;
}

export const Watchlist: React.FC<WatchlistProps> = ({ onSelectStock }) => {
  const { watchlist, removeFromWatchlist } = useWatchlistStore();

  if (watchlist.length === 0) {
    return (
      <div className="glass-panel p-4 text-center">
        <div className="mb-2.5 flex items-center justify-center space-x-2">
          <Star className="h-4 w-4 text-yellow-500" />
          <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-gray-900 dark:text-white">
            Watchlist
          </h3>
        </div>
        <p className="py-4 text-sm text-gray-500 dark:text-gray-400">
          No stocks in your watchlist yet. Add stocks to track them here.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-4">
      <div className="mb-3 flex items-center space-x-2">
        <Star className="h-4 w-4 text-yellow-500" />
        <h3 className="text-sm font-semibold uppercase tracking-[0.12em] text-gray-900 dark:text-white">
          Watchlist <span className="text-brand-accent ml-1">({watchlist.length})</span>
        </h3>
      </div>
      <div className="space-y-2">
        {watchlist.map((item) => (
          <div
            key={item.ticker}
            className="group flex items-center justify-between rounded-md border border-gray-200 bg-gray-50 p-3 transition-colors hover:border-brand-accent/50 dark:border-gray-800 dark:bg-brand-surfaceHover dark:hover:border-brand-accent/50"
          >
            <button
              onClick={() => onSelectStock(item.ticker)}
              className="flex-1 text-left"
            >
              <div className="flex items-center space-x-3">
                <span className="text-base font-semibold tracking-tight text-gray-900 dark:text-white">
                  {item.ticker}
                </span>
                {item.prediction && (
                  <span
                    className={`flex items-center space-x-1 text-xs font-semibold ${
                      item.prediction === 'UP'
                        ? 'text-financial-green'
                        : 'text-financial-red'
                    }`}
                  >
                    {item.prediction === 'UP' ? (
                      <TrendingUp className="h-3.5 w-3.5" />
                    ) : (
                      <TrendingDown className="h-3.5 w-3.5" />
                    )}
                    <span className="uppercase tracking-[0.08em]">{item.prediction}</span>
                  </span>
                )}
              </div>
              {item.latestPrice !== undefined && (
                <div className="mt-0.5 flex flex-wrap items-center gap-2.5">
                  <p className="text-xs text-gray-500 dark:text-gray-400 sm:text-sm">
                    {formatCurrency(item.latestPrice, item.currency ?? inferCurrencyFromTicker(item.ticker))}
                  </p>
                  {item.change !== undefined && item.changePercent !== undefined && (
                    <p className={`text-xs font-semibold ${item.change >= 0 ? 'text-financial-green' : 'text-financial-red'}`}>
                      {item.change >= 0 ? '+' : ''}
                      {item.change.toFixed(2)} ({item.change >= 0 ? '+' : ''}
                      {item.changePercent.toFixed(2)}%)
                    </p>
                  )}
                </div>
              )}
            </button>
            <button
              onClick={() => removeFromWatchlist(item.ticker)}
              className="rounded-md p-1.5 text-gray-400 opacity-0 transition-all hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-900/20 dark:hover:text-red-400 group-hover:opacity-100"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
