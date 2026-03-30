import React, { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart as LineChartIcon } from 'lucide-react';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { stockApi } from '../services/api';
import type { HistoricalPrice, IndexHistoricalResponse, MarketIndexKey } from '../types/stock';
import { formatCurrency } from '../utils/market';
import { INDEX_CONFIG } from '../config/indices';

type IndexPeriod = '1m' | '3m' | '6m' | '1y' | '5y' | 'all';

const PERIOD_OPTIONS: Array<{ label: string; value: IndexPeriod }> = [
  { label: '1M', value: '1m' },
  { label: '3M', value: '3m' },
  { label: '6M', value: '6m' },
  { label: '1Y', value: '1y' },
  { label: '5Y', value: '5y' },
  { label: 'ALL', value: 'all' },
];

const toChartRows = (rows: HistoricalPrice[]) =>
  rows.map((item) => ({
    date: item.date,
    close: item.close,
  }));

const formatAxisDate = (dateValue: string, period: IndexPeriod) => {
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) {
    return '';
  }

  if (period === '5y' || period === '1y' || period === 'all') {
    return date.toLocaleDateString(undefined, { month: 'short', year: '2-digit' });
  }

  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
};

interface IndicesChartsProps {
  selectedIndex: MarketIndexKey | null;
}

export const IndicesCharts: React.FC<IndicesChartsProps> = ({ selectedIndex }) => {
  const [period, setPeriod] = useState<IndexPeriod>('1m');

  const selectedMeta = selectedIndex
    ? INDEX_CONFIG.find((item) => item.key === selectedIndex) ?? null
    : null;
  const resolvedIndex = selectedMeta?.key ?? null;

  const { data, isLoading, isFetching } = useQuery<IndexHistoricalResponse>({
    queryKey: ['index-historical', resolvedIndex, period],
    queryFn: () => stockApi.getIndexHistorical(resolvedIndex as MarketIndexKey, period),
    enabled: Boolean(resolvedIndex),
    staleTime: 60000,
    refetchInterval: 180000,
  });

  const chartRows = useMemo(() => toChartRows(data?.data ?? []), [data?.data]);
  const latest = chartRows.at(-1)?.close ?? null;
  const first = chartRows.at(0)?.close ?? null;
  const absoluteChange = latest !== null && first !== null ? latest - first : null;
  const percentChange = absoluteChange !== null && first ? (absoluteChange / first) * 100 : null;
  const yAxisDomain = useMemo<[number, number] | ['auto', 'auto']>(() => {
    if (chartRows.length === 0) {
      return ['auto', 'auto'];
    }

    const closes = chartRows
      .map((row) => row.close)
      .filter((value): value is number => Number.isFinite(value));
    if (closes.length === 0) {
      return ['auto', 'auto'];
    }

    const minValue = Math.min(...closes);
    const maxValue = Math.max(...closes);

    if (minValue === maxValue) {
      const flatPadding = Math.max(Math.abs(minValue) * 0.01, 1);
      return [minValue - flatPadding, maxValue + flatPadding];
    }

    const spread = maxValue - minValue;
    const proportionalPadding = Math.max(spread * 0.12, Math.abs(maxValue) * 0.002);
    return [minValue - proportionalPadding, maxValue + proportionalPadding];
  }, [chartRows]);

  const yAxisTickFormatter = (value: number) =>
    value.toLocaleString(undefined, {
      maximumFractionDigits: value < 100 ? 2 : 0,
    });

  if (!selectedMeta) {
    return null;
  }

  return (
    <div className="glass-panel p-4">
      <div className="mb-3 flex flex-col gap-2.5 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <LineChartIcon className="h-4 w-4 text-brand-accent" />
          <h3 className="text-base font-semibold text-gray-900 dark:text-white tracking-tight">
            Index Chart
          </h3>
        </div>

        <div className="flex flex-wrap gap-2">
          {PERIOD_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => setPeriod(option.value)}
              className={`rounded-md px-2.5 py-1 text-[11px] font-semibold tracking-[0.08em] transition-colors ${
                period === option.value
                  ? 'bg-brand-accent text-white shadow-sm'
                  : 'border border-gray-200 bg-white text-gray-600 hover:border-brand-accent hover:text-brand-accent dark:border-gray-800 dark:bg-brand-surfaceHover dark:text-gray-400'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-md border border-gray-200/80 bg-white/80 p-3 dark:border-gray-800 dark:bg-brand-surfaceHover">
        <div className="mb-2.5 flex flex-wrap items-center justify-between gap-2">
          <div>
            <h4 className="text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">
              {selectedMeta.label}
            </h4>
            <p className="text-[11px] text-gray-500 dark:text-gray-400">
              {data?.name ?? '--'} ({data?.symbol ?? '--'})
            </p>
          </div>
          <div className="text-right">
            <p className="text-base font-semibold text-gray-900 dark:text-white">
              {latest !== null && data ? formatCurrency(latest, data.currency) : '--'}
            </p>
            {absoluteChange !== null && percentChange !== null && (
              <p className={`text-[11px] font-semibold ${absoluteChange >= 0 ? 'text-financial-green' : 'text-financial-red'}`}>
                {absoluteChange >= 0 ? '+' : ''}
                {absoluteChange.toFixed(2)} ({absoluteChange >= 0 ? '+' : ''}
                {percentChange.toFixed(2)}%)
              </p>
            )}
          </div>
        </div>

        {isLoading && (
          <div className="animate-pulse">
            <div className="h-52 rounded bg-gray-200 dark:bg-gray-700" />
          </div>
        )}

        {!isLoading && chartRows.length === 0 && (
          <p className="py-10 text-center text-sm text-gray-500 dark:text-gray-400">No chart data available for this index.</p>
        )}

        {!isLoading && chartRows.length > 0 && (
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartRows} margin={{ top: 6, right: 4, left: -10, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#475569" opacity={0.18} />
                <XAxis
                  dataKey="date"
                  minTickGap={24}
                  tickFormatter={(value: string) => formatAxisDate(value, period)}
                  stroke="#64748b"
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  type="number"
                  domain={yAxisDomain}
                  stroke="#64748b"
                  tickLine={false}
                  axisLine={false}
                  width={72}
                  tickFormatter={yAxisTickFormatter}
                />
                <Tooltip
                  labelFormatter={(value: string) => new Date(value).toLocaleString()}
                  formatter={(value: number) => (data ? formatCurrency(value, data.currency) : value)}
                  contentStyle={{
                    backgroundColor: '#1f2937',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="close"
                  name={selectedMeta.label}
                  stroke={selectedMeta.chartColor}
                  strokeWidth={2.4}
                  dot={false}
                  activeDot={{ r: 4 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {isFetching && !isLoading && (
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">Refreshing chart...</p>
        )}
      </div>
    </div>
  );
};
