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
      <div className="flex justify-center gap-3 mb-6">
        <button
          onClick={() => setMarket('US')}
          className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl font-medium transition-all duration-300 ${
            market === 'US'
              ? 'bg-brand-accent text-brand-dark shadow-sm'
              : 'bg-white dark:bg-brand-surface text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-white/5 hover:border-gray-300 dark:hover:border-white/10'
          }`}
        >
          <Globe className="h-4 w-4" />
          <span className="tracking-wide">US Market</span>
        </button>
        <button
          onClick={() => setMarket('INDIA')}
          className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl font-medium transition-all duration-300 ${
            market === 'INDIA'
              ? 'bg-brand-accent text-brand-dark shadow-sm'
              : 'bg-white dark:bg-brand-surface text-gray-600 dark:text-gray-400 border border-gray-200 dark:border-white/5 hover:border-gray-300 dark:hover:border-white/10'
          }`}
        >
          <Globe className="h-4 w-4" />
          <span className="tracking-wide">Indian Market (NSE)</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative group">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 group-focus-within:text-brand-accent transition-colors h-5 w-5" />
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            onFocus={() => setIsDropdownOpen(suggestions.length > 0)}
            onBlur={() => setTimeout(() => setIsDropdownOpen(false), 120)}
            placeholder={market === 'US' ? 'Search US stock (e.g., Apple or AAPL)' : 'Search Indian stock (e.g., Reliance or RELIANCE)'}
            className="w-full pl-12 pr-4 py-4 border border-gray-200 dark:border-white/5 bg-white dark:bg-brand-surface dark:text-white rounded-xl focus:ring-1 focus:ring-brand-accent focus:border-brand-accent font-mono text-lg transition-all dark:placeholder:text-gray-500 placeholder:font-sans placeholder:text-base"
            disabled={loading}
          />
          {isDropdownOpen && (
            <div className="absolute z-30 mt-2 w-full overflow-hidden rounded-xl border border-gray-200 dark:border-white/10 bg-white dark:bg-brand-surface shadow-xl">
              {suggestions.map((item) => (
                <button
                  type="button"
                  key={`${item.symbol}-${item.exchange ?? ''}`}
                  onMouseDown={() => handleSuggestionSelect(item)}
                  className="w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-brand-surfaceHover transition-colors border-b border-gray-100 dark:border-white/5 last:border-b-0"
                >
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {item.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 font-mono mt-1">
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
          className="px-8 py-4 bg-brand-accent text-brand-dark rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed font-bold tracking-wide transition-all shadow-sm"
        >
          {loading ? 'Analyzing...' : 'Execute'}
        </button>
      </form>
      <p className="mt-3 text-xs text-center text-gray-500 dark:text-gray-400">
        {isSearching ? 'Searching symbols...' : 'Tip: search by company name or ticker'}
      </p>

      <div className="mt-8">
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wider text-center">
          Popular {market === 'US' ? 'US' : 'Indian'} Equities
        </p>
        <div className="flex flex-wrap justify-center gap-2">
          {currentStocks.map((stock) => (
            <button
              key={stock}
              onClick={() => handleQuickSearch(stock)}
              disabled={loading}
              className="px-4 py-1.5 bg-white dark:bg-brand-surface border border-gray-200 dark:border-white/5 text-gray-700 dark:text-gray-400 rounded-lg hover:border-brand-accent hover:text-brand-accent dark:hover:text-brand-accent transition-all text-sm font-mono font-medium disabled:opacity-50"
            >
              {stock}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
