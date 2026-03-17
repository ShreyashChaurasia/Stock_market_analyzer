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
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg border transition-colors ${
        inWatchlist
          ? 'bg-yellow-50 border-yellow-500 text-yellow-700 hover:bg-yellow-100'
          : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
      }`}
    >
      <Star
        className={`h-5 w-5 ${inWatchlist ? 'fill-yellow-500' : ''}`}
      />
      <span className="font-medium">
        {inWatchlist ? 'In Watchlist' : 'Add to Watchlist'}
      </span>
    </button>
  );
};
