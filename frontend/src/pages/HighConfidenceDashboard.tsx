import React, { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  CheckCircle2,
  Gauge,
  RefreshCw,
  SlidersHorizontal,
  Sparkles,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';
import { Layout } from '../components/Layout';
import { ErrorAlert } from '../components/ErrorAlert';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { NewsCard } from '../components/NewsCard';
import { stockApi } from '../services/api';
import { useWatchlistStore } from '../store/watchlistStore';
import type { HighConfidenceDashboardResponse } from '../types/stock';
import { formatCurrency } from '../utils/market';

type MarketFilter = 'ALL' | 'US' | 'INDIA';

const MARKET_OPTIONS: MarketFilter[] = ['ALL', 'US', 'INDIA'];
const DEFAULT_CONFIDENCE_THRESHOLD = 0.3;
const DEFAULT_MIN_AUC = 0.5;

const clamp = (value: number, min: number, max: number): number =>
  Math.min(max, Math.max(min, value));

export const HighConfidenceDashboard: React.FC = () => {
  const [market, setMarket] = useState<MarketFilter>('ALL');
  const [includeNews, setIncludeNews] = useState<boolean>(true);
  const [draftConfidenceThreshold, setDraftConfidenceThreshold] = useState<number>(DEFAULT_CONFIDENCE_THRESHOLD);
  const [draftMinAuc, setDraftMinAuc] = useState<number>(DEFAULT_MIN_AUC);
  const [appliedConfidenceThreshold, setAppliedConfidenceThreshold] = useState<number>(DEFAULT_CONFIDENCE_THRESHOLD);
  const [appliedMinAuc, setAppliedMinAuc] = useState<number>(DEFAULT_MIN_AUC);
  const [isRefreshingBatch, setIsRefreshingBatch] = useState<boolean>(false);
  const [refreshErrorMessage, setRefreshErrorMessage] = useState<string | null>(null);
  const watchlist = useWatchlistStore((state) => state.watchlist);

  const watchlistParam = useMemo(
    () => watchlist.map((item) => item.ticker).join(','),
    [watchlist]
  );

  const hasPendingThresholdChanges =
    Math.abs(draftConfidenceThreshold - appliedConfidenceThreshold) > 0.0001 ||
    Math.abs(draftMinAuc - appliedMinAuc) > 0.0001;

  const { data, isLoading, error, refetch } = useQuery<HighConfidenceDashboardResponse>({
    queryKey: [
      'dashboard',
      'quant-discovery',
      market,
      includeNews,
      watchlistParam,
      appliedConfidenceThreshold,
      appliedMinAuc,
    ],
    queryFn: () =>
      stockApi.getHighConfidenceDashboard(
        market,
        12,
        watchlistParam || undefined,
        includeNews,
        appliedConfidenceThreshold,
        appliedMinAuc
      ),
    retry: 1,
  });

  const applyThresholdSettings = () => {
    setAppliedConfidenceThreshold(draftConfidenceThreshold);
    setAppliedMinAuc(draftMinAuc);
  };

  const resetThresholdSettings = () => {
    setDraftConfidenceThreshold(DEFAULT_CONFIDENCE_THRESHOLD);
    setDraftMinAuc(DEFAULT_MIN_AUC);
    setAppliedConfidenceThreshold(DEFAULT_CONFIDENCE_THRESHOLD);
    setAppliedMinAuc(DEFAULT_MIN_AUC);
  };

  const triggerBatchRefresh = async () => {
    setIsRefreshingBatch(true);
    setRefreshErrorMessage(null);
    try {
      await stockApi.refreshHighConfidenceDashboard(
        market,
        12,
        watchlistParam || undefined,
        includeNews,
        appliedConfidenceThreshold,
        appliedMinAuc
      );
      await refetch();
    } catch (errorObj) {
      setRefreshErrorMessage((errorObj as Error).message || 'Failed to refresh dashboard cache.');
    } finally {
      setIsRefreshingBatch(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-4 animate-fade-in">
        <div className="glass-panel p-4">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <div className="mb-2 inline-flex items-center gap-2 rounded-full bg-green-50 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.1em] text-financial-green dark:bg-financial-green/10 dark:text-financial-green">
                <Sparkles className="h-3.5 w-3.5" />
                Quant Discovery
              </div>
              <h1 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white md:text-3xl">
                Quant Discovery Signals
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                Ranked stocks where confidence and model quality both clear your selected threshold.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              {MARKET_OPTIONS.map((option) => {
                const isActive = option === market;
                return (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setMarket(option)}
                    className={`rounded-md px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.1em] transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-brand-surfaceHover dark:text-gray-200 dark:hover:bg-gray-700'
                    }`}
                  >
                    {option}
                  </button>
                );
              })}
              <button
                type="button"
                onClick={() => setIncludeNews((prev) => !prev)}
                className={`rounded-md px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.1em] transition-colors ${
                  includeNews
                    ? 'bg-brand-accent text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-brand-surfaceHover dark:text-gray-200 dark:hover:bg-gray-700'
                }`}
              >
                {includeNews ? 'News On' : 'News Off'}
              </button>
            </div>
          </div>
        </div>

        <div className="glass-panel p-4">
          <div className="mb-4 flex items-center gap-2">
            <SlidersHorizontal className="h-4 w-4 text-brand-accent" />
            <h2 className="text-base font-semibold tracking-tight text-gray-900 dark:text-white">Signal Filters</h2>
          </div>

          <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
            <div>
              <label className="text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                Confidence Threshold
              </label>
              <div className="mt-2 flex items-center gap-3">
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.01}
                  value={draftConfidenceThreshold}
                  onChange={(event) =>
                    setDraftConfidenceThreshold(clamp(Number(event.target.value), 0, 1))
                  }
                  className="w-full"
                />
                <input
                  type="number"
                  min={0}
                  max={1}
                  step={0.01}
                  value={draftConfidenceThreshold}
                  onChange={(event) => {
                    const nextValue = Number(event.target.value);
                    if (!Number.isNaN(nextValue)) {
                      setDraftConfidenceThreshold(clamp(nextValue, 0, 1));
                    }
                  }}
                  className="w-20 rounded-md border border-gray-200 bg-white px-2 py-1 text-sm text-gray-900 dark:border-gray-700 dark:bg-brand-surface dark:text-gray-100"
                />
              </div>
            </div>

            <div>
              <label className="text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                Minimum Model AUC
              </label>
              <div className="mt-2 flex items-center gap-3">
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.01}
                  value={draftMinAuc}
                  onChange={(event) => setDraftMinAuc(clamp(Number(event.target.value), 0, 1))}
                  className="w-full"
                />
                <input
                  type="number"
                  min={0}
                  max={1}
                  step={0.01}
                  value={draftMinAuc}
                  onChange={(event) => {
                    const nextValue = Number(event.target.value);
                    if (!Number.isNaN(nextValue)) {
                      setDraftMinAuc(clamp(nextValue, 0, 1));
                    }
                  }}
                  className="w-20 rounded-md border border-gray-200 bg-white px-2 py-1 text-sm text-gray-900 dark:border-gray-700 dark:bg-brand-surface dark:text-gray-100"
                />
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={applyThresholdSettings}
              disabled={!hasPendingThresholdChanges}
              className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.1em] text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Apply Settings
            </button>
            <button
              type="button"
              onClick={resetThresholdSettings}
              className="rounded-md bg-gray-100 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.1em] text-gray-700 hover:bg-gray-200 dark:bg-brand-surfaceHover dark:text-gray-200 dark:hover:bg-gray-700"
            >
              Reset Defaults
            </button>
            <button
              type="button"
              onClick={() => {
                void triggerBatchRefresh();
              }}
              disabled={isRefreshingBatch}
              className="inline-flex items-center gap-1.5 rounded-md bg-financial-green px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.1em] text-white hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-70"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isRefreshingBatch ? 'animate-spin' : ''}`} />
              {isRefreshingBatch ? 'Refreshing Broad Scan...' : 'Refresh Broad Scan'}
            </button>
          </div>

          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            Broad discovery evaluates a much larger ticker universe; the first scan may take longer to complete.
          </p>

          {refreshErrorMessage && (
            <p className="mt-2 text-sm text-red-600 dark:text-red-400">{refreshErrorMessage}</p>
          )}
        </div>

        {isLoading && (
          <LoadingSpinner message="Scanning a broad US/India universe (~600 liquid symbols). Please wait for quant discovery to complete..." />
        )}

        {error && (
          <ErrorAlert
            message={(error as Error).message || 'Failed to load Quant Discovery dashboard'}
            onRetry={() => {
              void refetch();
            }}
          />
        )}

        {data && !isLoading && !error && (
          <>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
              <div className="glass-panel p-4">
                <div className="mb-2 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                  <Gauge className="h-3.5 w-3.5 text-brand-accent" />
                  Evaluated Tickers
                </div>
                <div className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
                  {data.evaluated_tickers}
                </div>
              </div>

              <div className="glass-panel p-4">
                <div className="mb-2 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                  <CheckCircle2 className="h-3.5 w-3.5 text-financial-green" />
                  Qualified Signals
                </div>
                <div className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
                  {data.qualified_count}
                </div>
              </div>

              <div className="glass-panel p-4">
                <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                  Thresholds
                </div>
                <div className="text-sm text-gray-700 dark:text-gray-300">
                  confidence {'>='} {(data.thresholds.confidence * 100).toFixed(0)}% | AUC {'>='}{' '}
                  {data.thresholds.model_auc.toFixed(2)}
                </div>
                <div className="mt-2 text-[11px] uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                  Cache {data.cache_hit ? 'HIT' : 'MISS'}
                </div>
              </div>
            </div>

            {data.items.length === 0 ? (
              <div className="glass-panel p-6 text-sm text-gray-500 dark:text-gray-400">
                No symbols currently satisfy the Quant Discovery thresholds for this market filter.
              </div>
            ) : (
              <div className="space-y-4">
                {data.items.map((item) => {
                  const isUp = item.prediction === 'UP';
                  return (
                    <div key={item.ticker} className="glass-panel p-4">
                      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                        <div>
                          <div className="mb-2 flex items-center gap-2">
                            <h2 className="text-xl font-semibold tracking-tight text-gray-900 dark:text-white">
                              {item.ticker}
                            </h2>
                            <span
                              className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.1em] ${
                                isUp
                                  ? 'border-financial-green/30 bg-financial-green/10 text-financial-green'
                                  : 'border-financial-red/30 bg-financial-red/10 text-financial-red'
                              }`}
                            >
                              {isUp ? <TrendingUp className="mr-1 h-3.5 w-3.5" /> : <TrendingDown className="mr-1 h-3.5 w-3.5" />}
                              {item.prediction}
                            </span>
                            <span className="rounded-full bg-blue-50 px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.1em] text-brand-accent dark:bg-brand-accent/10 dark:text-brand-accent">
                              {item.confidence_tier.replace('_', ' ')}
                            </span>
                          </div>

                          <p className="text-sm text-gray-600 dark:text-gray-300">{item.interpretation}</p>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-right md:grid-cols-4 lg:min-w-[520px]">
                          <div>
                            <div className="text-[11px] uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">Price</div>
                            <div className="text-sm font-semibold text-gray-900 dark:text-white">
                              {formatCurrency(item.latest_close, item.currency)}
                            </div>
                          </div>
                          <div>
                            <div className="text-[11px] uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">Confidence</div>
                            <div className="text-sm font-semibold text-gray-900 dark:text-white">
                              {(item.confidence * 100).toFixed(1)}%
                            </div>
                          </div>
                          <div>
                            <div className="text-[11px] uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">Prob. Up</div>
                            <div className="text-sm font-semibold text-gray-900 dark:text-white">
                              {(item.probability_up * 100).toFixed(1)}%
                            </div>
                          </div>
                          <div>
                            <div className="text-[11px] uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">Model AUC</div>
                            <div className="text-sm font-semibold text-gray-900 dark:text-white">
                              {item.model_auc.toFixed(4)}
                            </div>
                          </div>
                        </div>
                      </div>

                      {includeNews && item.news && item.news.length > 0 && (
                        <div className="mt-4 grid grid-cols-1 gap-3 xl:grid-cols-2">
                          {item.news.map((article) => (
                            <NewsCard key={`${item.ticker}-${article.url}`} article={article} compact />
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}
      </div>
    </Layout>
  );
};
