import React from 'react';
import { Star, Trash2, TrendingUp, TrendingDown } from 'lucide-react';
import { useWatchlistStore } from '../store/watchlistStore';

interface WatchlistProps {
  onSelectStock: (ticker: string) => void;
}

export const Watchlist: React.FC<WatchlistProps> = ({ onSelectStock }) => {
  const { watchlist, removeFromWatchlist } = useWatchlistStore();

  if (watchlist.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Star className="h-5 w-5 text-yellow-500" />
          <h3 className="text-xl font-bold text-gray-900 dark:text-white">
            Watchlist
          </h3>
        </div>
        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
          No stocks in your watchlist yet. Add stocks to track them here.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-2 mb-4">
        <Star className="h-5 w-5 text-yellow-500" />
        <h3 className="text-xl font-bold text-gray-900 dark:text-white">
          Watchlist ({watchlist.length})
        </h3>
      </div>
      <div className="space-y-3">
        {watchlist.map((item) => (
          <div
            key={item.ticker}
            className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <button
              onClick={() => onSelectStock(item.ticker)}
              className="flex-1 text-left"
            >
              <div className="flex items-center space-x-3">
                <span className="text-lg font-bold text-gray-900 dark:text-white">
                  {item.ticker}
                </span>
                {item.prediction && (
                  <span
                    className={`flex items-center space-x-1 text-sm font-medium ${
                      item.prediction === 'UP'
                        ? 'text-green-600'
                        : 'text-red-600'
                    }`}
                  >
                    {item.prediction === 'UP' ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : (
                      <TrendingDown className="h-4 w-4" />
                    )}
                    <span>{item.prediction}</span>
                  </span>
                )}
              </div>
              {item.latestPrice && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                  ${item.latestPrice.toFixed(2)}
                </p>
              )}
            </button>
            <button
              onClick={() => removeFromWatchlist(item.ticker)}
              className="p-2 text-gray-400 hover:text-red-600 transition-colors"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};