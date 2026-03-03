import re
from datetime import datetime
from typing import Optional, Tuple

from src.core.exceptions import InvalidTickerError, InvalidDateRangeError


class TickerValidator:
    """Validates stock ticker symbols"""
    
    # Updated pattern to support Indian stocks (.NS, .BO suffix)
    TICKER_PATTERN = re.compile(r'^[A-Z]{1,10}(\.(NS|BO|NSE|BSE))?$')
    
    @classmethod
    def validate(cls, ticker: str) -> str:
        """
        Validate and normalize ticker symbol
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Normalized ticker symbol (uppercase)
            
        Raises:
            InvalidTickerError: If ticker is invalid
        """
        if not ticker:
            raise InvalidTickerError("Empty ticker")
        
        ticker = ticker.strip().upper()
        
        if not cls.TICKER_PATTERN.match(ticker):
            raise InvalidTickerError(ticker)
        
        return ticker


class DateValidator:
    """Validates date strings and ranges"""
    
    DATE_FORMAT = "%Y-%m-%d"
    
    @classmethod
    def validate_date(cls, date_str: str) -> datetime:
        """
        Validate date string format
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            
        Returns:
            datetime object
            
        Raises:
            ValidationError: If date format is invalid
        """
        try:
            return datetime.strptime(date_str, cls.DATE_FORMAT)
        except ValueError:
            from src.core.exceptions import ValidationError
            raise ValidationError(
                "date",
                f"Invalid date format: {date_str}. Expected YYYY-MM-DD"
            )
    
    @classmethod
    def validate_date_range(
        cls,
        start: Optional[str],
        end: Optional[str]
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Validate date range
        
        Args:
            start: Start date string
            end: End date string
            
        Returns:
            Tuple of (start_date, end_date) as datetime objects
            
        Raises:
            InvalidDateRangeError: If date range is invalid
        """
        start_date = cls.validate_date(start) if start else None
        end_date = cls.validate_date(end) if end else None
        
        if start_date and end_date:
            if start_date >= end_date:
                raise InvalidDateRangeError(start, end)
            
            if end_date > datetime.now():
                raise InvalidDateRangeError(start, end)
        
        return start_date, end_date


class PeriodValidator:
    """Validates period strings for yfinance"""
    
    VALID_PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    
    @classmethod
    def validate(cls, period: str) -> str:
        """
        Validate period string
        
        Args:
            period: Period string
            
        Returns:
            Validated period string
            
        Raises:
            ValidationError: If period is invalid
        """
        if period not in cls.VALID_PERIODS:
            from src.core.exceptions import ValidationError
            raise ValidationError(
                "period",
                f"Invalid period: {period}. Valid periods: {', '.join(cls.VALID_PERIODS)}"
            )
        
        return period