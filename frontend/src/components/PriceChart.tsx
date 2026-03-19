import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  CandlestickSeries,
  ColorType,
  createChart,
  CrosshairMode,
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

type ChartTimeframe = '1d' | '1w' | '1m' | '3m' | '6m' | '1y' | '5y' | 'all';
type MainChartType = 'candles' | 'line';

const TIMEFRAMES: Array<{ label: string; value: ChartTimeframe }> = [
  { label: '1D', value: '1d' },
  { label: '1W', value: '1w' },
  { label: '1M', value: '1m' },
  { label: '3M', value: '3m' },
  { label: '6M', value: '6m' },
  { label: '1Y', value: '1y' },
  { label: '5Y', value: '5y' },
  { label: 'ALL', value: 'all' },
];

const intradayFrames = new Set<ChartTimeframe>(['1d', '1w']);

const toChartTime = (date: string) => Math.floor(new Date(date).getTime() / 1000) as UTCTimestamp;

export const PriceChart: React.FC<PriceChartProps> = ({ ticker, currency }) => {
  const [timeframe, setTimeframe] = useState<ChartTimeframe>('1m');
  const [chartType, setChartType] = useState<MainChartType>('candles');
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

    const closes = data.data.map((point) => ({
      time: toChartTime(point.date),
      value: point.close,
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
      closes,
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
      height: 360,
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
        scaleMargins: { top: 0.05, bottom: 0.05 },
      },
      timeScale: {
        borderVisible: false,
        timeVisible: isIntraday,
        secondsVisible: false,
        rightOffset: 10,
        barSpacing: isIntraday ? 10 : timeframe === 'all' ? 6 : timeframe === '5y' ? 7 : 9,
      },
      handleScale: {
        axisPressedMouseMove: {
          time: true,
          price: false,
        },
        mouseWheel: false,
        pinch: true,
      },
      handleScroll: {
        mouseWheel: false,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: false,
      },
    });

    if (chartType === 'line') {
      const lineSeries = chart.addSeries(LineSeries, {
        color: '#2563EB',
        lineWidth: 2,
        crosshairMarkerVisible: true,
        crosshairMarkerRadius: 3,
        priceLineVisible: true,
        lastValueVisible: true,
      });
      lineSeries.setData(chartSeries.closes);
    } else {
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
    }

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

    const handleWheelZoom = (event: WheelEvent) => {
      event.preventDefault();

      const logicalRange = chart.timeScale().getVisibleLogicalRange();
      if (!logicalRange) {
        return;
      }

      const currentBars = Math.max(logicalRange.to - logicalRange.from, 1);
      const minBars = isIntraday ? 15 : 20;
      const maxBars = Math.max(chartSeries.candles.length * 2, minBars + 1);
      const zoomSensitivity = 0.18;
      const zoomFactor = Math.exp((event.deltaY / 120) * zoomSensitivity);
      const nextBars = Math.min(maxBars, Math.max(minBars, currentBars * zoomFactor));
      const center = (logicalRange.from + logicalRange.to) / 2;

      chart.timeScale().setVisibleLogicalRange({
        from: center - nextBars / 2,
        to: center + nextBars / 2,
      });
    };

    container.addEventListener('wheel', handleWheelZoom, { passive: false });

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
      container.removeEventListener('wheel', handleWheelZoom);
      chart.unsubscribeCrosshairMove(handleCrosshairMove);
      chart.remove();
      chartRef.current = null;
    };
  }, [chartSeries, chartType, isDarkMode, isIntraday, latestPoint, locale, resolvedCurrency, showMA, timeframe]);

  if (isLoading) {
    return (
      <div className="glass-panel p-4">
        <div className="animate-pulse">
          <div className="mb-3 h-5 w-1/3 rounded bg-gray-200 dark:bg-gray-700" />
          <div className="h-[360px] rounded-md bg-gray-200 dark:bg-gray-700" />
        </div>
      </div>
    );
  }

  if (!data?.data?.length || !activePoint) {
    return (
      <div className="glass-panel p-4">
        <h3 className="mb-2 text-base font-semibold text-gray-900 dark:text-white">
          {ticker} Price Chart
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">No historical data available for this range.</p>
      </div>
    );
  }

  const activeIndex = data.data.findIndex((point) => point.date === activePoint.date);
  const previousClose = activeIndex > 0 ? data.data[activeIndex - 1].close : activePoint.open;
  const absoluteChange = activePoint.close - previousClose;
  const percentChange = previousClose ? (absoluteChange / previousClose) * 100 : 0;

  return (
    <div className="glass-panel p-4">
      <div className="mb-4 flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400">
            <BarChart3 className="h-4 w-4 text-brand-accent" />
            <h3 className="text-base font-semibold text-gray-900 dark:text-white tracking-tight">
              {ticker} {chartType === 'line' ? 'Line' : 'Candlestick'} Chart
            </h3>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-3">
            <div className="min-w-0">
              <p className="text-[11px] uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">Close</p>
              <p className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
                {formatCurrency(activePoint.close, resolvedCurrency)}
              </p>
            </div>
            <div className={`min-w-0 ${absoluteChange >= 0 ? 'text-financial-green' : 'text-financial-red'}`}>
              <p className="text-[11px] uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">Change</p>
              <p className="text-sm font-semibold">
                {absoluteChange >= 0 ? '+' : ''}
                {formatCurrency(absoluteChange, resolvedCurrency)} ({absoluteChange >= 0 ? '+' : ''}
                {percentChange.toFixed(2)}%)
              </p>
            </div>
            <div className="min-w-0">
              <p className="text-[11px] uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">Volume</p>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                {formatLargeNumber(activePoint.volume, locale)}
              </p>
            </div>
          </div>
          <div className="mt-2.5 flex flex-wrap gap-3 text-xs text-gray-500 dark:text-gray-400">
            <span>Open {formatCurrency(activePoint.open, resolvedCurrency)}</span>
            <span>High {formatCurrency(activePoint.high, resolvedCurrency)}</span>
            <span>Low {formatCurrency(activePoint.low, resolvedCurrency)}</span>
            <span>{formatDateTime(activePoint.date, isIntraday)}</span>
          </div>
        </div>

        <div className="flex flex-col gap-2 xl:items-end">
          <div className="flex flex-wrap gap-1.5">
            {TIMEFRAMES.map((option) => (
              <button
                key={option.value}
                onClick={() => {
                  setTimeframe(option.value);
                  setHoveredTime(null);
                }}
                className={`rounded-md px-2.5 py-1 text-[11px] font-semibold tracking-[0.08em] transition-colors ${
                  timeframe === option.value
                    ? 'bg-brand-accent text-white shadow-sm'
                    : 'border border-gray-200 bg-white text-gray-600 hover:border-brand-accent hover:text-brand-accent dark:border-gray-800 dark:bg-brand-surfaceHover dark:text-gray-400 dark:hover:text-brand-accent'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap gap-1.5">
            <button
              onClick={() => setChartType('candles')}
              className={`rounded-md px-2.5 py-1 text-xs font-semibold transition-colors ${
                chartType === 'candles'
                  ? 'bg-brand-accent text-white shadow-sm'
                  : 'border border-gray-200 bg-white text-gray-600 hover:border-brand-accent hover:text-brand-accent dark:border-gray-800 dark:bg-brand-surfaceHover dark:text-gray-400'
              }`}
            >
              Candles
            </button>
            <button
              onClick={() => setChartType('line')}
              className={`rounded-md px-2.5 py-1 text-xs font-semibold transition-colors ${
                chartType === 'line'
                  ? 'bg-brand-accent text-white shadow-sm'
                  : 'border border-gray-200 bg-white text-gray-600 hover:border-brand-accent hover:text-brand-accent dark:border-gray-800 dark:bg-brand-surfaceHover dark:text-gray-400'
              }`}
            >
              Line
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5">
            <button
              onClick={() => setShowMA((current) => !current)}
              className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold transition-colors ${
                showMA
                  ? 'bg-brand-accent/10 text-brand-accent ring-1 ring-brand-accent/30'
                  : 'border border-gray-200 bg-white text-gray-600 hover:border-brand-accent hover:text-brand-accent dark:border-gray-800 dark:bg-brand-surfaceHover dark:text-gray-400'
              }`}
            >
              <Activity className="h-3.5 w-3.5" />
              Moving Averages
            </button>
            <button
              onClick={() => chartRef.current?.timeScale().fitContent()}
              className="inline-flex items-center gap-1.5 rounded-md border border-gray-200 bg-white px-2.5 py-1 text-xs font-semibold text-gray-600 transition-colors hover:border-brand-accent hover:text-brand-accent dark:border-gray-800 dark:bg-brand-surfaceHover dark:text-gray-400"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Reset Zoom
            </button>
          </div>
          {showMA && (
            <div className="flex flex-wrap items-center gap-3 text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">
              <span className="inline-flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[#F59E0B]" />
                SMA 20
              </span>
              <span className="inline-flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-[#8B5CF6]" />
                SMA 50
              </span>
            </div>
          )}
        </div>
      </div>

      <div
        ref={chartContainerRef}
        className="h-[360px] w-full overflow-hidden rounded-md border border-gray-200/80 bg-white/80 dark:border-gray-800 dark:bg-[#111827]"
      />

      <p className="mt-3 text-xs text-gray-500 dark:text-gray-400">
        Scroll to zoom, drag to pan, and double-click to reset the visible range. Zoom now stays centered.
      </p>
    </div>
  );
};
