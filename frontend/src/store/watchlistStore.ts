import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface WatchlistItem {
  ticker: string;
  addedAt: string;
  latestPrice?: number;
  prediction?: string;
}

interface WatchlistStore {
  watchlist: WatchlistItem[];
  addToWatchlist: (ticker: string) => void;
  removeFromWatchlist: (ticker: string) => void;
  isInWatchlist: (ticker: string) => boolean;
  updateWatchlistItem: (ticker: string, data: Partial<WatchlistItem>) => void;
  clearWatchlist: () => void;
}

export const useWatchlistStore = create<WatchlistStore>()(
  persist(
    (set, get) => ({
      watchlist: [],
      
      addToWatchlist: (ticker) => {
        const exists = get().watchlist.find(item => item.ticker === ticker);
        if (!exists) {
          set((state) => ({
            watchlist: [
              ...state.watchlist,
              {
                ticker: ticker.toUpperCase(),
                addedAt: new Date().toISOString(),
              },
            ],
          }));
        }
      },
      
      removeFromWatchlist: (ticker) => {
        set((state) => ({
          watchlist: state.watchlist.filter(item => item.ticker !== ticker),
        }));
      },
      
      isInWatchlist: (ticker) => {
        return get().watchlist.some(item => item.ticker === ticker);
      },
      
      updateWatchlistItem: (ticker, data) => {
        set((state) => ({
          watchlist: state.watchlist.map(item =>
            item.ticker === ticker ? { ...item, ...data } : item
          ),
        }));
      },
      
      clearWatchlist: () => {
        set({ watchlist: [] });
      },
    }),
    {
      name: 'watchlist-storage',
    }
  )
);