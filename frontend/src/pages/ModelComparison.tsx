import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { StockSearch } from '../components/StockSearch';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { ModelComparisonChart } from '../components/ModelComparisonChart';
import { stockApi } from '../services/api';
import { BarChart3, Trophy } from 'lucide-react';

export const ModelComparison: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['compare-models', selectedTicker],
    queryFn: async () => {
      const result = await stockApi.compareModels(selectedTicker!);
      return result.data;
    },
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
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Model Comparison
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Train and compare all ML models to find the best performer
            </p>
          </div>
        </div>

        <div className="max-w-2xl">
          <StockSearch onSearch={handleSearch} loading={isLoading} />
        </div>

        {isLoading && (
          <LoadingSpinner message="Training and comparing all models... This may take 2-3 minutes" />
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
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-primary-50 dark:bg-primary-900/20 rounded-lg p-4">
                  <p className="text-sm text-primary-600 dark:text-primary-400">Models Trained</p>
                  <p className="text-2xl font-bold text-primary-900 dark:text-primary-100">
                    {data.models_trained}
                  </p>
                </div>
                {data.best_model && (
                  <>
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                      <div className="flex items-center space-x-2">
                        <Trophy className="h-5 w-5 text-green-600" />
                        <p className="text-sm text-green-600 dark:text-green-400">Best Model</p>
                      </div>
                      <p className="text-xl font-bold text-green-900 dark:text-green-100 mt-1">
                        {data.best_model.model_type}
                      </p>
                    </div>
                    <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                      <p className="text-sm text-yellow-600 dark:text-yellow-400">Best Score (AUC)</p>
                      <p className="text-2xl font-bold text-yellow-900 dark:text-yellow-100">
                        {(data.best_model.score * 100).toFixed(2)}%
                      </p>
                    </div>
                  </>
                )}
              </div>
            </div>

            {data.comparison && data.comparison.length > 0 && (
              <>
                <ModelComparisonChart models={data.comparison} />

                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden">
                  <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                      Detailed Metrics Comparison
                    </h3>
                  </div>
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
                        {data.comparison.map((model: any, index: number) => (
                          <tr key={index} className={data.best_model?.model_type === model.model ? 'bg-green-50 dark:bg-green-900/10' : ''}>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                {data.best_model?.model_type === model.model && (
                                  <Trophy className="h-4 w-4 text-green-600 mr-2" />
                                )}
                                <span className="text-sm font-medium text-gray-900 dark:text-white">
                                  {model.model}
                                </span>
                              </div>
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

        {!selectedTicker && !isLoading && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 text-center">
            <BarChart3 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
              Compare ML Models
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6">
              Train and compare Logistic Regression, Random Forest, XGBoost, and Gradient Boosting models
            </p>
            <ul className="text-left max-w-md mx-auto space-y-2 text-gray-600 dark:text-gray-400">
              <li className="flex items-center space-x-2">
                <span className="text-green-600">✓</span>
                <span>See which model performs best for your stock</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-green-600">✓</span>
                <span>Compare accuracy, precision, recall, and F1 score</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-green-600">✓</span>
                <span>Visual radar chart for easy comparison</span>
              </li>
            </ul>
          </div>
        )}
      </div>
    </Layout>
  );
};