import React, { useEffect, useState } from 'react';
import { Search, Globe } from 'lucide-react';
import { stockApi } from '../services/api';
import type { StockSuggestion } from '../types/stock';

interface StockSearchProps {
  onSearch: (ticker: string) => void;
  loading?: boolean;
}

const usStocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA', 'AMZN', 'META'];
const indianStocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS', 'ITC.NS'];

export const StockSearch: React.FC<StockSearchProps> = ({ onSearch, loading }) => {
  const [ticker, setTicker] = useState('');
  const [market, setMarket] = useState<'US' | 'INDIA'>('US');
  const [suggestions, setSuggestions] = useState<StockSuggestion[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    const query = ticker.trim();
    if (!query) {
      setSuggestions([]);
      setIsDropdownOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setIsSearching(true);
        const marketScope = market === 'US' ? 'US' : 'INDIA';
        const response = await stockApi.searchSymbols(query, marketScope, 8);
        const nextSuggestions = response.results || [];
        setSuggestions(nextSuggestions);
        setIsDropdownOpen(nextSuggestions.length > 0);
      } catch {
        setSuggestions([]);
        setIsDropdownOpen(false);
      } finally {
        setIsSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [ticker, market]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const rawInput = ticker.trim();
    if (rawInput) {
      const exactSymbol = suggestions.find(
        (item) => item.symbol.toUpperCase() === rawInput.toUpperCase()
      );
      const tickerLikePattern = /^[A-Za-z^.=][A-Za-z0-9^.=/-]{0,14}$/;

      let finalTicker = exactSymbol
        ? exactSymbol.symbol
        : (!tickerLikePattern.test(rawInput) && suggestions.length > 0)
          ? suggestions[0].symbol
          : rawInput.toUpperCase();

      // Add .NS suffix for Indian stocks if user entered raw NSE symbol
      if (market === 'INDIA' && !finalTicker.includes('.NS') && !finalTicker.includes('.BO')) {
        finalTicker = `${finalTicker}.NS`;
      }

      setTicker(finalTicker);
      setIsDropdownOpen(false);
      onSearch(finalTicker);
    }
  };

  const handleQuickSearch = (stock: string) => {
    setTicker(stock);
    setSuggestions([]);
    setIsDropdownOpen(false);
    onSearch(stock);
  };

  const handleSuggestionSelect = (suggestion: StockSuggestion) => {
    setTicker(suggestion.symbol);
    setSuggestions([]);
    setIsDropdownOpen(false);
    onSearch(suggestion.symbol);
  };

  const currentStocks = market === 'US' ? usStocks : indianStocks;

  return (
    <div className="w-full">
      <div className="mb-4 flex justify-center gap-2.5">
        <button
          onClick={() => setMarket('US')}
          className={`flex items-center space-x-1.5 rounded-md px-3 py-2 text-sm font-semibold transition-colors ${
            market === 'US'
              ? 'bg-brand-accent text-white shadow-sm'
              : 'border border-gray-200 bg-white text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:bg-brand-surface dark:text-gray-400 dark:hover:border-gray-600'
          }`}
        >
          <Globe className="h-3.5 w-3.5" />
          <span>US Market</span>
        </button>
        <button
          onClick={() => setMarket('INDIA')}
          className={`flex items-center space-x-1.5 rounded-md px-3 py-2 text-sm font-semibold transition-colors ${
            market === 'INDIA'
              ? 'bg-brand-accent text-white shadow-sm'
              : 'border border-gray-200 bg-white text-gray-600 hover:border-gray-300 dark:border-gray-700 dark:bg-brand-surface dark:text-gray-400 dark:hover:border-gray-600'
          }`}
        >
          <Globe className="h-3.5 w-3.5" />
          <span>Indian Market (NSE)</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-2.5 sm:flex-row">
        <div className="flex-1 relative group">
          <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 transform text-gray-400 transition-colors group-focus-within:text-brand-accent" />
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            onFocus={() => setIsDropdownOpen(suggestions.length > 0)}
            onBlur={() => setTimeout(() => setIsDropdownOpen(false), 120)}
            placeholder={market === 'US' ? 'Search US stock (e.g., Apple or AAPL)' : 'Search Indian stock (e.g., Reliance or RELIANCE)'}
            className="w-full rounded-md border border-gray-200 bg-white py-2.5 pl-10 pr-3 text-sm font-medium text-gray-900 transition-colors placeholder:font-sans placeholder:text-sm placeholder:text-gray-500 focus:border-brand-accent focus:ring-1 focus:ring-brand-accent dark:border-gray-700 dark:bg-brand-surface dark:text-white dark:placeholder:text-gray-500"
            disabled={loading}
          />
          {isDropdownOpen && (
            <div className="absolute z-30 mt-1.5 w-full overflow-hidden rounded-md border border-gray-200 bg-white shadow-lg dark:border-gray-700 dark:bg-brand-surface">
              {suggestions.map((item) => (
                <button
                  type="button"
                  key={`${item.symbol}-${item.exchange ?? ''}`}
                  onMouseDown={() => handleSuggestionSelect(item)}
                  className="w-full border-b border-gray-100 px-3.5 py-2.5 text-left transition-colors last:border-b-0 hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-brand-surfaceHover"
                >
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {item.name}
                  </p>
                  <p className="mt-0.5 font-mono text-xs text-gray-500 dark:text-gray-400">
                    {item.symbol}{item.exchange ? ` • ${item.exchange}` : ''}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
        <button
          type="submit"
          disabled={loading || !ticker.trim()}
          className="rounded-md bg-brand-accent px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? 'Analyzing...' : 'Execute'}
        </button>
      </form>
      <p className="mt-2 text-center text-xs text-gray-500 dark:text-gray-400">
        {isSearching ? 'Searching symbols...' : 'Tip: search by company name or ticker'}
      </p>

      <div className="mt-5">
        <p className="mb-2 text-center text-[11px] font-semibold uppercase tracking-[0.12em] text-gray-500 dark:text-gray-400">
          Popular {market === 'US' ? 'US' : 'Indian'} Equities
        </p>
        <div className="flex flex-wrap justify-center gap-1.5">
          {currentStocks.map((stock) => (
            <button
              key={stock}
              onClick={() => handleQuickSearch(stock)}
              disabled={loading}
              className="rounded-md border border-gray-200 bg-white px-3 py-1 text-xs font-medium text-gray-700 transition-colors hover:border-brand-accent hover:text-brand-accent disabled:opacity-50 dark:border-gray-700 dark:bg-brand-surface dark:text-gray-400 dark:hover:text-brand-accent"
            >
              {stock}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
