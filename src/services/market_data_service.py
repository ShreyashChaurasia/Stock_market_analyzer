import pandas as pd
import yfinance as yf
from typing import Dict, Any, Optional
from datetime import datetime

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
            
            current_price = float(hist['Close'].iloc[-1])
            previous_close = float(hist['Close'].iloc[-2])
            
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
            
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
            )
            market_cap = self._pick_numeric(
                info.get('marketCap'),
                fast_info.get('marketCap'),
                fast_info.get('market_cap'),
            )
            if market_cap is None and shares_outstanding is not None:
                market_cap = shares_outstanding * current_price

            enterprise_value = self._pick_numeric(
                info.get('enterpriseValue'),
                info.get('enterprise_value'),
            )
            pe_ratio = self._pick_numeric(
                info.get('trailingPE'),
                info.get('forwardPE'),
                fast_info.get('trailingPE'),
                fast_info.get('trailing_pe'),
            )
            dividend_yield = self._pick_numeric(
                info.get('dividendYield'),
                info.get('fiveYearAvgDividendYield'),
                fast_info.get('dividendYield'),
                fast_info.get('dividend_yield'),
            )
            beta = self._pick_numeric(
                info.get('beta'),
                fast_info.get('beta'),
            )
            exchange = self._pick_value(
                info.get('fullExchangeName'),
                info.get('exchange'),
                fast_info.get('exchange'),
            )
            
            return {
                'ticker': ticker,
                'company_name': self._pick_value(
                    info.get('longName'),
                    info.get('shortName'),
                    fast_info.get('longName'),
                    fast_info.get('shortName'),
                    ticker,
                ),
                'sector': self._pick_value(info.get('sector'), 'N/A'),
                'industry': self._pick_value(info.get('industry'), 'N/A'),
                'current_price': round(current_price, 2),
                'currency': currency,
                'exchange': exchange,
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
                volume_value = int(row['Volume']) if pd.notna(row.get('Volume')) else 0
                result.append({
                    'date': index.isoformat(),
                    'open': round(float(row['Open']), 2),
                    'high': round(float(row['High']), 2),
                    'low': round(float(row['Low']), 2),
                    'close': round(float(row['Close']), 2),
                    'sma_20': round(float(row['SMA_20']), 2) if not pd.isna(row['SMA_20']) else None,
                    'sma_50': round(float(row['SMA_50']), 2) if not pd.isna(row['SMA_50']) else None,
                    'volume': volume_value,
                })
            
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
