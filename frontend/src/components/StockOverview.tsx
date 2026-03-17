import React from 'react';
import { Building2, Landmark, Scale, Activity } from 'lucide-react';
import type { StockInfo } from '../types/stock';
import {
  formatCompactCurrency,
  formatCurrency,
  formatLargeNumber,
  formatNumber,
  formatPercent,
} from '../utils/market';

interface StockOverviewProps {
  info?: StockInfo;
  isLoading?: boolean;
}

export const StockOverview: React.FC<StockOverviewProps> = ({ info, isLoading = false }) => {
  if (isLoading) {
    return (
      <div className="glass-panel p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-7 w-2/3 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="grid grid-cols-2 gap-3">
            {Array.from({ length: 8 }).map((_, index) => (
              <div key={index} className="h-20 rounded-xl bg-gray-200 dark:bg-gray-700" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!info) {
    return null;
  }

  const locale = info.currency === 'INR' ? 'en-IN' : 'en-US';

  const items = [
    {
      label: 'Market Cap',
      value: formatCompactCurrency(info.market_cap, info.currency),
      icon: Landmark,
    },
    {
      label: 'Enterprise Value',
      value: formatCompactCurrency(info.enterprise_value, info.currency),
      icon: Building2,
    },
    {
      label: 'Current Volume',
      value: formatLargeNumber(info.current_volume, locale),
      icon: Activity,
    },
    {
      label: 'Avg Volume',
      value: formatLargeNumber(info.avg_volume, locale),
      icon: Activity,
    },
    {
      label: 'Day Range',
      value: `${formatCurrency(info.day_low, info.currency)} - ${formatCurrency(info.day_high, info.currency)}`,
      icon: Scale,
    },
    {
      label: '52W Range',
      value: `${formatCurrency(info.low_52week, info.currency)} - ${formatCurrency(info.high_52week, info.currency)}`,
      icon: Scale,
    },
    {
      label: 'Shares Out',
      value: formatLargeNumber(info.shares_outstanding, locale),
      icon: Building2,
    },
    {
      label: 'Dividend Yield',
      value: info.dividend_yield !== null && info.dividend_yield !== undefined
        ? formatPercent(info.dividend_yield * 100)
        : 'N/A',
      icon: Landmark,
    },
  ];

  return (
    <div className="glass-panel p-6">
      <div className="mb-5">
        <div className="flex flex-wrap items-center gap-2 mb-2">
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">
            {info.company_name}
          </h3>
          {info.exchange && (
            <span className="rounded-full border border-gray-200 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-gray-500 dark:border-gray-700 dark:text-gray-400">
              {info.exchange}
            </span>
          )}
          <span className="rounded-full bg-brand-accent/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-brand-accent">
            {info.currency}
          </span>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {info.sector} • {info.industry}
        </p>
        <div className="mt-4 grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-gray-200/70 bg-white/70 p-4 dark:border-gray-800 dark:bg-brand-surfaceHover">
            <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Previous Close</p>
            <p className="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
              {formatCurrency(info.previous_close, info.currency)}
            </p>
          </div>
          <div className="rounded-xl border border-gray-200/70 bg-white/70 p-4 dark:border-gray-800 dark:bg-brand-surfaceHover">
            <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Open</p>
            <p className="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
              {formatCurrency(info.open_price, info.currency)}
            </p>
          </div>
          <div className="rounded-xl border border-gray-200/70 bg-white/70 p-4 dark:border-gray-800 dark:bg-brand-surfaceHover">
            <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">P/E Ratio</p>
            <p className="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
              {info.pe_ratio !== null && info.pe_ratio !== undefined ? info.pe_ratio.toFixed(2) : 'N/A'}
            </p>
          </div>
          <div className="rounded-xl border border-gray-200/70 bg-white/70 p-4 dark:border-gray-800 dark:bg-brand-surfaceHover">
            <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Beta</p>
            <p className="mt-2 text-lg font-semibold text-gray-900 dark:text-white">
              {info.beta !== null && info.beta !== undefined ? info.beta.toFixed(2) : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <div
              key={item.label}
              className="rounded-xl border border-gray-200/70 bg-white/70 p-4 dark:border-gray-800 dark:bg-brand-surfaceHover"
            >
              <div className="mb-3 flex items-center gap-2 text-gray-500 dark:text-gray-400">
                <Icon className="h-4 w-4" />
                <span className="text-xs font-semibold uppercase tracking-[0.18em]">{item.label}</span>
              </div>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {item.value}
              </p>
            </div>
          );
        })}
      </div>

      <p className="mt-4 text-xs text-gray-500 dark:text-gray-400">
        Latest volume: {formatNumber(info.current_volume, locale)} shares
      </p>
    </div>
  );
};
