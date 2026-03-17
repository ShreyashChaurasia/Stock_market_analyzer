import React from 'react';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
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
  const metrics = ['accuracy', 'precision', 'recall', 'f1_score', 'auc'];
  
  const data = metrics.map(metric => {
    const dataPoint: Record<string, number | string> = { metric: metric.toUpperCase() };
    models.forEach(model => {
      dataPoint[model.model] = (model[metric as keyof ModelMetrics] as number) * 100;
    });
    return dataPoint;
  });

  const colors = ['#0ea5e9', '#f59e0b', '#10b981', '#ef4444'];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
        Model Performance Comparison
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={data}>
          <PolarGrid stroke="#374151" />
          <PolarAngleAxis dataKey="metric" stroke="#6b7280" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} stroke="#6b7280" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
            }}
          />
          <Legend />
          {models.map((model, index) => (
            <Radar
              key={model.model}
              name={model.model}
              dataKey={model.model}
              stroke={colors[index % colors.length]}
              fill={colors[index % colors.length]}
              fillOpacity={0.3}
            />
          ))}
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};
