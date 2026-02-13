from typing import Any, Dict, Optional


class StockAnalyzerException(Exception):
    """Base exception for Stock Analyzer application"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class DataFetchError(StockAnalyzerException):
    """Raised when stock data cannot be fetched"""
    
    def __init__(self, ticker: str, reason: str):
        message = f"Failed to fetch data for {ticker}: {reason}"
        super().__init__(message, status_code=400, details={"ticker": ticker})


class InsufficientDataError(StockAnalyzerException):
    """Raised when insufficient data is available"""
    
    def __init__(self, ticker: str, available: int, required: int):
        message = f"Insufficient data for {ticker}: {available} rows (minimum {required} required)"
        super().__init__(
            message,
            status_code=400,
            details={"ticker": ticker, "available": available, "required": required}
        )


class ModelNotFoundError(StockAnalyzerException):
    """Raised when a model file is not found"""
    
    def __init__(self, ticker: str):
        message = f"No trained model found for {ticker}"
        super().__init__(message, status_code=404, details={"ticker": ticker})


class ModelTrainingError(StockAnalyzerException):
    """Raised when model training fails"""
    
    def __init__(self, ticker: str, reason: str):
        message = f"Model training failed for {ticker}: {reason}"
        super().__init__(message, status_code=500, details={"ticker": ticker})


class ValidationError(StockAnalyzerException):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, reason: str):
        message = f"Validation error for {field}: {reason}"
        super().__init__(message, status_code=422, details={"field": field})


class InvalidTickerError(ValidationError):
    """Raised when ticker symbol is invalid"""
    
    def __init__(self, ticker: str):
        super().__init__(
            "ticker",
            f"Invalid ticker symbol: {ticker}"
        )


class InvalidDateRangeError(ValidationError):
    """Raised when date range is invalid"""
    
    def __init__(self, start: str, end: str):
        super().__init__(
            "date_range",
            f"Invalid date range: {start} to {end}"
        )