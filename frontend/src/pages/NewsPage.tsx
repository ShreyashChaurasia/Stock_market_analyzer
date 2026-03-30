import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Flame, Newspaper } from 'lucide-react';
import { Layout } from '../components/Layout';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { NewsCard } from '../components/NewsCard';
import { stockApi } from '../services/api';
import type { LatestNewsResponse, TrendingNewsResponse } from '../types/stock';

type MarketFilter = 'ALL' | 'US' | 'INDIA';

const MARKET_OPTIONS: MarketFilter[] = ['ALL', 'US', 'INDIA'];

export const NewsPage: React.FC = () => {
  const [market, setMarket] = useState<MarketFilter>('ALL');

  const {
    data: latestNews,
    isLoading: isLatestLoading,
    error: latestError,
    refetch: refetchLatest,
  } = useQuery<LatestNewsResponse>({
    queryKey: ['news', 'latest', market],
    queryFn: () => stockApi.getLatestNews(market, 12),
    retry: 1,
  });

  const {
    data: trendingNews,
    isLoading: isTrendingLoading,
    error: trendingError,
    refetch: refetchTrending,
  } = useQuery<TrendingNewsResponse>({
    queryKey: ['news', 'trending', market],
    queryFn: () => stockApi.getTrendingNews(market, 10),
    retry: 1,
  });

  const isLoading = isLatestLoading || isTrendingLoading;
  const error = (latestError as Error | null) || (trendingError as Error | null);

  return (
    <Layout>
      <div className="space-y-4 animate-fade-in">
        <div className="glass-panel overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 via-cyan-600 to-teal-500 px-5 py-6 text-white">
            <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Market News Terminal</h1>
            <p className="mt-2 max-w-2xl text-sm text-blue-50">
              Follow the latest and trending headlines shaping equity markets.
            </p>
          </div>
          <div className="flex flex-wrap gap-2 border-t border-white/20 px-4 py-3 dark:border-white/5">
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
          </div>
        </div>

        {isLoading && <LoadingSpinner message="Fetching latest and trending market news..." />}

        {error && (
          <ErrorAlert
            message={error.message || 'Failed to load news'}
            onRetry={() => {
              void refetchLatest();
              void refetchTrending();
            }}
          />
        )}

        {!isLoading && !error && (
          <>
            <section className="glass-panel p-4">
              <div className="mb-3 flex items-center gap-2">
                <Flame className="h-4 w-4 text-financial-red" />
                <h2 className="text-base font-semibold tracking-tight text-gray-900 dark:text-white">
                  Trending Tickers
                </h2>
              </div>

              {trendingNews && trendingNews.trending_tickers.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {trendingNews.trending_tickers.map((ticker) => (
                    <div
                      key={ticker.ticker}
                      className="rounded-md border border-gray-200 bg-gray-50 px-3 py-2 dark:border-gray-700 dark:bg-brand-surfaceHover"
                    >
                      <div className="text-sm font-semibold text-gray-900 dark:text-white">{ticker.ticker}</div>
                      <div className="text-[11px] uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                        {ticker.mentions} mention{ticker.mentions > 1 ? 's' : ''}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Not enough data to identify trending tickers yet.
                </p>
              )}
            </section>

            <section>
              <div className="mb-3 flex items-center gap-2">
                <Newspaper className="h-4 w-4 text-brand-accent" />
                <h2 className="text-base font-semibold tracking-tight text-gray-900 dark:text-white">
                  Latest Headlines
                </h2>
              </div>

              {latestNews && latestNews.data.length > 0 ? (
                <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
                  {latestNews.data.map((article) => (
                    <NewsCard key={article.url} article={article} />
                  ))}
                </div>
              ) : (
                <div className="glass-panel p-6 text-sm text-gray-500 dark:text-gray-400">
                  No articles available right now. Try again in a few minutes.
                </div>
              )}
            </section>
          </>
        )}
      </div>
    </Layout>
  );
};
