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
import { IndicesCharts } from '../components/IndicesCharts';
import { StockOverview } from '../components/StockOverview';
import { stockApi } from '../services/api';
import type { PredictionResponse, StockInfo } from '../types/stock';
import type { MarketIndexKey } from '../types/stock';
import { useWatchlistStore } from '../store/watchlistStore';
import { TrendingUp, Landmark, Target, BarChart3, Activity, Scale } from 'lucide-react';
import { formatCompactCurrency, formatCurrency, formatLargeNumber, inferCurrencyFromTicker } from '../utils/market';

export const Dashboard: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const [selectedIndex, setSelectedIndex] = useState<MarketIndexKey | null>(null);
  const [shouldScrollToStockInfo, setShouldScrollToStockInfo] = useState(false);
  const { updateWatchlistItem } = useWatchlistStore();
  const stockInfoRef = React.useRef<HTMLDivElement | null>(null);

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

  const handleIndexSelect = (indexKey: MarketIndexKey) => {
    setSelectedIndex((current) => (current === indexKey ? null : indexKey));
  };

  const handleWatchlistSelect = (ticker: string) => {
    setSelectedTicker(ticker);
    setShouldScrollToStockInfo(true);
  };

  React.useEffect(() => {
    if (data && selectedTicker) {
      const previousClose = stockInfoData?.data?.previous_close;
      const hasPreviousClose = previousClose !== null && previousClose !== undefined && previousClose !== 0;
      const change = hasPreviousClose ? data.latest_close - previousClose : undefined;
      const changePercent = hasPreviousClose ? (change! / previousClose) * 100 : undefined;

      updateWatchlistItem(selectedTicker, {
        latestPrice: data.latest_close,
        prediction: data.prediction,
        currency: data.currency,
        change,
        changePercent,
      });
    }
  }, [data, selectedTicker, stockInfoData, updateWatchlistItem]);

  React.useEffect(() => {
    if (!shouldScrollToStockInfo || !data || !stockInfoRef.current) {
      return;
    }

    stockInfoRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setShouldScrollToStockInfo(false);
  }, [data, shouldScrollToStockInfo]);

  const stockInfo = stockInfoData?.data;
  const resolvedCurrency = stockInfo?.currency ?? data?.currency ?? inferCurrencyFromTicker(selectedTicker);
  const locale = resolvedCurrency === 'INR' ? 'en-IN' : 'en-US';
  const previousClose = stockInfo?.previous_close;
  const hasPreviousClose = previousClose !== null && previousClose !== undefined && previousClose !== 0;
  const watchlistChange = data && hasPreviousClose ? data.latest_close - previousClose : undefined;
  const watchlistChangePercent =
    data && hasPreviousClose && watchlistChange !== undefined
      ? (watchlistChange / previousClose) * 100
      : undefined;

  return (
    <Layout>
      <div className="space-y-4 animate-fade-in">
        {/* Market Summary - Always visible */}
        <MarketSummary selectedIndex={selectedIndex} onSelectIndex={handleIndexSelect} />
        {selectedIndex && <IndicesCharts selectedIndex={selectedIndex} />}

        {/* Hero Section */}
        <div className="py-2 text-center">
          <h1 className="mb-2 text-2xl font-semibold tracking-tight text-gray-900 dark:text-white md:text-3xl">
            Quant-Driven Stock Analysis
          </h1>
          <p className="mx-auto max-w-2xl text-sm text-gray-600 dark:text-gray-400">
            Real-time analysis and machine-learning forecasts for US and Indian equities.
          </p>
        </div>

        {/* Search Section */}
        <div className="mx-auto max-w-3xl">
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
          <div ref={stockInfoRef} className="space-y-4">
            {/* Top Watchlist Button for Symmetry */}
            <div className="flex justify-end w-full">
                <WatchlistButton
                  ticker={data.ticker}
                  latestPrice={data.latest_close}
                  prediction={data.prediction}
                  currency={resolvedCurrency}
                  change={watchlistChange}
                  changePercent={watchlistChangePercent}
                />
              </div>

              {/* Statistics Cards */}
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
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
            <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
              <div className="space-y-4 xl:col-span-2">
                <PriceChart ticker={data.ticker} currency={resolvedCurrency} />
                <TechnicalIndicators ticker={data.ticker} currency={resolvedCurrency} />
              </div>

              <div className="space-y-4">
                <PredictionCard prediction={data} currency={resolvedCurrency} />
                <StockOverview info={stockInfo} isLoading={isStockInfoLoading} />
              </div>
            </div>

            {/* Bottom Section - Watchlist */}
            <div className="w-full">
              <Watchlist onSelectStock={handleWatchlistSelect} />
            </div>
          </div>
        )}

        {/* Empty State */}
        {!selectedTicker && !isLoading && (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="glass-panel flex h-full flex-col items-center justify-center p-8 text-center md:p-10">
              <div className="mb-4 rounded-full bg-gray-100 p-3 dark:bg-brand-surfaceHover">
                <BarChart3 className="h-8 w-8 text-brand-accent dark:text-brand-accent" />
              </div>
              <h3 className="mb-2 text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
                Terminal Ready
              </h3>
              <p className="mx-auto max-w-md text-sm text-gray-500 dark:text-gray-400">
                Enter a stock ticker above (e.g., AAPL, RELIANCE.NS) to execute deep analysis.
              </p>
            </div>
            <div>
              <Watchlist onSelectStock={handleWatchlistSelect} />
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
