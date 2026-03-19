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

interface MetricCardItem {
  label: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const StockOverview: React.FC<StockOverviewProps> = ({ info, isLoading = false }) => {
  const [isLogoBroken, setIsLogoBroken] = React.useState(false);
  const [logoCandidateIndex, setLogoCandidateIndex] = React.useState(0);
  const logoCandidates = React.useMemo(() => {
    if (!info) return [];

    const optimizeCandidate = (candidate: string) => {
      let normalized = candidate.trim();
      if (normalized.includes('logo.clearbit.com') && !normalized.includes('size=')) {
        normalized = `${normalized}${normalized.includes('?') ? '&' : '?'}size=256`;
      }
      return normalized;
    };

    const merged = [info.company_logo, ...(info.company_logo_candidates || [])]
      .filter((candidate): candidate is string => Boolean(candidate))
      .map((candidate) => optimizeCandidate(candidate))
      .filter((candidate) => candidate.length > 0 && !candidate.includes('google.com/s2/favicons'));

    const uniqueCandidates = [...new Set(merged)];

    // Prefer higher-quality brand logo sources over favicon-sized ICO files.
    return uniqueCandidates.sort((a, b) => Number(a.includes('.ico')) - Number(b.includes('.ico')));
  }, [info]);
  const activeLogo = logoCandidates[logoCandidateIndex];
  const logoCandidatesKey = React.useMemo(
    () => info?.company_logo_candidates?.join('|') ?? '',
    [info?.company_logo_candidates]
  );

  React.useEffect(() => {
    setIsLogoBroken(false);
    setLogoCandidateIndex(0);
  }, [info?.ticker, info?.company_logo, logoCandidatesKey]);

  if (isLoading) {
    return (
      <div className="glass-panel p-4">
        <div className="animate-pulse space-y-3">
          <div className="h-6 w-2/3 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="grid grid-cols-2 gap-2.5">
            {Array.from({ length: 6 }).map((_, index) => (
              <div key={index} className="h-16 rounded-md bg-gray-200 dark:bg-gray-700" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!info) {
    return null;
  }

  const isMeaningful = (value: unknown) => {
    if (value === null || value === undefined) return false;
    if (typeof value === 'number') return !Number.isNaN(value);
    if (typeof value === 'string') {
      const normalized = value.trim().toUpperCase();
      return normalized !== '' && normalized !== 'N/A' && normalized !== 'NA';
    }
    return true;
  };

  const locale = info.currency === 'INR' ? 'en-IN' : 'en-US';
  const sector = isMeaningful(info.sector) ? info.sector : null;
  const industry = isMeaningful(info.industry) ? info.industry : null;
  const profileSummary = [sector, industry].filter(Boolean).join(' • ');
  const exchangeDisplayMap: Record<string, string> = {
    NMS: 'NASDAQ',
    NASDAQGS: 'NASDAQ',
    NASDAQGM: 'NASDAQ',
    NASDAQCM: 'NASDAQ',
    NYQ: 'NYSE',
  };
  const exchangeLabel = isMeaningful(info.exchange)
    ? exchangeDisplayMap[String(info.exchange)] ?? String(info.exchange)
    : null;
  const companyInitials = info.company_name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase();

  const topMetrics: MetricCardItem[] = [
    isMeaningful(info.previous_close) && {
      label: 'Previous Close',
      value: formatCurrency(info.previous_close, info.currency),
      icon: Landmark,
    },
    isMeaningful(info.open_price) && {
      label: 'Open',
      value: formatCurrency(info.open_price, info.currency),
      icon: Landmark,
    },
    isMeaningful(info.pe_ratio) && {
      label: 'P/E Ratio',
      value: info.pe_ratio.toFixed(2),
      icon: Activity,
    },
  ].filter((item): item is MetricCardItem => Boolean(item));

  const items: MetricCardItem[] = [
    isMeaningful(info.market_cap) && {
      label: 'Market Cap',
      value: formatCompactCurrency(info.market_cap, info.currency),
      icon: Landmark,
    },
    isMeaningful(info.enterprise_value) && {
      label: 'Enterprise Value',
      value: formatCompactCurrency(info.enterprise_value, info.currency),
      icon: Building2,
    },
    isMeaningful(info.current_volume) && {
      label: 'Current Volume',
      value: formatLargeNumber(info.current_volume, locale),
      icon: Activity,
    },
    isMeaningful(info.avg_volume) && {
      label: 'Avg Volume',
      value: formatLargeNumber(info.avg_volume, locale),
      icon: Activity,
    },
    isMeaningful(info.day_low) && isMeaningful(info.day_high) && {
      label: 'Day Range',
      value: `${formatCurrency(info.day_low, info.currency)} - ${formatCurrency(info.day_high, info.currency)}`,
      icon: Scale,
    },
    isMeaningful(info.low_52week) && isMeaningful(info.high_52week) && {
      label: '52W Range',
      value: `${formatCurrency(info.low_52week, info.currency)} - ${formatCurrency(info.high_52week, info.currency)}`,
      icon: Scale,
    },
    isMeaningful(info.dividend_yield) && {
      label: 'Dividend Yield',
      value: formatPercent(info.dividend_yield * 100),
      icon: Landmark,
    },
  ].filter((item): item is MetricCardItem => Boolean(item));

  return (
    <div className="glass-panel p-4">
      <div className="mb-4">
        <div className="mb-2 flex items-start gap-3">
          <div className="h-12 w-12 shrink-0 overflow-hidden rounded-md border border-gray-200/70 bg-white dark:border-gray-800 dark:bg-brand-surfaceHover">
            {activeLogo && !isLogoBroken ? (
              <img
                src={activeLogo}
                alt={`${info.company_name} logo`}
                className="h-full w-full bg-white object-contain p-1"
                loading="lazy"
                onLoad={(event) => {
                  const image = event.currentTarget;
                  const minDimension = Math.min(image.naturalWidth, image.naturalHeight);
                  if (minDimension < 48 && logoCandidateIndex < logoCandidates.length - 1) {
                    setLogoCandidateIndex((prev) => prev + 1);
                  }
                }}
                onError={() => {
                  if (logoCandidateIndex < logoCandidates.length - 1) {
                    setLogoCandidateIndex((prev) => prev + 1);
                    return;
                  }
                  setIsLogoBroken(true);
                }}
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center text-sm font-bold text-brand-accent">
                {companyInitials || info.ticker.slice(0, 2)}
              </div>
            )}
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="text-xl font-semibold tracking-tight text-gray-900 dark:text-white">
                {info.company_name}
              </h3>
              {exchangeLabel && (
                <span className="rounded-full border border-gray-200 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.1em] text-gray-500 dark:border-gray-700 dark:text-gray-400">
                  {exchangeLabel}
                </span>
              )}
              <span className="rounded-full bg-brand-accent/10 px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.1em] text-brand-accent">
                {info.currency}
              </span>
            </div>
            {profileSummary && (
              <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">
                {profileSummary}
              </p>
            )}
          </div>
        </div>

        {topMetrics.length > 0 && (
          <div className="mt-3 grid grid-cols-2 gap-2.5">
            {topMetrics.map((metric, index) => (
              <div
                key={metric.label}
                className={`rounded-md border border-gray-200/70 bg-white/70 p-3 dark:border-gray-800 dark:bg-brand-surfaceHover ${
                  topMetrics.length % 2 === 1 && index === topMetrics.length - 1 ? 'col-span-2' : ''
                }`}
              >
                <p className="text-[11px] uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">{metric.label}</p>
                <p className="mt-1.5 text-base font-semibold text-gray-900 dark:text-white">
                  {metric.value}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      {items.length > 0 && (
        <div className="grid grid-cols-2 gap-2.5">
          {items.map((item, index) => {
            const Icon = item.icon;
            return (
              <div
                key={item.label}
                className={`rounded-md border border-gray-200/70 bg-white/70 p-3 dark:border-gray-800 dark:bg-brand-surfaceHover ${
                  items.length % 2 === 1 && index === items.length - 1 ? 'col-span-2' : ''
                }`}
              >
                <div className="mb-2 flex items-center gap-1.5 text-gray-500 dark:text-gray-400">
                  <Icon className="h-3.5 w-3.5" />
                  <span className="text-[11px] font-semibold uppercase tracking-[0.12em]">{item.label}</span>
                </div>
                <p className="text-sm font-semibold text-gray-900 dark:text-white sm:text-base">
                  {item.value}
                </p>
              </div>
            );
          })}
        </div>
      )}

      {isMeaningful(info.current_volume) && (
        <p className="mt-3 text-[11px] text-gray-500 dark:text-gray-400">
          Latest volume: {formatNumber(info.current_volume, locale)} shares
        </p>
      )}
    </div>
  );
};
