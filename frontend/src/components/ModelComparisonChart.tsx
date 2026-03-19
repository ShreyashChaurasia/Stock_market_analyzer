import React from 'react';
import {
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Bar,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';

interface ModelMetrics {
  model: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1_score: number;
  auc: number;
}

interface ModelComparisonChartProps {
  models: ModelMetrics[];
}

export const ModelComparisonChart: React.FC<ModelComparisonChartProps> = ({ models }) => {
  const metrics: Array<{ key: keyof Omit<ModelMetrics, 'model'>; label: string }> = [
    { key: 'accuracy', label: 'Accuracy' },
    { key: 'precision', label: 'Precision' },
    { key: 'recall', label: 'Recall' },
    { key: 'f1_score', label: 'F1 Score' },
    { key: 'auc', label: 'AUC' },
  ];

  const data = metrics.map(({ key, label }) => {
    const dataPoint: Record<string, number | string> = { metric: label };
    models.forEach((model) => {
      dataPoint[model.model] = (model[key] as number) * 100;
    });
    return dataPoint;
  });

  const colors = ['#0ea5e9', '#f59e0b', '#10b981', '#ef4444'];

  return (
    <div className="glass-panel p-4">
      <h3 className="mb-3 text-base font-semibold text-gray-900 dark:text-white">
        Model Performance Comparison
      </h3>
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data} margin={{ top: 12, right: 10, left: -10, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
          <XAxis dataKey="metric" stroke="#6b7280" tickLine={false} axisLine={false} fontSize={12} />
          <YAxis
            domain={[0, 100]}
            tickFormatter={(value: number) => `${value}%`}
            stroke="#6b7280"
            tickLine={false}
            axisLine={false}
            width={38}
            fontSize={12}
          />
          <Tooltip
            formatter={(value: number | undefined) => value !== undefined ? `${value.toFixed(2)}%` : '0%'}
            contentStyle={{
              backgroundColor: '#1f2937',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
            }}
          />
          <Legend />
          {models.map((model, index) => (
            <Bar
              key={model.model}
              name={model.model}
              dataKey={model.model}
              fill={colors[index % colors.length]}
              radius={[3, 3, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
