"""
Feature column definitions for ML models
"""

# Technical indicators
INDICATOR_FEATURES = [
    'SMA_20',
    'SMA_50',
    'EMA_20',
    'RSI',
    'MACD',
    'MACD_signal',
    'BB_high',
    'BB_low',
]

# Engineered features
ENGINEERED_FEATURES = [
    'Return_1d',
    'Return_5d',
    'Volatility_20',
    'Trend',
    'Trend_Slope',
]

# All features
FEATURE_COLUMNS = INDICATOR_FEATURES + ENGINEERED_FEATURES

# Target
TARGET_COLUMN = 'Target'