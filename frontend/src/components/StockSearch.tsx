import React, { useState } from 'react';
import { Search, Globe } from 'lucide-react';

interface StockSearchProps {
  onSearch: (ticker: string) => void;
  loading?: boolean;
}

const usStocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'AMZN', 'META'];
const indianStocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'ITC.NS'];

export const StockSearch: React.FC<StockSearchProps> = ({ onSearch, loading }) => {
  const [ticker, setTicker] = useState('');
  const [market, setMarket] = useState<'US' | 'INDIA'>('US');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (ticker.trim()) {
      let finalTicker = ticker.toUpperCase();
      // Add .NS suffix for Indian stocks if not present
      if (market === 'INDIA' && !finalTicker.includes('.NS')) {
        finalTicker = `${finalTicker}.NS`;
      }
      onSearch(finalTicker);
    }
  };

  const handleQuickSearch = (stock: string) => {
    setTicker(stock);
    onSearch(stock);
  };

  const currentStocks = market === 'US' ? usStocks : indianStocks;

  return (
    <div className="w-full">
      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setMarket('US')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            market === 'US'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          <Globe className="h-4 w-4" />
          <span>US Market</span>
        </button>
        <button
          onClick={() => setMarket('INDIA')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            market === 'INDIA'
              ? 'bg-primary-600 text-white'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          <Globe className="h-4 w-4" />
          <span>Indian Market (NSE)</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
            placeholder={market === 'US' ? 'Enter US ticker (e.g., AAPL)' : 'Enter Indian ticker (e.g., RELIANCE)'}
            className="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            disabled={loading}
          />
        </div>
        <button
          type="submit"
          disabled={loading || !ticker.trim()}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
        >
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </form>

      <div className="mt-4">
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
          Popular {market === 'US' ? 'US' : 'Indian'} stocks:
        </p>
        <div className="flex flex-wrap gap-2">
          {currentStocks.map((stock) => (
            <button
              key={stock}
              onClick={() => handleQuickSearch(stock)}
              disabled={loading}
              className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 text-sm font-medium disabled:opacity-50"
            >
              {stock}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};