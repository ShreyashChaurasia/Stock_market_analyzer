import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Line,
} from 'recharts';
import { format } from 'date-fns';
import { stockApi } from '../services/api';
import type { HistoricalPrice } from '../types/stock';

interface PriceChartProps {
  ticker: string;
  period?: string;
}

export const PriceChart: React.FC<PriceChartProps> = ({ ticker, period = '1mo' }) => {
  const { data, isLoading } = useQuery<{ data: HistoricalPrice[] }>({
    queryKey: ['historical-prices', ticker, period],
    queryFn: () => stockApi.getHistoricalPrices(ticker, period),
    enabled: !!ticker,
  });

  const formatDate = (dateStr: string) => {
    try {
      return format(new Date(dateStr), 'MMM dd');
    } catch {
      return dateStr;
    }
  };

  const formatPrice = (value: number) => {
    return `$${value.toFixed(2)}`;
  };

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-80 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (!data?.data || data.data.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          {ticker} Price Chart
        </h3>
        <p className="text-gray-500 dark:text-gray-400">No historical data available</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
        {ticker} Price Chart ({period})
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={data.data}>
          <defs>
            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            stroke="#6b7280"
          />
          <YAxis
            tickFormatter={formatPrice}
            stroke="#6b7280"
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1f2937',
              border: 'none',
              borderRadius: '8px',
              color: '#fff',
            }}
            formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Price']}
            labelFormatter={(label: any) => formatDate(label as string)}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="close"
            stroke="#0ea5e9"
            fillOpacity={1}
            fill="url(#colorPrice)"
            name="Close Price"
          />
          {data.data[0]?.sma_20 && (
            <Line
              type="monotone"
              dataKey="sma_20"
              stroke="#f59e0b"
              strokeWidth={2}
              dot={false}
              name="SMA 20"
            />
          )}
          {data.data[0]?.sma_50 && (
            <Line
              type="monotone"
              dataKey="sma_50"
              stroke="#ef4444"
              strokeWidth={2}
              dot={false}
              name="SMA 50"
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};