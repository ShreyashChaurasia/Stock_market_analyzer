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
import { StatsCard } from '../components/StatsCard';
import { TechnicalIndicators } from '../components/TechnicalIndicators';
import { MarketSummary } from '../components/MarketSummary';
import { stockApi } from '../services/api';
import type { PredictionResponse } from '../types/stock';
import { useWatchlistStore } from '../store/watchlistStore';
import { TrendingUp, DollarSign, Target, BarChart3, Brain } from 'lucide-react';

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

  React.useEffect(() => {
    if (data && selectedTicker) {
      updateWatchlistItem(selectedTicker, {
        latestPrice: data.latest_close,
        prediction: data.prediction,
      });
    }
  }, [data, selectedTicker, updateWatchlistItem]);

  return (
    <Layout>
      <div className="space-y-6">
        {/* Market Summary - Always visible */}
        <MarketSummary />

        {/* Hero Section */}
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            AI-Powered Stock Analysis
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Get predictions for US and Indian stocks using advanced machine learning
          </p>
        </div>

        {/* Search Section */}
        <div className="max-w-3xl mx-auto">
          <StockSearch onSearch={handleSearch} loading={isLoading} />
        </div>

        {/* Loading State */}
        {isLoading && (
          <LoadingSpinner message="Analyzing stock data and generating prediction..." />
        )}

        {/* Error State */}
        {error && (
          <ErrorAlert
            message={(error as Error).message || 'Failed to fetch prediction'}
            onRetry={() => refetch()}
          />
        )}

        {/* Results Section */}
        {data && !isLoading && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Content - 2 columns */}
            <div className="lg:col-span-2 space-y-6">
              {/* Watchlist Button */}
              <div className="flex justify-end">
                <WatchlistButton
                  ticker={data.ticker}
                  latestPrice={data.latest_close}
                  prediction={data.prediction}
                />
              </div>

              {/* Statistics Cards */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <StatsCard
                  title="Current Price"
                  value={`$${data.latest_close.toFixed(2)}`}
                  icon={DollarSign}
                  color="blue"
                />
                <StatsCard
                  title="Probability Up"
                  value={`${(data.probability_up * 100).toFixed(1)}%`}
                  icon={TrendingUp}
                  color={data.prediction === 'UP' ? 'green' : 'red'}
                />
                <StatsCard
                  title="Confidence"
                  value={`${(data.confidence * 100).toFixed(1)}%`}
                  subtitle={data.interpretation}
                  icon={Target}
                  color="purple"
                />
                <StatsCard
                  title="Model AUC"
                  value={data.model_auc.toFixed(4)}
                  subtitle={`${data.data_points_used} data points`}
                  icon={Brain}
                  color="yellow"
                />
              </div>

              {/* Prediction Card */}
              <PredictionCard prediction={data} />

              {/* Charts Row 1 */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ProbabilityChart
                  probabilityUp={data.probability_up}
                  probabilityDown={data.probability_down}
                />
                <PriceChart ticker={data.ticker} period="1mo" />
              </div>
            </div>

            {/* Sidebar - 1 column */}
            <div className="space-y-6">
              <Watchlist onSelectStock={handleSearch} />
              <TechnicalIndicators ticker={data.ticker} />
            </div>
          </div>
        )}

        {/* Empty State with Watchlist */}
        {!selectedTicker && !isLoading && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 text-center">
                <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Start Your Analysis
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  Enter a stock ticker above to get AI-powered predictions and insights
                </p>
              </div>
            </div>
            <div>
              <Watchlist onSelectStock={handleSearch} />
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};