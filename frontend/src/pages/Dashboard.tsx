import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { StockSearch } from '../components/StockSearch';
import { PredictionCard } from '../components/PredictionCard';
import { PriceChart } from '../components/PriceChart';
import { ProbabilityChart } from '../components/probabilityChart';
import { Watchlist } from '../components/Watchlist';
import { WatchlistButton } from '../components/WatchlistButton';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { stockApi } from '../services/api';
import type { PredictionResponse } from '../types/stock';
import { useWatchlistStore } from '../store/watchlistStore';

export const Dashboard: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const { updateWatchlistItem } = useWatchlistStore();

  const { data, isLoading, error, refetch } = useQuery<PredictionResponse>({
    queryKey: ['prediction', selectedTicker],
    queryFn: () => stockApi.getPrediction({ ticker: selectedTicker! }),
    enabled: !!selectedTicker,
    retry: 1,
  });

  const handleSearch = (ticker: string) => {
    setSelectedTicker(ticker);
  };

  // Update watchlist when we get new data
  React.useEffect(() => {
    if (data && selectedTicker) {
      updateWatchlistItem(selectedTicker, {
        latestPrice: data.latest_close,
        prediction: data.prediction,
      });
    }
  }, [data, selectedTicker]);

  // Mock price data for chart
  const mockPriceData = data
    ? Array.from({ length: 30 }, (_, i) => ({
        date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString(),
        close: data.latest_close * (1 + (Math.random() - 0.5) * 0.1),
      }))
    : [];

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
              Stock Market Prediction
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Get AI-powered predictions for your favorite stocks
            </p>
          </div>

          <StockSearch onSearch={handleSearch} loading={isLoading} />

          {isLoading && (
            <LoadingSpinner message="Analyzing stock data and generating prediction..." />
          )}

          {error && (
            <ErrorAlert
              message={(error as Error).message || 'Failed to fetch prediction'}
              onRetry={() => refetch()}
            />
          )}

          {data && !isLoading && (
            <div className="space-y-6">
              <div className="flex justify-end">
                <WatchlistButton
                  ticker={data.ticker}
                  latestPrice={data.latest_close}
                  prediction={data.prediction}
                />
              </div>

              <PredictionCard prediction={data} />

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ProbabilityChart
                  probabilityUp={data.probability_up}
                  probabilityDown={data.probability_down}
                />
                <PriceChart data={mockPriceData} ticker={data.ticker} />
              </div>
            </div>
          )}

          {!selectedTicker && !isLoading && (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                Enter a stock ticker above to get started
              </p>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <Watchlist onSelectStock={handleSearch} />
        </div>
      </div>
    </Layout>
  );
};