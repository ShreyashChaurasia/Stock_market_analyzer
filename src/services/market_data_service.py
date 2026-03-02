import pandas as pd
import yfinance as yf
from typing import Dict, Any, List
from datetime import datetime, timedelta

from src.core.logger import get_logger

logger = get_logger(__name__)


class MarketDataService:
    """
    Service for fetching real-time market data
    """
    
    # Major market indices
    INDICES = {
        'sp500': '^GSPC',
        'nasdaq': '^IXIC',
        'dowjones': '^DJI',
        'nifty50': '^NSEI',
        'sensex': '^BSESN',
        'ftse': '^FTSE',
        'dax': '^GDAXI',
    }
    
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
            hist = ticker.history(period='2d')
            
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
            info = stock.info
            hist = stock.history(period='5d')
            
            if hist.empty:
                return None
            
            current_price = float(hist['Close'].iloc[-1])
            
            # Calculate 52-week high/low
            year_hist = stock.history(period='1y')
            high_52week = float(year_hist['High'].max()) if not year_hist.empty else None
            low_52week = float(year_hist['Low'].min()) if not year_hist.empty else None
            
            # Get volume
            avg_volume = int(hist['Volume'].mean())
            current_volume = int(hist['Volume'].iloc[-1])
            
            return {
                'ticker': ticker,
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'current_price': round(current_price, 2),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'high_52week': round(high_52week, 2) if high_52week else None,
                'low_52week': round(low_52week, 2) if low_52week else None,
                'avg_volume': avg_volume,
                'current_volume': current_volume,
                'beta': info.get('beta'),
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
    
    def get_historical_prices(self, ticker: str, period: str = '1mo') -> List[Dict[str, Any]]:
        """
        Get historical price data for charting
        
        Args:
            ticker: Stock ticker symbol
            period: Time period (1mo, 3mo, 6mo, 1y, etc.)
            
        Returns:
            List of price data points
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            if hist.empty:
                return []
            
            # Calculate moving averages
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['SMA_50'] = hist['Close'].rolling(window=50).mean()
            
            result = []
            for index, row in hist.iterrows():
                result.append({
                    'date': index.isoformat(),
                    'close': round(float(row['Close']), 2),
                    'sma_20': round(float(row['SMA_20']), 2) if not pd.isna(row['SMA_20']) else None,
                    'sma_50': round(float(row['SMA_50']), 2) if not pd.isna(row['SMA_50']) else None,
                    'volume': int(row['Volume']),
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching historical prices for {ticker}: {str(e)}")
            return []


# Global service instance
market_service = MarketDataService()