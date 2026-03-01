import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { StockSearch } from '../components/StockSearch';
import { PredictionCard } from '../components/PredictionCard';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { stockApi } from '../services/api';
import type { PredictionResponse } from '../types/stock';

export const Dashboard: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);

  const { data, isLoading, error, refetch } = useQuery<PredictionResponse>({
    queryKey: ['prediction', selectedTicker],
    queryFn: () => stockApi.getPrediction({ ticker: selectedTicker! }),
    enabled: !!selectedTicker,
    retry: 1,
  });

  const handleSearch = (ticker: string) => {
    setSelectedTicker(ticker);
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Stock Market Prediction
          </h1>
          <p className="text-gray-600">
            Get AI-powered predictions for your favorite stocks
          </p>
        </div>

        <div className="max-w-2xl mx-auto">
          <StockSearch onSearch={handleSearch} loading={isLoading} />
        </div>

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
          <div className="max-w-2xl mx-auto">
            <PredictionCard prediction={data} />
          </div>
        )}

        {!selectedTicker && !isLoading && (
          <div className="text-center py-12">
            <p className="text-gray-500">
              Enter a stock ticker above to get started
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};