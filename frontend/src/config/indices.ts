import type { MarketIndexKey } from '../types/stock';

export interface IndexConfigItem {
  key: MarketIndexKey;
  label: string;
  chartColor: string;
}

export const INDEX_CONFIG: IndexConfigItem[] = [
  { key: 'nasdaq', label: 'NASDAQ', chartColor: '#3B82F6' },
  { key: 'dowjones', label: 'Dow Jones', chartColor: '#10B981' },
  { key: 'nifty50', label: 'NSE (NIFTY 50)', chartColor: '#F59E0B' },
  { key: 'sensex', label: 'BSE (SENSEX)', chartColor: '#F97316' },
];
