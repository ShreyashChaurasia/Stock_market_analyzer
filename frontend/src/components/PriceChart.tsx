import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { format } from 'date-fns';
import { Activity, LayoutTemplate } from 'lucide-react';
import { stockApi } from '../services/api';
import type { HistoricalPrice } from '../types/stock';

interface PriceChartProps {
  ticker: string;
  period?: string;
}

type ChartType = 'area' | 'line';

export const PriceChart: React.FC<PriceChartProps> = ({ ticker, period = '1mo' }) => {
  const [chartType, setChartType] = useState<ChartType>('area');
  const [showMA, setShowMA] = useState<boolean>(false);

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
      <div className="glass-panel p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3 mb-4"></div>
          <div className="h-80 bg-gray-200 dark:bg-gray-700 rounded"></div>
        </div>
      </div>
    );
  }

  if (!data?.data || data.data.length === 0) {
    return (
      <div className="glass-panel p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          {ticker} Price Chart
        </h3>
        <p className="text-gray-500 dark:text-gray-400">No historical data available</p>
      </div>
    );
  }

  // Calculate Y-axis domain to make movement more pronounced (similar to Groww)
  const minPrice = Math.min(...data.data.map(d => d.close));
  const maxPrice = Math.max(...data.data.map(d => d.close));
  const padding = (maxPrice - minPrice) * 0.1;

  return (
    <div className="glass-panel p-6 flex flex-col h-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight flex items-center gap-2">
          {ticker} <span className="text-sm font-medium text-gray-500 dark:text-gray-400 font-mono">({period})</span>
        </h3>
        <div className="flex bg-gray-100 dark:bg-brand-surfaceHover rounded-lg p-1 border border-gray-200 dark:border-gray-800">
          <button
            onClick={() => setChartType('area')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
              chartType === 'area'
                ? 'bg-white dark:bg-brand-surface text-brand-accent shadow-sm ring-1 ring-gray-200 dark:ring-gray-700'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <LayoutTemplate className="w-4 h-4" /> Area
          </button>
          <button
            onClick={() => setChartType('line')}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${
              chartType === 'line'
                ? 'bg-white dark:bg-brand-surface text-brand-accent shadow-sm ring-1 ring-gray-200 dark:ring-gray-700'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <Activity className="w-4 h-4" /> Line
          </button>
          <div className="w-px h-6 bg-gray-300 dark:bg-gray-700 mx-1 self-center"></div>
          <button
            onClick={() => setShowMA(!showMA)}
            className={`px-3 py-1.5 rounded-md text-sm font-medium transition-all ${
              showMA
                ? 'bg-brand-accent/10 text-brand-accent ring-1 ring-brand-accent/30'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            MA
          </button>
        </div>
      </div>
      
      <div className="flex-1 w-full" style={{ minHeight: '350px' }}>
        <ResponsiveContainer width="100%" height={350}>
          {chartType === 'area' ? (
            <AreaChart data={data.data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.6} />
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" vertical={false} opacity={0.4} />
              <XAxis dataKey="date" tickFormatter={formatDate} stroke="#718096" tick={{ fill: '#718096', fontSize: 12 }} tickLine={false} axisLine={false} dy={10} />
              <YAxis domain={[minPrice - padding, maxPrice + padding]} tickFormatter={formatPrice} stroke="#718096" tick={{ fill: '#718096', fontSize: 12 }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#121212', border: '1px solid #27272A', borderRadius: '12px', color: '#fff', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                itemStyle={{ color: '#00D09C', fontWeight: 'bold' }}
                formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Price']}
                labelFormatter={(label: any) => formatDate(label as string)}
              />
              {showMA && <Legend wrapperStyle={{ paddingTop: '20px' }} />}
              <Area type="monotone" dataKey="close" stroke="#3B82F6" strokeWidth={3} fillOpacity={1} fill="url(#colorPrice)" name="Close Price" />
              {showMA && data.data[0]?.sma_20 && <Line type="monotone" dataKey="sma_20" stroke="#F59E0B" strokeWidth={2} dot={false} name="SMA 20" />}
              {showMA && data.data[0]?.sma_50 && <Line type="monotone" dataKey="sma_50" stroke="#F23645" strokeWidth={2} dot={false} name="SMA 50" />}
            </AreaChart>
          ) : (
            <LineChart data={data.data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2D3748" vertical={false} opacity={0.4} />
              <XAxis dataKey="date" tickFormatter={formatDate} stroke="#718096" tick={{ fill: '#718096', fontSize: 12 }} tickLine={false} axisLine={false} dy={10} />
              <YAxis domain={[minPrice - padding, maxPrice + padding]} tickFormatter={formatPrice} stroke="#718096" tick={{ fill: '#718096', fontSize: 12 }} tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{ backgroundColor: '#121212', border: '1px solid #27272A', borderRadius: '12px', color: '#fff', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                itemStyle={{ color: '#00D09C', fontWeight: 'bold' }}
                formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Price']}
                labelFormatter={(label: any) => formatDate(label as string)}
              />
              {showMA && <Legend wrapperStyle={{ paddingTop: '20px' }} />}
              <Line type="monotone" dataKey="close" stroke="#3B82F6" strokeWidth={3} dot={false} name="Close Price" />
              {showMA && data.data[0]?.sma_20 && <Line type="monotone" dataKey="sma_20" stroke="#F59E0B" strokeWidth={2} dot={false} name="SMA 20" />}
              {showMA && data.data[0]?.sma_50 && <Line type="monotone" dataKey="sma_50" stroke="#F23645" strokeWidth={2} dot={false} name="SMA 50" />}
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
};