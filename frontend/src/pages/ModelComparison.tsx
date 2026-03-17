import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Layout } from '../components/Layout';
import { StockSearch } from '../components/StockSearch';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorAlert } from '../components/ErrorAlert';
import { ModelComparisonChart } from '../components/ModelComparisonChart';
import { stockApi } from '../services/api';
import { BarChart3, Trophy } from 'lucide-react';

interface ComparisonMetricRow {
  model: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  auc: number;
}

interface ModelComparisonResponse {
  models_trained: number;
  comparison: ComparisonMetricRow[];
  best_model: {
    model_type: string;
    score: number;
  } | null;
}

export const ModelComparison: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);

  const { data, isLoading, error, refetch } = useQuery<ModelComparisonResponse>({
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
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-3 rounded-full bg-blue-50 dark:bg-brand-accent/10">
            <BarChart3 className="h-8 w-8 text-brand-accent dark:text-brand-accent" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white tracking-tight">
              Model Comparison
            </h1>
            <p className="text-sm font-medium text-gray-500 dark:text-gray-400 mt-1 uppercase tracking-wider">
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
            <div className="glass-panel p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6 tracking-tight">
                Results for {selectedTicker}
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 dark:bg-brand-accent/10 rounded-xl p-4 border border-blue-100 dark:border-brand-accent/20">
                  <p className="text-sm font-medium text-brand-accent dark:text-brand-accent uppercase tracking-wider">Models Trained</p>
                  <p className="text-3xl font-mono font-bold text-gray-900 dark:text-white mt-2 tracking-tight">
                    {data.models_trained}
                  </p>
                </div>
                {data.best_model && (
                  <>
                    <div className="bg-green-50 dark:bg-financial-green/10 rounded-xl p-4 border border-green-100 dark:border-financial-green/20">
                      <div className="flex items-center space-x-2">
                        <Trophy className="h-4 w-4 text-financial-green" />
                        <p className="text-sm font-medium text-financial-green dark:text-financial-green uppercase tracking-wider">Best Model</p>
                      </div>
                      <p className="text-xl font-bold text-gray-900 dark:text-white mt-1">
                        {data.best_model.model_type}
                      </p>
                    </div>
                    <div className="bg-yellow-50 dark:bg-financial-yellow/10 rounded-xl p-4 border border-yellow-100 dark:border-financial-yellow/20">
                      <p className="text-sm font-medium text-financial-yellow dark:text-financial-yellow uppercase tracking-wider">Best Score (AUC)</p>
                      <p className="text-3xl font-mono font-bold text-gray-900 dark:text-white mt-2 tracking-tight">
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

                <div className="glass-panel overflow-hidden">
                  <div className="p-6 border-b border-gray-200 dark:border-white/5">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
                      Detailed Metrics Comparison
                    </h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-white/5">
                      <thead className="bg-gray-50 dark:bg-brand-surfaceHover">
                        <tr>
                          <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Model
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Accuracy
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Precision
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            Recall
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            F1 Score
                          </th>
                          <th className="px-6 py-4 text-left text-xs font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                            AUC
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-brand-surface divide-y divide-gray-200 dark:divide-white/5">
                        {data.comparison.map((model, index: number) => (
                          <tr key={index} className={data.best_model?.model_type === model.model ? 'bg-green-50/50 dark:bg-financial-green/5' : 'hover:bg-gray-50 dark:hover:bg-brand-surfaceHover transition-colors'}>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                {data.best_model?.model_type === model.model && (
                                  <Trophy className="h-4 w-4 text-financial-green mr-2" />
                                )}
                                <span className="text-sm font-bold text-gray-900 dark:text-white">
                                  {model.model}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono font-medium text-gray-600 dark:text-gray-300">
                              {(model.accuracy * 100).toFixed(2)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono font-medium text-gray-600 dark:text-gray-300">
                              {(model.precision * 100).toFixed(2)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono font-medium text-gray-600 dark:text-gray-300">
                              {(model.recall * 100).toFixed(2)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono font-medium text-gray-600 dark:text-gray-300">
                              {(model.f1_score * 100).toFixed(2)}%
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono font-medium text-brand-accent dark:text-brand-accent">
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
          <div className="glass-panel p-12 text-center flex flex-col items-center justify-center">
            <div className="p-4 rounded-full bg-gray-100 dark:bg-brand-surfaceHover mb-6">
              <BarChart3 className="h-12 w-12 text-brand-accent dark:text-brand-accent" />
            </div>
            <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 tracking-tight">
              Compare ML Models
            </h3>
            <p className="text-gray-500 dark:text-gray-400 max-w-md mx-auto mb-8 text-lg">
              Train and compare Logistic Regression, Random Forest, XGBoost, and Gradient Boosting models
            </p>
            <div className="bg-gray-50 dark:bg-brand-surfaceHover rounded-xl p-6 inline-block text-left border border-gray-100 dark:border-white/5">
              <ul className="space-y-3 text-sm font-medium text-gray-600 dark:text-gray-300">
                <li className="flex items-center space-x-3">
                  <span className="text-brand-accent text-lg">✓</span>
                  <span>See which model performs best for your stock</span>
                </li>
                <li className="flex items-center space-x-3">
                  <span className="text-brand-accent text-lg">✓</span>
                  <span>Compare accuracy, precision, recall, and F1 score</span>
                </li>
                <li className="flex items-center space-x-3">
                  <span className="text-brand-accent text-lg">✓</span>
                  <span>Visual bar charts for easy model-by-metric comparison</span>
                </li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
