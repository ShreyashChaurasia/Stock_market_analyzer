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
      <div className="glass-panel p-6 text-center">
        <div className="flex items-center justify-center space-x-2 mb-4">
          <Star className="h-5 w-5 text-yellow-500" />
          <h3 className="text-lg font-bold text-gray-900 dark:text-white uppercase tracking-wider">
            Watchlist
          </h3>
        </div>
        <p className="text-sm font-medium text-gray-500 dark:text-gray-400 py-6">
          No stocks in your watchlist yet. Add stocks to track them here.
        </p>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6">
      <div className="flex items-center space-x-2 mb-5">
        <Star className="h-5 w-5 text-yellow-500" />
        <h3 className="text-lg font-bold text-gray-900 dark:text-white tracking-wider uppercase">
          Watchlist <span className="text-brand-accent ml-1">({watchlist.length})</span>
        </h3>
      </div>
      <div className="space-y-3">
        {watchlist.map((item) => (
          <div
            key={item.ticker}
            className="flex items-center justify-between p-4 border border-gray-100 dark:border-gray-800 rounded-lg bg-gray-50 dark:bg-brand-surfaceHover hover:border-brand-accent/50 dark:hover:border-brand-accent/50 transition-all group"
          >
            <button
              onClick={() => onSelectStock(item.ticker)}
              className="flex-1 text-left"
            >
              <div className="flex items-center space-x-3">
                <span className="text-lg font-mono font-bold text-gray-900 dark:text-white tracking-tight">
                  {item.ticker}
                </span>
                {item.prediction && (
                  <span
                    className={`flex items-center space-x-1 text-sm font-medium ${
                      item.prediction === 'UP'
                        ? 'text-financial-green'
                        : 'text-financial-red'
                    }`}
                  >
                    {item.prediction === 'UP' ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : (
                      <TrendingDown className="h-4 w-4" />
                    )}
                    <span className="uppercase tracking-wider">{item.prediction}</span>
                  </span>
                )}
              </div>
              {item.latestPrice && (
                <p className="text-sm font-mono text-gray-500 dark:text-gray-400 mt-1">
                  {formatCurrency(item.latestPrice, item.currency ?? inferCurrencyFromTicker(item.ticker))}
                </p>
              )}
            </button>
            <button
              onClick={() => removeFromWatchlist(item.ticker)}
              className="p-2 text-gray-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all opacity-0 group-hover:opacity-100"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};
