import React from 'react';
import { Star } from 'lucide-react';
import { useWatchlistStore } from '../store/watchlistStore';

interface WatchlistButtonProps {
  ticker: string;
  latestPrice?: number;
  prediction?: string;
  currency?: string;
  change?: number;
  changePercent?: number;
}

export const WatchlistButton: React.FC<WatchlistButtonProps> = ({
  ticker,
  latestPrice,
  prediction,
  currency,
  change,
  changePercent,
}) => {
  const { addToWatchlist, removeFromWatchlist, isInWatchlist, updateWatchlistItem } =
    useWatchlistStore();

  const inWatchlist = isInWatchlist(ticker);

  const handleToggle = () => {
    if (inWatchlist) {
      removeFromWatchlist(ticker);
    } else {
      addToWatchlist(ticker);
      if (latestPrice !== undefined || prediction || currency || change !== undefined || changePercent !== undefined) {
        updateWatchlistItem(ticker, { latestPrice, prediction, currency, change, changePercent });
      }
    }
  };

  return (
    <button
      onClick={handleToggle}
      className={`flex items-center space-x-1.5 rounded-md border px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.08em] transition-colors ${
        inWatchlist
          ? 'border-yellow-400 bg-yellow-50 text-yellow-700 hover:bg-yellow-100 dark:border-yellow-600 dark:bg-yellow-500/10 dark:text-yellow-300'
          : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50 dark:border-gray-700 dark:bg-brand-surface dark:text-gray-300'
      }`}
    >
      <Star
        className={`h-3.5 w-3.5 ${inWatchlist ? 'fill-yellow-500' : ''}`}
      />
      <span>
        {inWatchlist ? 'In Watchlist' : 'Add to Watchlist'}
      </span>
    </button>
  );
};
