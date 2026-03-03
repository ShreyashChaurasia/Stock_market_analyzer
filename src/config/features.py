"""
Feature column definitions for ML models
"""

# Base features from raw data
BASE_FEATURES = [
    'Open',
    'High',
    'Low',
    'Close',
    'Volume',
]

# Technical indicators
INDICATOR_FEATURES = [
    'SMA_20',
    'EMA_12',
    'EMA_26',
    'RSI',
    'MACD',
    'MACD_signal',
    'BB_high',
    'BB_low',
    'BB_mid',
]

# Engineered features
ENGINEERED_FEATURES = [
    'returns',
    'log_returns',
    'volatility',
    'momentum',
    'price_range',
    'volume_change',
]

# All features used for ML models
FEATURE_COLUMNS = INDICATOR_FEATURES + ENGINEERED_FEATURES

# Target variable
TARGET_COLUMN = 'Target'