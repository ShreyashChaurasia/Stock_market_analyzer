import math
import re
import pandas as pd
import yfinance as yf
from typing import Dict, Any, Optional
from datetime import datetime
from urllib.parse import urlparse
try:
    from yfinance import EquityQuery
except Exception:  # pragma: no cover - safeguard for older yfinance versions
    EquityQuery = None

from src.core.config import settings
from src.core.logger import get_logger
from src.core.yfinance_config import configure_yfinance

logger = get_logger(__name__)

configure_yfinance()


class MarketDataService:
    """
    Service for fetching real-time market data
    """
    
    # Major market indices
    INDICES = {
        'nasdaq': '^IXIC',
        'dowjones': '^DJI',
        'nifty50': '^NSEI',
        'sensex': '^BSESN',
    }
    INDEX_CHART_SYMBOLS = {
        'nasdaq': {'symbol': '^IXIC', 'name': 'NASDAQ'},
        'dowjones': {'symbol': '^DJI', 'name': 'Dow Jones'},
        'nifty50': {'symbol': '^NSEI', 'name': 'NIFTY 50'},
        'sensex': {'symbol': '^BSESN', 'name': 'SENSEX'},
        # Backward-compatible aliases
        'nse': {'symbol': '^NSEI', 'name': 'NIFTY 50'},
        'bse': {'symbol': '^BSESN', 'name': 'SENSEX'},
    }

    PERIOD_CONFIG = {
        '1d': {'period': '1d', 'interval': '5m'},
        '1w': {'period': '5d', 'interval': '30m'},
        '1m': {'period': '1mo', 'interval': '1d'},
        '3m': {'period': '3mo', 'interval': '1d'},
        '6m': {'period': '6mo', 'interval': '1d'},
        '1y': {'period': '1y', 'interval': '1d'},
        '5y': {'period': '5y', 'interval': '1wk'},
        'all': {'period': 'max', 'interval': '1wk'},
    }

    STOCK_INFO_CACHE_TTL_SECONDS = 6 * 60 * 60
    SYMBOL_DISCOVERY_MAX_TARGET = 1200
    SYMBOL_PATTERN = re.compile(r'^[A-Z][A-Z0-9.\-]{0,14}$')
    DISCOVERY_US_QUERIES = [
        *list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        'nasdaq',
        'nyse',
        'technology stock',
        'financial stock',
        'energy stock',
        'healthcare stock',
        'consumer stock',
        'industrial stock',
        'semiconductor stock',
    ]
    DISCOVERY_INDIA_QUERIES = [
        *[f'{letter}.NS' for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'],
        'nse stock',
        'bse stock',
        'nifty 50',
        'sensex',
        'bank nifty',
        'india stock market',
    ]
    DISCOVERY_FALLBACK_TICKERS = {
        'US': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'META', 'AMZN'],
        'INDIA': ['RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'SBIN.NS'],
    }

    def __init__(self):
        self._stock_info_cache: Dict[str, Dict[str, Any]] = {}
        self._symbol_discovery_cache: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def infer_currency_from_ticker(ticker: str) -> str:
        if ticker.endswith(('.NS', '.BO')):
            return 'INR'
        return 'USD'

    def resolve_currency(self, ticker: str, info: Dict[str, Any]) -> str:
        return info.get('currency') or self.infer_currency_from_ticker(ticker)

    @staticmethod
    def _normalize_history_frame(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            if col in df.columns and hasattr(df[col], 'squeeze'):
                df[col] = df[col].squeeze()

        return df

    def _fetch_history(
        self,
        stock: yf.Ticker,
        symbol: str,
        *,
        period: Optional[str] = None,
        interval: str = '1d',
        start: Optional[str] = None,
        end: Optional[str] = None,
        auto_adjust: bool = False,
        actions: bool = False,
    ) -> pd.DataFrame:
        history_kwargs: Dict[str, Any] = {
            'interval': interval,
            'auto_adjust': auto_adjust,
            'actions': actions,
        }
        if start:
            history_kwargs['start'] = start
            if end:
                history_kwargs['end'] = end
        elif period:
            history_kwargs['period'] = period

        try:
            hist = stock.history(**history_kwargs)
            hist = self._normalize_history_frame(hist)
            if not hist.empty:
                return hist
            logger.warning(f"Ticker.history returned empty data for {symbol}: {history_kwargs}")
        except Exception as exc:
            logger.warning(
                f"Ticker.history failed for {symbol}. kwargs={history_kwargs}, error={exc}"
            )

        download_kwargs: Dict[str, Any] = {
            'tickers': symbol,
            'interval': interval,
            'auto_adjust': auto_adjust,
            'actions': actions,
            'progress': False,
            'threads': False,
        }
        if start:
            download_kwargs['start'] = start
            if end:
                download_kwargs['end'] = end
        elif period:
            download_kwargs['period'] = period

        try:
            hist = yf.download(**download_kwargs)
            hist = self._normalize_history_frame(hist)
            if not hist.empty:
                logger.info(f"Fetched history for {symbol} using yf.download fallback")
                return hist
            logger.warning(f"yf.download returned empty data for {symbol}: {download_kwargs}")
        except Exception as exc:
            logger.error(
                f"yf.download failed for {symbol}. kwargs={download_kwargs}, error={exc}",
                exc_info=True,
            )

        return pd.DataFrame()

    @staticmethod
    def _safe_info(stock: yf.Ticker, symbol: str) -> Dict[str, Any]:
        try:
            info = stock.info or {}
            if info:
                return info
        except Exception as exc:
            logger.warning(f"Ticker.info failed for {symbol}: {exc}")
        try:
            return stock.get_info() or {}
        except Exception as exc:
            logger.warning(f"Ticker.get_info failed for {symbol}: {exc}")
            return {}

    @staticmethod
    def _safe_fast_info(stock: yf.Ticker, symbol: str) -> Dict[str, Any]:
        try:
            raw_fast_info = stock.fast_info
            if not raw_fast_info:
                return {}
            if isinstance(raw_fast_info, dict):
                return raw_fast_info
            if hasattr(raw_fast_info, 'keys'):
                return {key: raw_fast_info[key] for key in raw_fast_info.keys()}
            return {}
        except Exception as exc:
            logger.warning(f"Ticker.fast_info failed for {symbol}: {exc}")
            return {}

    @staticmethod
    def _is_missing(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        if isinstance(value, str) and value.strip().upper() in {'', 'N/A', 'NA', 'NONE', 'NULL'}:
            return True
        return False

    @classmethod
    def _pick_value(cls, *values: Any) -> Any:
        for value in values:
            if cls._is_missing(value):
                continue
            return value
        return None

    @classmethod
    def _pick_numeric(cls, *values: Any) -> Optional[float]:
        value = cls._pick_value(*values)
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_finite_float(value: Any) -> Optional[float]:
        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(numeric_value):
            return None

        return numeric_value

    def _get_cached_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        cache_key = ticker.upper()
        cached_entry = self._stock_info_cache.get(cache_key)
        if not cached_entry:
            return None

        cached_at = cached_entry.get('cached_at')
        if not isinstance(cached_at, datetime):
            return None

        age_seconds = (datetime.utcnow() - cached_at).total_seconds()
        if age_seconds > self.STOCK_INFO_CACHE_TTL_SECONDS:
            self._stock_info_cache.pop(cache_key, None)
            return None

        return cached_entry.get('data')

    def _update_stock_info_cache(self, ticker: str, stock_info: Dict[str, Any]) -> None:
        cache_key = ticker.upper()
        self._stock_info_cache[cache_key] = {
            'cached_at': datetime.utcnow(),
            'data': stock_info,
        }

    @staticmethod
    def _normalize_market_scope(market: str | None) -> str:
        normalized = (market or 'ALL').strip().upper()
        if normalized not in {'ALL', 'US', 'INDIA'}:
            return 'ALL'
        return normalized

    @staticmethod
    def _is_indian_symbol(symbol: str, exchange: str | None = None) -> bool:
        exchange_upper = (exchange or '').upper()
        return (
            symbol.endswith('.NS')
            or symbol.endswith('.BO')
            or 'NSE' in exchange_upper
            or 'BSE' in exchange_upper
        )

    @classmethod
    def _is_valid_equity_symbol(cls, symbol: str, quote_type: str | None = None) -> bool:
        if not symbol or symbol.startswith('^') or '=' in symbol:
            return False
        if not cls.SYMBOL_PATTERN.match(symbol):
            return False
        normalized_quote_type = (quote_type or '').strip().upper()
        if normalized_quote_type and normalized_quote_type != 'EQUITY':
            return False
        return True

    def _get_cached_symbol_discovery(
        self,
        cache_key: str,
        ttl_seconds: int,
    ) -> Optional[list[str]]:
        cached_entry = self._symbol_discovery_cache.get(cache_key)
        if not cached_entry:
            return None

        cached_at = cached_entry.get('cached_at')
        if not isinstance(cached_at, datetime):
            return None

        age_seconds = (datetime.utcnow() - cached_at).total_seconds()
        if age_seconds > ttl_seconds:
            self._symbol_discovery_cache.pop(cache_key, None)
            return None

        symbols = cached_entry.get('symbols')
        if isinstance(symbols, list):
            return symbols
        return None

    def _cache_symbol_discovery(self, cache_key: str, symbols: list[str]) -> None:
        self._symbol_discovery_cache[cache_key] = {
            'cached_at': datetime.utcnow(),
            'symbols': symbols,
        }

    def _discover_symbols_for_market(
        self,
        market: str,
        target_count: int,
        per_query_limit: int,
    ) -> list[str]:
        if target_count <= 0:
            return []

        query_pool = (
            self.DISCOVERY_INDIA_QUERIES
            if market == 'INDIA'
            else self.DISCOVERY_US_QUERIES
        )

        discovered: list[str] = []
        seen: set[str] = set()
        max_results = max(15, min(per_query_limit * 3, 120))

        for query in query_pool:
            try:
                search = yf.Search(query, max_results=max_results)
                quotes = getattr(search, 'quotes', []) or []
            except Exception as exc:
                logger.debug(f"Ticker discovery query failed for '{query}': {exc}")
                continue

            for quote in quotes:
                symbol = str(quote.get('symbol') or '').upper().strip()
                if not symbol or symbol in seen:
                    continue

                exchange = str(
                    quote.get('exchDisp')
                    or quote.get('exchange')
                    or quote.get('exch')
                    or ''
                ).strip()
                quote_type = str(quote.get('quoteType') or '').strip()

                if not self._is_valid_equity_symbol(symbol, quote_type):
                    continue

                is_indian = self._is_indian_symbol(symbol, exchange)
                if market == 'INDIA' and not is_indian:
                    continue
                if market == 'US' and is_indian:
                    continue

                seen.add(symbol)
                discovered.append(symbol)
                if len(discovered) >= target_count:
                    return discovered

        for fallback_symbol in self.DISCOVERY_FALLBACK_TICKERS.get(market, []):
            symbol = fallback_symbol.upper().strip()
            if symbol and symbol not in seen:
                seen.add(symbol)
                discovered.append(symbol)
            if len(discovered) >= target_count:
                break

        return discovered

    def _screen_symbols_for_market(self, market: str, target_count: int) -> list[str]:
        if target_count <= 0 or EquityQuery is None:
            return []

        region_code = 'in' if market == 'INDIA' else 'us'
        query = EquityQuery('eq', ['region', region_code])
        page_size = min(250, max(50, target_count))
        max_offset = max(target_count * 3, 750)

        discovered: list[str] = []
        seen: set[str] = set()
        offset = 0

        while len(discovered) < target_count and offset < max_offset:
            try:
                response = yf.screen(
                    query,
                    offset=offset,
                    size=page_size,
                    sortField='ticker',
                    sortAsc=True,
                )
            except Exception as exc:
                logger.debug(f"Screener discovery failed for market={market} offset={offset}: {exc}")
                break

            quotes = response.get('quotes', []) or []
            if not quotes:
                break

            for quote in quotes:
                symbol = str(quote.get('symbol') or '').upper().strip()
                if not symbol or symbol in seen:
                    continue

                exchange = str(
                    quote.get('exchange')
                    or quote.get('fullExchangeName')
                    or quote.get('quoteSourceName')
                    or ''
                ).strip()
                quote_type = str(quote.get('quoteType') or '').strip()

                if not self._is_valid_equity_symbol(symbol, quote_type):
                    continue

                is_indian = self._is_indian_symbol(symbol, exchange)
                if market == 'INDIA' and not is_indian:
                    continue
                if market == 'US' and is_indian:
                    continue

                seen.add(symbol)
                discovered.append(symbol)
                if len(discovered) >= target_count:
                    break

            if len(quotes) < page_size:
                break
            offset += len(quotes)

        return discovered

    def discover_liquid_symbols(
        self,
        market: str = 'ALL',
        target_count: int = 600,
        per_query_limit: int = 35,
    ) -> list[str]:
        normalized_market = self._normalize_market_scope(market)
        bounded_target = max(50, min(int(target_count), self.SYMBOL_DISCOVERY_MAX_TARGET))
        bounded_query_limit = max(10, min(int(per_query_limit), 100))
        cache_ttl = max(300, int(settings.HIGH_CONFIDENCE_DISCOVERY_CACHE_TTL))
        cache_key = f'{normalized_market}:{bounded_target}:{bounded_query_limit}'

        cached_symbols = self._get_cached_symbol_discovery(cache_key, cache_ttl)
        if cached_symbols is not None:
            return cached_symbols

        if normalized_market == 'ALL':
            us_target = max(200, int(bounded_target * 0.7))
            india_target = max(120, bounded_target - us_target)
            us_symbols = self._screen_symbols_for_market('US', us_target)
            if len(us_symbols) < us_target:
                us_symbols.extend(
                    self._discover_symbols_for_market(
                        'US',
                        us_target - len(us_symbols),
                        bounded_query_limit,
                    )
                )

            india_symbols = self._screen_symbols_for_market('INDIA', india_target)
            if len(india_symbols) < india_target:
                india_symbols.extend(
                    self._discover_symbols_for_market(
                        'INDIA',
                        india_target - len(india_symbols),
                        bounded_query_limit,
                    )
                )

            merged: list[str] = []
            merged_seen: set[str] = set()
            for symbol in us_symbols + india_symbols:
                if symbol in merged_seen:
                    continue
                merged.append(symbol)
                merged_seen.add(symbol)
                if len(merged) >= bounded_target:
                    break

            discovered_symbols = merged
        else:
            discovered_symbols = self._screen_symbols_for_market(normalized_market, bounded_target)
            if len(discovered_symbols) < bounded_target:
                discovered_symbols.extend(
                    self._discover_symbols_for_market(
                        normalized_market,
                        bounded_target - len(discovered_symbols),
                        bounded_query_limit,
                    )
                )

            deduped_symbols: list[str] = []
            seen_symbols: set[str] = set()
            for symbol in discovered_symbols:
                normalized_symbol = symbol.upper().strip()
                if not normalized_symbol or normalized_symbol in seen_symbols:
                    continue
                deduped_symbols.append(normalized_symbol)
                seen_symbols.add(normalized_symbol)
                if len(deduped_symbols) >= bounded_target:
                    break
            discovered_symbols = deduped_symbols

        self._cache_symbol_discovery(cache_key, discovered_symbols)
        return discovered_symbols

    def _estimate_dividend_yield(self, stock: yf.Ticker, current_price: float) -> Optional[float]:
        if current_price <= 0:
            return None

        try:
            dividends = stock.dividends
            if dividends is None or dividends.empty:
                return None

            if dividends.index.tz is None:
                cutoff = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=365)
            else:
                cutoff = pd.Timestamp.now(tz=dividends.index.tz) - pd.Timedelta(days=365)

            trailing_dividends = dividends[dividends.index >= cutoff]
            annual_dividend = float(trailing_dividends.sum()) if not trailing_dividends.empty else float(dividends.tail(4).sum())
            if annual_dividend <= 0:
                return None

            return annual_dividend / current_price
        except Exception as exc:
            logger.warning(f"Dividend yield estimate failed: {exc}")
            return None

    @staticmethod
    def _normalize_website(website: Optional[str]) -> Optional[str]:
        if not website or not isinstance(website, str):
            return None

        cleaned = website.strip()
        if not cleaned:
            return None

        if not cleaned.startswith(('http://', 'https://')):
            cleaned = f'https://{cleaned}'

        return cleaned

    @staticmethod
    def _extract_domain(website: Optional[str]) -> Optional[str]:
        normalized_website = MarketDataService._normalize_website(website)
        if not normalized_website:
            return None

        parsed = urlparse(normalized_website)
        domain = (parsed.netloc or '').lower().strip()
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain or None

    def _resolve_company_logo(
        self,
        info: Dict[str, Any],
        cached_info: Optional[Dict[str, Any]],
    ) -> tuple[Optional[str], Optional[str], list[str]]:
        website = self._pick_value(
            info.get('website'),
            cached_info.get('website') if cached_info else None,
        )
        normalized_website = self._normalize_website(website)

        logo_candidates: list[str] = []

        def add_candidate(candidate: Optional[str]) -> None:
            if not candidate or not isinstance(candidate, str):
                return
            cleaned = candidate.strip()
            if (
                not cleaned
                or 'google.com/s2/favicons' in cleaned
                or cleaned in logo_candidates
            ):
                return
            logo_candidates.append(cleaned)

        domain = self._extract_domain(normalized_website)
        if domain:
            # Prefer higher-resolution brand logos first to avoid pixelated icons in UI cards.
            add_candidate(f'https://logo.clearbit.com/{domain}?size=256')
            add_candidate(f'https://logo.clearbit.com/{domain}')

        add_candidate(info.get('logo_url'))
        add_candidate(info.get('logoUrl'))
        add_candidate(cached_info.get('company_logo') if cached_info else None)

        if domain:
            add_candidate(f'https://icons.duckduckgo.com/ip3/{domain}.ico')

        primary_logo = logo_candidates[0] if logo_candidates else None
        return normalized_website, primary_logo, logo_candidates

    def search_symbols(self, query: str, market: str = 'ALL', limit: int = 8) -> list[Dict[str, Any]]:
        normalized_query = (query or '').strip()
        if not normalized_query:
            return []

        normalized_market = self._normalize_market_scope(market)
        bounded_limit = max(1, min(limit, 20))

        try:
            search = yf.Search(normalized_query, max_results=max(10, bounded_limit * 3))
            quotes = getattr(search, 'quotes', []) or []
        except Exception as exc:
            logger.warning(f"Ticker search failed for query '{normalized_query}': {exc}")
            return []

        results: list[Dict[str, Any]] = []
        seen_symbols: set[str] = set()

        for quote in quotes:
            symbol = str(quote.get('symbol') or '').upper().strip()
            if not symbol or symbol in seen_symbols:
                continue

            exchange = str(
                quote.get('exchDisp')
                or quote.get('exchange')
                or quote.get('exch')
                or ''
            ).strip()
            quote_type = str(quote.get('quoteType') or '').strip()
            is_indian = self._is_indian_symbol(symbol, exchange)

            if normalized_market == 'INDIA' and not is_indian:
                continue
            if normalized_market == 'US' and is_indian:
                continue

            seen_symbols.add(symbol)
            results.append(
                {
                    'symbol': symbol,
                    'name': (
                        quote.get('shortname')
                        or quote.get('longname')
                        or quote.get('name')
                        or symbol
                    ),
                    'exchange': exchange or None,
                    'quote_type': quote_type or None,
                }
            )

            if len(results) >= bounded_limit:
                break

        return results
    
    def get_index_data(self, index_symbol: str) -> Dict[str, Any]:
        """
        Get real-time data for a market index
        
        Args:
            index_symbol: Yahoo Finance symbol for the index
            
        Returns:
            Dictionary with current price, change, and change percent
        """
        try:
            ticker = yf.Ticker(index_symbol)
            hist = pd.DataFrame()
            for history_period in ('2d', '5d'):
                hist = self._fetch_history(
                    ticker,
                    index_symbol,
                    period=history_period,
                    interval='1d',
                    auto_adjust=False,
                )
                if not hist.empty and len(hist) >= 2:
                    break
            
            if hist.empty or len(hist) < 2:
                logger.warning(f"Insufficient data for {index_symbol}")
                return None

            close_series = pd.to_numeric(hist.get('Close'), errors='coerce').dropna()
            if len(close_series) < 2:
                logger.warning(f"Insufficient valid close data for {index_symbol}")
                return None

            current_price = self._to_finite_float(close_series.iloc[-1])
            previous_close = self._to_finite_float(close_series.iloc[-2])

            if current_price is None or previous_close is None or abs(previous_close) < 1e-12:
                logger.warning(
                    f"Invalid close values for {index_symbol}: current={current_price}, "
                    f"previous={previous_close}"
                )
                return None

            change = current_price - previous_close
            change_percent = (change / previous_close) * 100

            if not math.isfinite(change) or not math.isfinite(change_percent):
                logger.warning(
                    f"Invalid change values for {index_symbol}: "
                    f"change={change}, change_percent={change_percent}"
                )
                return None
            
            return {
                'symbol': index_symbol,
                'current_price': round(current_price, 2),
                'change': round(change, 2),
                'change_percent': round(change_percent, 2),
                'timestamp': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error fetching data for {index_symbol}: {str(e)}")
            return None
    
    def get_all_indices(self) -> Dict[str, Any]:
        """
        Get data for all major indices
        
        Returns:
            Dictionary mapping index name to its data
        """
        logger.info("Fetching all market indices data")
        
        results = {}
        for name, symbol in self.INDICES.items():
            data = self.get_index_data(symbol)
            if data:
                results[name] = data
        
        logger.info(f"Fetched data for {len(results)} indices")
        return results
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """
        Get detailed information about a stock
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with stock information
        """
        try:
            stock = yf.Ticker(ticker)
            cached_info = self._get_cached_stock_info(ticker)
            info = self._safe_info(stock, ticker)
            fast_info = self._safe_fast_info(stock, ticker)
            hist = self._fetch_history(
                stock,
                ticker,
                period='5d',
                interval='1d',
                auto_adjust=False,
            )
            
            if hist.empty:
                logger.warning(f"No historical data available for {ticker} in get_stock_info")
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            
            # Calculate 52-week high/low
            year_hist = self._fetch_history(
                stock,
                ticker,
                period='1y',
                interval='1d',
                auto_adjust=False,
            )
            high_52week = float(year_hist['High'].max()) if not year_hist.empty else None
            low_52week = float(year_hist['Low'].min()) if not year_hist.empty else None
            
            # Get volume
            average_volume_raw = self._pick_value(
                info.get('averageVolume'),
                info.get('averageDailyVolume3Month'),
                fast_info.get('threeMonthAverageVolume'),
                fast_info.get('three_month_average_volume'),
                fast_info.get('tenDayAverageVolume'),
                fast_info.get('ten_day_average_volume'),
                fast_info.get('lastVolume'),
                fast_info.get('last_volume'),
                cached_info.get('avg_volume') if cached_info else None,
            )
            if average_volume_raw is None:
                volume_series = year_hist['Volume'] if not year_hist.empty else hist['Volume']
                average_volume_raw = volume_series.mean()

            avg_volume = int(average_volume_raw) if pd.notna(average_volume_raw) else 0
            current_volume = int(hist['Volume'].iloc[-1]) if 'Volume' in hist else int(
                self._pick_numeric(fast_info.get('lastVolume'), fast_info.get('last_volume')) or 0
            )
            current_open = self._pick_numeric(
                float(hist['Open'].iloc[-1]) if 'Open' in hist else None,
                info.get('open'),
                info.get('regularMarketOpen'),
                fast_info.get('open'),
                fast_info.get('regularMarketOpen'),
                fast_info.get('last_open'),
            )
            day_high = self._pick_numeric(
                float(hist['High'].iloc[-1]) if 'High' in hist else None,
                info.get('dayHigh'),
                info.get('regularMarketDayHigh'),
                fast_info.get('dayHigh'),
                fast_info.get('day_high'),
            )
            day_low = self._pick_numeric(
                float(hist['Low'].iloc[-1]) if 'Low' in hist else None,
                info.get('dayLow'),
                info.get('regularMarketDayLow'),
                fast_info.get('dayLow'),
                fast_info.get('day_low'),
            )
            previous_close = self._pick_numeric(
                float(hist['Close'].iloc[-2]) if len(hist) > 1 else None,
                info.get('previousClose'),
                info.get('regularMarketPreviousClose'),
                fast_info.get('previousClose'),
                fast_info.get('previous_close'),
                fast_info.get('regularMarketPreviousClose'),
            )
            currency = self.resolve_currency(ticker, info)

            shares_outstanding = self._pick_numeric(
                info.get('sharesOutstanding'),
                fast_info.get('shares'),
                fast_info.get('sharesOutstanding'),
                cached_info.get('shares_outstanding') if cached_info else None,
            )
            market_cap = self._pick_numeric(
                info.get('marketCap'),
                fast_info.get('marketCap'),
                fast_info.get('market_cap'),
                cached_info.get('market_cap') if cached_info else None,
            )
            if market_cap is None and shares_outstanding is not None:
                market_cap = shares_outstanding * current_price

            enterprise_value = self._pick_numeric(
                info.get('enterpriseValue'),
                info.get('enterprise_value'),
                cached_info.get('enterprise_value') if cached_info else None,
            )
            pe_ratio = self._pick_numeric(
                info.get('trailingPE'),
                info.get('forwardPE'),
                fast_info.get('trailingPE'),
                fast_info.get('trailing_pe'),
                fast_info.get('peRatio'),
                fast_info.get('pe_ratio'),
                cached_info.get('pe_ratio') if cached_info else None,
            )
            dividend_yield = self._pick_numeric(
                info.get('dividendYield'),
                info.get('fiveYearAvgDividendYield'),
                fast_info.get('dividendYield'),
                fast_info.get('dividend_yield'),
                cached_info.get('dividend_yield') if cached_info else None,
            )
            if dividend_yield is None:
                dividend_yield = self._estimate_dividend_yield(stock, current_price)
            beta = self._pick_numeric(
                info.get('beta'),
                fast_info.get('beta'),
                cached_info.get('beta') if cached_info else None,
            )
            exchange = self._pick_value(
                info.get('fullExchangeName'),
                info.get('exchange'),
                fast_info.get('exchange'),
                cached_info.get('exchange') if cached_info else None,
            )
            website, company_logo, company_logo_candidates = self._resolve_company_logo(info, cached_info)
            
            stock_info_payload = {
                'ticker': ticker,
                'company_name': self._pick_value(
                    info.get('longName'),
                    info.get('shortName'),
                    fast_info.get('longName'),
                    fast_info.get('shortName'),
                    cached_info.get('company_name') if cached_info else None,
                    ticker,
                ),
                'sector': self._pick_value(
                    info.get('sector'),
                    cached_info.get('sector') if cached_info else None,
                    'N/A',
                ),
                'industry': self._pick_value(
                    info.get('industry'),
                    cached_info.get('industry') if cached_info else None,
                    'N/A',
                ),
                'current_price': round(current_price, 2),
                'currency': currency,
                'exchange': exchange,
                'website': website,
                'company_logo': company_logo,
                'company_logo_candidates': company_logo_candidates,
                'previous_close': round(previous_close, 2) if previous_close is not None else None,
                'open_price': round(current_open, 2) if current_open is not None else None,
                'day_high': round(day_high, 2) if day_high is not None else None,
                'day_low': round(day_low, 2) if day_low is not None else None,
                'market_cap': int(market_cap) if market_cap is not None else None,
                'enterprise_value': int(enterprise_value) if enterprise_value is not None else None,
                'pe_ratio': round(pe_ratio, 2) if pe_ratio is not None else None,
                'dividend_yield': round(dividend_yield, 4) if dividend_yield is not None else None,
                'high_52week': round(high_52week, 2) if high_52week is not None else None,
                'low_52week': round(low_52week, 2) if low_52week is not None else None,
                'avg_volume': avg_volume,
                'current_volume': current_volume,
                'shares_outstanding': int(shares_outstanding) if shares_outstanding is not None else None,
                'beta': round(beta, 4) if beta is not None else None,
                'timestamp': datetime.now().isoformat(),
            }

            self._update_stock_info_cache(ticker, stock_info_payload)
            return stock_info_payload
            
        except Exception as e:
            logger.error(f"Error fetching stock info for {ticker}: {str(e)}")
            return None
    
    def get_technical_indicators(self, ticker: str) -> Dict[str, Any]:
        """
        Calculate real technical indicators for a stock
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with technical indicators
        """
        try:
            from src.core.data_fetcher import fetch_stock_data
            from src.core.indicators import add_indicators
            
            # Fetch recent data
            df = fetch_stock_data(ticker, period='3mo')
            df = add_indicators(df)
            
            # Get latest values
            latest = df.iloc[-1]
            
            # Calculate signals
            rsi = float(latest['RSI'])
            rsi_signal = 'Buy' if rsi < 30 else 'Sell' if rsi > 70 else 'Neutral'
            
            macd = float(latest['MACD'])
            macd_signal_line = float(latest['MACD_signal'])
            macd_signal = 'Buy' if macd > macd_signal_line else 'Sell'
            
            sma_20 = float(latest['SMA_20'])
            sma_50 = df['Close'].rolling(50).mean().iloc[-1] if len(df) >= 50 else None
            current_price = float(latest['Close'])
            
            sma_signal = 'Buy' if current_price > sma_20 else 'Sell'
            
            bb_upper = float(latest['BB_high'])
            bb_lower = float(latest['BB_low'])
            
            if current_price > bb_upper:
                bb_signal = 'Overbought'
            elif current_price < bb_lower:
                bb_signal = 'Oversold'
            else:
                bb_signal = 'Neutral'
            
            return {
                'ticker': ticker,
                'rsi': {
                    'value': round(rsi, 2),
                    'signal': rsi_signal,
                },
                'macd': {
                    'value': round(macd, 4),
                    'signal_line': round(macd_signal_line, 4),
                    'signal': macd_signal,
                },
                'sma_20': {
                    'value': round(sma_20, 2),
                    'signal': sma_signal,
                },
                'sma_50': {
                    'value': round(float(sma_50), 2) if sma_50 else None,
                    'signal': 'Buy' if sma_50 and current_price > sma_50 else 'Sell',
                } if sma_50 else None,
                'bollinger_bands': {
                    'upper': round(bb_upper, 2),
                    'lower': round(bb_lower, 2),
                    'signal': bb_signal,
                },
                'timestamp': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {ticker}: {str(e)}")
            return None
    
    def get_historical_prices(self, ticker: str, period: str = '1m') -> Dict[str, Any]:
        """
        Get historical price data for charting
        
        Args:
            ticker: Stock ticker symbol
            period: Time period key (1d, 1w, 1m, 3m, 6m, 1y, 5y, all)
            
        Returns:
            Historical prices plus interval and currency metadata
        """
        try:
            stock = yf.Ticker(ticker)
            config = self.PERIOD_CONFIG.get(period, self.PERIOD_CONFIG['1m'])
            hist = self._fetch_history(
                stock,
                ticker,
                period=config['period'],
                interval=config['interval'],
                auto_adjust=False,
            )
            
            if hist.empty:
                return {
                    'interval': config['interval'],
                    'currency': self.infer_currency_from_ticker(ticker),
                    'data': [],
                }
            
            # Calculate moving averages
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            info = self._safe_info(stock, ticker)
            currency = self.resolve_currency(ticker, info)
            
            result = []
            for index, row in hist.iterrows():
                open_price = self._to_finite_float(row.get('Open'))
                high_price = self._to_finite_float(row.get('High'))
                low_price = self._to_finite_float(row.get('Low'))
                close_price = self._to_finite_float(row.get('Close'))

                if (
                    open_price is None
                    or high_price is None
                    or low_price is None
                    or close_price is None
                ):
                    continue

                sma_20 = self._to_finite_float(row.get('SMA_20'))
                sma_50 = self._to_finite_float(row.get('SMA_50'))

                volume_raw = self._to_finite_float(row.get('Volume'))
                volume_value = int(volume_raw) if volume_raw is not None else 0

                date_value = index.isoformat() if hasattr(index, 'isoformat') else str(index)

                result.append({
                    'date': date_value,
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'sma_20': round(sma_20, 2) if sma_20 is not None else None,
                    'sma_50': round(sma_50, 2) if sma_50 is not None else None,
                    'volume': volume_value,
                })

            if not result:
                logger.warning(f"No valid historical rows remained after sanitization for {ticker}")
            
            return {
                'interval': config['interval'],
                'currency': currency,
                'data': result,
            }
            
        except Exception as e:
            logger.error(f"Error fetching historical prices for {ticker}: {str(e)}")
            return {
                'interval': self.PERIOD_CONFIG.get(period, self.PERIOD_CONFIG['1m'])['interval'],
                'currency': self.infer_currency_from_ticker(ticker),
                'data': [],
            }

    def get_index_historical_prices(self, market: str, period: str = '1m') -> Dict[str, Any]:
        """
        Get historical chart data for supported market indices.

        Args:
            market: Market key (nasdaq, dowjones, nifty50, sensex) or aliases (nse, bse)
            period: Time period key (1d, 1w, 1m, 3m, 6m, 1y, 5y, all)

        Returns:
            Historical price payload with index metadata
        """
        market_key = market.lower()
        index_meta = self.INDEX_CHART_SYMBOLS.get(market_key)

        if not index_meta:
            raise ValueError(
                "Unsupported market. Use one of: nasdaq, dowjones, nifty50, sensex, nse, bse."
            )

        history = self.get_historical_prices(index_meta['symbol'], period)
        return {
            'market': market_key,
            'name': index_meta['name'],
            'symbol': index_meta['symbol'],
            'period': period,
            'interval': history['interval'],
            'currency': history['currency'],
            'data': history['data'],
        }


# Global service instance
market_service = MarketDataService()
