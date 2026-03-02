import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { StockSearch } from '../components/StockSearch';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { ModelComparisonChart } from '../components/ModelComparisonChart';
import { stockApi } from '../services/api';
import { BarChart3 } from 'lucide-react';

export const ModelComparison: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['compare-models', selectedTicker],
    queryFn: () => stockApi.compareModels(selectedTicker!),
    enabled: !!selectedTicker,
    retry: 1,
  });

  const handleSearch = (ticker: string) => {
    setSelectedTicker(ticker);
  };

  return (
    <Layout>
      <div className="space-y-6">
        <div className="flex items-center space-x-3">
          <BarChart3 className="h-8 w-8 text-primary-600" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Model Comparison
          </h1>
        </div>

        <div className="max-w-2xl">
          <StockSearch onSearch={handleSearch} loading={isLoading} />
        </div>

        {isLoading && (
          <LoadingSpinner message="Training and comparing all models..." />
        )}

        {error && (
          <ErrorAlert
            message={(error as Error).message || 'Failed to compare models'}
            onRetry={() => refetch()}
          />
        )}

        {data && !isLoading && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                Results for {selectedTicker}
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {data.data.models_trained} models trained and compared
              </p>
              
              {data.data.best_model && (
                <div className="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg p-4">
                  <p className="text-sm font-medium text-primary-900 dark:text-primary-100">
                    Best Model: {data.data.best_model.model_type}
                  </p>
                  <p className="text-sm text-primary-700 dark:text-primary-300">
                    Score: {(data.data.best_model.score * 100).toFixed(2)}%
                  </p>
                </div>
              )}
            </div>

            {data.data.comparison && data.data.comparison.length > 0 && (
              <>
                <ModelComparisonChart models={data.data.comparison} />

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                      <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Model
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Accuracy
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Precision
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            Recall
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            F1 Score
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                            AUC
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                        {data.data.comparison.map((model: any) => (
                          <tr key={model.model}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                              {model.model}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                              {(model.accuracy * 100).toFixed(2)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                              {(model.precision * 100).toFixed(2)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                              {(model.recall * 100).toFixed(2)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                              {(model.f1_score * 100).toFixed(2)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                              {(model.auc * 100).toFixed(2)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </Layout>
  );
};