import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { StockSearch } from '../components/StockSearch';
import { PredictionCard } from '../components/PredictionCard';
import { PriceChart } from '../components/PriceChart';
import { Watchlist } from '../components/Watchlist';
import { WatchlistButton } from '../components/WatchlistButton';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { StatsCard } from '../components/StatsCard';
import { TechnicalIndicators } from '../components/TechnicalIndicators';
import { MarketSummary } from '../components/MarketSummary';
import { StockOverview } from '../components/StockOverview';
import { stockApi } from '../services/api';
import type { PredictionResponse, StockInfo } from '../types/stock';
import { useWatchlistStore } from '../store/watchlistStore';
import { TrendingUp, Landmark, Target, BarChart3, Activity, Scale } from 'lucide-react';
import { formatCompactCurrency, formatCurrency, formatLargeNumber, inferCurrencyFromTicker } from '../utils/market';

export const Dashboard: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const { updateWatchlistItem } = useWatchlistStore();

  const { data, isLoading, error, refetch } = useQuery<PredictionResponse>({
    queryKey: ['prediction', selectedTicker],
    queryFn: () => stockApi.getPrediction({ ticker: selectedTicker! }),
    enabled: !!selectedTicker,
    retry: 1,
  });

  const { data: stockInfoData, isLoading: isStockInfoLoading } = useQuery<{ data: StockInfo }>({
    queryKey: ['stock-info', selectedTicker],
    queryFn: () => stockApi.getStockInfo(selectedTicker!),
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
        currency: data.currency,
      });
    }
  }, [data, selectedTicker, updateWatchlistItem]);

  const stockInfo = stockInfoData?.data;
  const resolvedCurrency = stockInfo?.currency ?? data?.currency ?? inferCurrencyFromTicker(selectedTicker);
  const locale = resolvedCurrency === 'INR' ? 'en-IN' : 'en-US';

  return (
    <Layout>
      <div className="space-y-5 animate-fade-in">
        {/* Market Summary - Always visible */}
        <MarketSummary />

        {/* Hero Section */}
        <div className="text-center py-4">
          <h1 className="text-3xl md:text-5xl font-bold text-gray-900 dark:text-white mb-3 tracking-tight">
            AI-Powered Stock <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-teal-500">Analysis</span>
          </h1>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto text-sm md:text-base">
            Professional-grade predictions for US and Indian equities using advanced machine learning models.
          </p>
        </div>

        {/* Search Section */}
        <div className="max-w-4xl mx-auto">
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
          <div className="space-y-6">
            {/* Top Watchlist Button for Symmetry */}
            <div className="flex justify-end w-full">
                <WatchlistButton
                  ticker={data.ticker}
                  latestPrice={data.latest_close}
                  prediction={data.prediction}
                  currency={resolvedCurrency}
                />
              </div>

              {/* Statistics Cards */}
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3">
                <StatsCard
                  title="Current Price"
                  value={formatCurrency(data.latest_close, resolvedCurrency)}
                  subtitle={stockInfo?.company_name}
                  icon={Landmark}
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
                  title="Market Cap"
                  value={formatCompactCurrency(stockInfo?.market_cap, resolvedCurrency)}
                  subtitle={stockInfo?.exchange ?? 'Market value'}
                  icon={Landmark}
                  color="yellow"
                />
                <StatsCard
                  title="Current Volume"
                  value={formatLargeNumber(stockInfo?.current_volume, locale)}
                  subtitle={stockInfo ? `Avg ${formatLargeNumber(stockInfo.avg_volume, locale)}` : 'Volume traded'}
                  icon={Activity}
                  color="blue"
                />
                <StatsCard
                  title="52W Range"
                  value={
                    stockInfo
                      ? `${formatCurrency(stockInfo.low_52week, resolvedCurrency)} - ${formatCurrency(stockInfo.high_52week, resolvedCurrency)}`
                      : 'N/A'
                  }
                  subtitle={`${data.model_auc.toFixed(4)} model AUC`}
                  icon={Scale}
                  color="yellow"
                />
              </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
              <div className="xl:col-span-2">
                <PriceChart ticker={data.ticker} currency={resolvedCurrency} />
              </div>

              <div className="space-y-6">
                <PredictionCard prediction={data} currency={resolvedCurrency} />
                <StockOverview info={stockInfo} isLoading={isStockInfoLoading} />
              </div>
            </div>

            <TechnicalIndicators ticker={data.ticker} currency={resolvedCurrency} />

            {/* Bottom Section - Watchlist */}
            <div className="w-full">
              <Watchlist onSelectStock={handleSearch} />
            </div>
          </div>
        )}

        {/* Empty State */}
        {!selectedTicker && !isLoading && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="glass-panel p-10 md:p-16 text-center h-full flex flex-col items-center justify-center">
              <div className="p-4 rounded-full bg-gray-100 dark:bg-brand-surfaceHover mb-6">
                <BarChart3 className="h-12 w-12 text-brand-accent dark:text-brand-accent" />
              </div>
              <h3 className="text-3xl font-bold text-gray-900 dark:text-white mb-4 tracking-tight">
                Terminal Ready
              </h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto text-lg">
                Enter a stock ticker above (e.g., AAPL, RELIANCE.NS) to execute deep analysis.
              </p>
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
