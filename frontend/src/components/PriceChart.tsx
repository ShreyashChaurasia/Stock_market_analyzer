import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  CandlestickSeries,
  ColorType,
  createChart,
  CrosshairMode,
  HistogramSeries,
  LineSeries,
  type IChartApi,
  type Time,
  type UTCTimestamp,
} from 'lightweight-charts';
import { Activity, BarChart3, RotateCcw } from 'lucide-react';
import { stockApi } from '../services/api';
import type { HistoricalPrice, HistoricalPricesResponse } from '../types/stock';
import { formatCurrency, formatDateTime, formatLargeNumber } from '../utils/market';
import { useThemeStore } from '../store/themeStore';

interface PriceChartProps {
  ticker: string;
  currency: string;
}

type ChartTimeframe = '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | '5y';

const TIMEFRAMES: Array<{ label: string; value: ChartTimeframe }> = [
  { label: '1D', value: '1d' },
  { label: '1W', value: '1w' },
  { label: '1M', value: '1m' },
  { label: '3M', value: '3m' },
  { label: '6M', value: '6m' },
  { label: '1Y', value: '1y' },
  { label: '5Y', value: '5y' },
];

const intradayFrames = new Set<ChartTimeframe>(['1d', '1w']);

const toChartTime = (date: string) => Math.floor(new Date(date).getTime() / 1000) as UTCTimestamp;

export const PriceChart: React.FC<PriceChartProps> = ({ ticker, currency }) => {
  const [timeframe, setTimeframe] = useState<ChartTimeframe>('1m');
  const [showMA, setShowMA] = useState(false);
  const [hoveredTime, setHoveredTime] = useState<number | null>(null);
  const chartContainerRef = useRef<HTMLDivElement | null>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const { isDarkMode } = useThemeStore();

  const { data, isLoading } = useQuery<HistoricalPricesResponse>({
    queryKey: ['historical-prices', ticker, timeframe],
    queryFn: () => stockApi.getHistoricalPrices(ticker, timeframe),
    enabled: !!ticker,
  });

  const resolvedCurrency = data?.currency ?? currency;
  const locale = resolvedCurrency === 'INR' ? 'en-IN' : 'en-US';
  const isIntraday = intradayFrames.has(timeframe);
  const latestPoint = data?.data.at(-1) ?? null;

  const chartSeries = useMemo(() => {
    if (!data?.data?.length) {
      return null;
    }

    const pointByTime = new Map<number, HistoricalPrice>();

    const candles = data.data.map((point) => {
      const time = toChartTime(point.date);
      pointByTime.set(Number(time), point);

      return {
        time,
        open: point.open,
        high: point.high,
        low: point.low,
        close: point.close,
      };
    });

    const volumes = data.data.map((point) => ({
      time: toChartTime(point.date),
      value: point.volume,
      color: point.close >= point.open ? 'rgba(34, 197, 94, 0.45)' : 'rgba(239, 68, 68, 0.45)',
    }));

    const sma20 = data.data
      .filter((point) => point.sma_20 !== null)
      .map((point) => ({
        time: toChartTime(point.date),
        value: point.sma_20 as number,
      }));

    const sma50 = data.data
      .filter((point) => point.sma_50 !== null)
      .map((point) => ({
        time: toChartTime(point.date),
        value: point.sma_50 as number,
      }));

    return {
      candles,
      volumes,
      sma20,
      sma50,
      pointByTime,
    };
  }, [data]);
  const activePoint: HistoricalPrice | null = hoveredTime !== null
    ? chartSeries?.pointByTime.get(hoveredTime) ?? latestPoint
    : latestPoint;

  useEffect(() => {
    if (!chartContainerRef.current || !chartSeries || !latestPoint) {
      return undefined;
    }

    const container = chartContainerRef.current;
    const chart = createChart(container, {
      width: container.clientWidth,
      height: 420,
      layout: {
        background: { type: ColorType.Solid, color: isDarkMode ? '#111827' : '#FFFFFF' },
        textColor: isDarkMode ? '#D1D5DB' : '#475569',
        attributionLogo: false,
      },
      grid: {
        vertLines: { color: isDarkMode ? 'rgba(71, 85, 105, 0.18)' : 'rgba(148, 163, 184, 0.24)' },
        horzLines: { color: isDarkMode ? 'rgba(71, 85, 105, 0.18)' : 'rgba(148, 163, 184, 0.24)' },
      },
      crosshair: {
        mode: CrosshairMode.MagnetOHLC,
      },
      localization: {
        locale,
        priceFormatter: (value: number) =>
          formatCurrency(value, resolvedCurrency, { maximumFractionDigits: 2 }),
      },
      rightPriceScale: {
        borderVisible: false,
        scaleMargins: { top: 0.1, bottom: 0.28 },
      },
      timeScale: {
        borderVisible: false,
        timeVisible: isIntraday,
        secondsVisible: false,
        rightOffset: 10,
        barSpacing: isIntraday ? 10 : timeframe === '5y' ? 7 : 9,
      },
      handleScale: {
        axisPressedMouseMove: {
          time: true,
          price: false,
        },
        mouseWheel: true,
        pinch: true,
      },
      handleScroll: {
        mouseWheel: true,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: false,
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#16A34A',
      downColor: '#DC2626',
      wickUpColor: '#16A34A',
      wickDownColor: '#DC2626',
      borderVisible: false,
      priceLineVisible: false,
      lastValueVisible: true,
    });
    candleSeries.setData(chartSeries.candles);

    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: 'volume' },
      priceLineVisible: false,
      lastValueVisible: false,
    });
    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.78,
        bottom: 0,
      },
    });
    volumeSeries.setData(chartSeries.volumes);

    if (showMA && chartSeries.sma20.length > 0) {
      const sma20Series = chart.addSeries(LineSeries, {
        color: '#F59E0B',
        lineWidth: 2,
        lastValueVisible: false,
        priceLineVisible: false,
      });
      sma20Series.setData(chartSeries.sma20);
    }

    if (showMA && chartSeries.sma50.length > 0) {
      const sma50Series = chart.addSeries(LineSeries, {
        color: '#8B5CF6',
        lineWidth: 2,
        lastValueVisible: false,
        priceLineVisible: false,
      });
      sma50Series.setData(chartSeries.sma50);
    }

    chart.timeScale().fitContent();
    chartRef.current = chart;

    const handleCrosshairMove = (param: { time?: Time }) => {
      if (!param.time || typeof param.time !== 'number') {
        setHoveredTime(null);
        return;
      }

      setHoveredTime(Number(param.time));
    };

    chart.subscribeCrosshairMove(handleCrosshairMove);

    const resizeObserver = new ResizeObserver((entries) => {
      const entry = entries[0];
      if (!entry) {
        return;
      }

      chart.applyOptions({ width: entry.contentRect.width });
    });
    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      chart.unsubscribeCrosshairMove(handleCrosshairMove);
      chart.remove();
      chartRef.current = null;
    };
  }, [chartSeries, isDarkMode, isIntraday, latestPoint, locale, resolvedCurrency, showMA, timeframe]);

  if (isLoading) {
    return (
      <div className="glass-panel p-6">
        <div className="animate-pulse">
          <div className="mb-4 h-6 w-1/3 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-[420px] rounded-2xl bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
    );
  }

  if (!data?.data?.length || !activePoint) {
    return (
      <div className="glass-panel p-6">
        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
          {ticker} Price Chart
        </h3>
        <p className="text-gray-500 dark:text-gray-400">No historical data available for this range.</p>
      </div>
    );
  }

  const activeIndex = data.data.findIndex((point) => point.date === activePoint.date);
  const previousClose = activeIndex > 0 ? data.data[activeIndex - 1].close : activePoint.open;
  const absoluteChange = activePoint.close - previousClose;
  const percentChange = previousClose ? (absoluteChange / previousClose) * 100 : 0;

  return (
    <div className="glass-panel p-6">
      <div className="mb-5 flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
            <BarChart3 className="h-5 w-5 text-brand-accent" />
            <h3 className="text-xl font-bold text-gray-900 dark:text-white tracking-tight">
              {ticker} Candlestick Chart
            </h3>
          </div>
          <div className="mt-4 flex flex-wrap items-end gap-x-5 gap-y-2">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Close</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {formatCurrency(activePoint.close, resolvedCurrency)}
              </p>
            </div>
            <div className={absoluteChange >= 0 ? 'text-financial-green' : 'text-financial-red'}>
              <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Change</p>
              <p className="text-lg font-semibold">
                {absoluteChange >= 0 ? '+' : ''}
                {formatCurrency(absoluteChange, resolvedCurrency)} ({absoluteChange >= 0 ? '+' : ''}
                {percentChange.toFixed(2)}%)
              </p>
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-gray-500 dark:text-gray-400">Volume</p>
              <p className="text-lg font-semibold text-gray-900 dark:text-white">
                {formatLargeNumber(activePoint.volume, locale)}
              </p>
            </div>
          </div>
          <div className="mt-3 flex flex-wrap gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span>Open {formatCurrency(activePoint.open, resolvedCurrency)}</span>
            <span>High {formatCurrency(activePoint.high, resolvedCurrency)}</span>
            <span>Low {formatCurrency(activePoint.low, resolvedCurrency)}</span>
            <span>{formatDateTime(activePoint.date, isIntraday)}</span>
          </div>
        </div>

        <div className="flex flex-col gap-3 xl:items-end">
          <div className="flex flex-wrap gap-2">
            {TIMEFRAMES.map((option) => (
              <button
                key={option.value}
                onClick={() => {
                  setTimeframe(option.value);
                  setHoveredTime(null);
                }}
                className={`rounded-xl px-3 py-2 text-sm font-semibold tracking-wide transition-all ${
                  timeframe === option.value
                    ? 'bg-brand-accent text-brand-dark shadow-sm'
                    : 'border border-gray-200 bg-white text-gray-600 hover:border-brand-accent hover:text-brand-accent dark:border-gray-800 dark:bg-brand-surfaceHover dark:text-gray-400 dark:hover:text-brand-accent'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setShowMA((current) => !current)}
              className={`inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-semibold transition-all ${
                showMA
                  ? 'bg-brand-accent/10 text-brand-accent ring-1 ring-brand-accent/30'
                  : 'border border-gray-200 bg-white text-gray-600 hover:border-brand-accent hover:text-brand-accent dark:border-gray-800 dark:bg-brand-surfaceHover dark:text-gray-400'
              }`}
            >
              <Activity className="h-4 w-4" />
              Moving Averages
            </button>
            <button
              onClick={() => chartRef.current?.timeScale().fitContent()}
              className="inline-flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-3 py-2 text-sm font-semibold text-gray-600 transition-all hover:border-brand-accent hover:text-brand-accent dark:border-gray-800 dark:bg-brand-surfaceHover dark:text-gray-400"
            >
              <RotateCcw className="h-4 w-4" />
              Reset Zoom
            </button>
          </div>
        </div>
      </div>

      <div
        ref={chartContainerRef}
        className="h-[420px] w-full overflow-hidden rounded-2xl border border-gray-200/80 bg-white/80 dark:border-gray-800 dark:bg-[#111827]"
      />

      <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
        Scroll to zoom, drag to pan, and double-click to reset the visible range.
      </p>
    </div>
  );
};
