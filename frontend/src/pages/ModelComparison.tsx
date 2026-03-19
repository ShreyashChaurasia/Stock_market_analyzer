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
      <div className="space-y-4">
        <div className="mb-2 flex items-center space-x-3">
          <div className="rounded-md bg-blue-50 p-2 dark:bg-brand-accent/10">
            <BarChart3 className="h-5 w-5 text-brand-accent dark:text-brand-accent" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
              Model Comparison
            </h1>
            <p className="mt-1 text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">
              Train and compare all ML models to find the best performer
            </p>
          </div>
        </div>

        <div className="max-w-3xl">
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
          <div className="space-y-4">
            <div className="glass-panel p-4">
              <h2 className="mb-3 text-base font-semibold tracking-tight text-gray-900 dark:text-white">
                Results for {selectedTicker}
              </h2>
              <div className="mb-1 grid grid-cols-1 gap-3 md:grid-cols-3">
                <div className="rounded-md border border-blue-100 bg-blue-50 p-3 dark:border-brand-accent/20 dark:bg-brand-accent/10">
                  <p className="text-[11px] font-semibold uppercase tracking-[0.1em] text-brand-accent dark:text-brand-accent">Models Trained</p>
                  <p className="mt-1 text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
                    {data.models_trained}
                  </p>
                </div>
                {data.best_model && (
                  <>
                    <div className="rounded-md border border-green-100 bg-green-50 p-3 dark:border-financial-green/20 dark:bg-financial-green/10">
                      <div className="flex items-center space-x-2">
                        <Trophy className="h-3.5 w-3.5 text-financial-green" />
                        <p className="text-[11px] font-semibold uppercase tracking-[0.1em] text-financial-green dark:text-financial-green">Best Model</p>
                      </div>
                      <p className="mt-1 text-base font-semibold text-gray-900 dark:text-white">
                        {data.best_model.model_type}
                      </p>
                    </div>
                    <div className="rounded-md border border-yellow-100 bg-yellow-50 p-3 dark:border-financial-yellow/20 dark:bg-financial-yellow/10">
                      <p className="text-[11px] font-semibold uppercase tracking-[0.1em] text-financial-yellow dark:text-financial-yellow">Best Score (AUC)</p>
                      <p className="mt-1 text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
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
                  <div className="border-b border-gray-200 p-4 dark:border-white/5">
                    <h3 className="text-base font-semibold tracking-tight text-gray-900 dark:text-white">
                      Detailed Metrics Comparison
                    </h3>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200 dark:divide-white/5">
                      <thead className="bg-gray-50 dark:bg-brand-surfaceHover">
                        <tr>
                          <th className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                            Model
                          </th>
                          <th className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                            Accuracy
                          </th>
                          <th className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                            Precision
                          </th>
                          <th className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                            Recall
                          </th>
                          <th className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                            F1 Score
                          </th>
                          <th className="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:text-gray-400">
                            AUC
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white dark:bg-brand-surface divide-y divide-gray-200 dark:divide-white/5">
                        {data.comparison.map((model, index: number) => (
                          <tr key={index} className={data.best_model?.model_type === model.model ? 'bg-green-50/50 dark:bg-financial-green/5' : 'hover:bg-gray-50 dark:hover:bg-brand-surfaceHover transition-colors'}>
                            <td className="whitespace-nowrap px-4 py-3">
                              <div className="flex items-center">
                                {data.best_model?.model_type === model.model && (
                                  <Trophy className="mr-2 h-3.5 w-3.5 text-financial-green" />
                                )}
                                <span className="text-xs font-semibold text-gray-900 dark:text-white sm:text-sm">
                                  {model.model}
                                </span>
                              </div>
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-xs text-gray-600 dark:text-gray-300 sm:text-sm">
                              {(model.accuracy * 100).toFixed(2)}%
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-xs text-gray-600 dark:text-gray-300 sm:text-sm">
                              {(model.precision * 100).toFixed(2)}%
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-xs text-gray-600 dark:text-gray-300 sm:text-sm">
                              {(model.recall * 100).toFixed(2)}%
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-xs text-gray-600 dark:text-gray-300 sm:text-sm">
                              {(model.f1_score * 100).toFixed(2)}%
                            </td>
                            <td className="whitespace-nowrap px-4 py-3 text-xs font-semibold text-brand-accent dark:text-brand-accent sm:text-sm">
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
          <div className="glass-panel flex flex-col items-center justify-center p-8 text-center">
            <div className="mb-4 rounded-full bg-gray-100 p-3 dark:bg-brand-surfaceHover">
              <BarChart3 className="h-8 w-8 text-brand-accent dark:text-brand-accent" />
            </div>
            <h3 className="mb-2 text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
              Compare ML Models
            </h3>
            <p className="mx-auto mb-5 max-w-md text-sm text-gray-500 dark:text-gray-400">
              Train and compare Logistic Regression, Random Forest, XGBoost, and Gradient Boosting models
            </p>
            <div className="inline-block rounded-md border border-gray-100 bg-gray-50 p-4 text-left dark:border-white/5 dark:bg-brand-surfaceHover">
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
                <li className="flex items-center space-x-3">
                  <span className="text-brand-accent">✓</span>
                  <span>See which model performs best for your stock</span>
                </li>
                <li className="flex items-center space-x-3">
                  <span className="text-brand-accent">✓</span>
                  <span>Compare accuracy, precision, recall, and F1 score</span>
                </li>
                <li className="flex items-center space-x-3">
                  <span className="text-brand-accent">✓</span>
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
