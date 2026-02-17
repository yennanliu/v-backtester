"""
Pytest configuration and shared fixtures for the test suite.

This module provides reusable test data and fixtures for all tests.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


@pytest.fixture
def simple_price_data():
    """
    Simple price series for basic MA calculations.

    Returns 10 consecutive integers as prices.
    """
    return pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19])


@pytest.fixture
def golden_cross_data():
    """
    Synthetic data designed to produce a golden cross.

    Creates a scenario where short MA crosses above long MA.
    Pattern: downtrend -> uptrend causing golden cross
    """
    # Create prices that will generate a golden cross
    # Start with downtrend, then sharp uptrend
    prices = [100] * 10  # Flat period
    prices += list(range(95, 85, -1))  # Downtrend: 95, 94, ..., 86
    prices += list(range(86, 120, 2))  # Sharp uptrend: 86, 88, 90, ..., 118
    prices += [120] * 10  # Flat period at top

    dates = pd.date_range(start='2023-01-01', periods=len(prices), freq='D')
    return pd.Series(prices, index=dates, dtype=float)


@pytest.fixture
def death_cross_data():
    """
    Synthetic data designed to produce a death cross.

    Creates a scenario where short MA crosses below long MA.
    Pattern: uptrend -> downtrend causing death cross
    """
    # Create prices that will generate a death cross
    # Start with uptrend, then sharp downtrend
    prices = [50] * 10  # Flat period
    prices += list(range(51, 81, 2))  # Uptrend: 51, 53, 55, ..., 79
    prices += list(range(80, 40, -2))  # Sharp downtrend: 80, 78, 76, ..., 42
    prices += [40] * 10  # Flat period at bottom

    dates = pd.date_range(start='2023-01-01', periods=len(prices), freq='D')
    return pd.Series(prices, index=dates, dtype=float)


@pytest.fixture
def multi_cross_data():
    """
    Data with multiple golden and death crosses.

    Creates oscillating price pattern with several crossovers.
    """
    prices = []
    # Create sine wave pattern to generate multiple crosses
    for i in range(200):
        price = 100 + 20 * np.sin(i / 10) + np.random.normal(0, 1)
        prices.append(price)

    dates = pd.date_range(start='2023-01-01', periods=len(prices), freq='D')
    return pd.Series(prices, index=dates, dtype=float)


@pytest.fixture
def flat_price_data():
    """
    Flat price data with no trend.

    All prices are identical - should not generate any crosses.
    """
    prices = [100.0] * 100
    dates = pd.date_range(start='2023-01-01', periods=len(prices), freq='D')
    return pd.Series(prices, index=dates, dtype=float)


@pytest.fixture
def realistic_backtest_data():
    """
    More realistic price data for backtest integration tests.

    Simulates realistic market behavior with trends and volatility.
    """
    np.random.seed(42)  # For reproducibility

    # Generate 500 days of price data with realistic characteristics
    days = 500
    initial_price = 100.0
    prices = [initial_price]

    for i in range(days - 1):
        # Random walk with drift and volatility
        drift = 0.0005  # Slight upward drift
        volatility = 0.02  # 2% daily volatility
        change = drift + volatility * np.random.randn()
        new_price = prices[-1] * (1 + change)
        prices.append(max(new_price, 1.0))  # Prevent negative prices

    dates = pd.date_range(start='2022-01-01', periods=days, freq='D')
    return pd.Series(prices, index=dates, dtype=float)


@pytest.fixture
def known_ma_values():
    """
    Price data with known/expected MA values for validation.

    Simple sequence where we can easily calculate expected MAs.
    """
    # Prices: [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    prices = pd.Series(range(10, 101, 10), dtype=float)

    # Expected 3-period SMA:
    # Index 0-1: NaN (not enough data)
    # Index 2: (10+20+30)/3 = 20
    # Index 3: (20+30+40)/3 = 30
    # Index 4: (30+40+50)/3 = 40
    # etc.

    return prices


@pytest.fixture
def edge_case_data():
    """
    Edge case data for testing error handling.

    Returns various problematic data scenarios.
    """
    return {
        'empty': pd.Series([], dtype=float),
        'single_value': pd.Series([100.0]),
        'two_values': pd.Series([100.0, 101.0]),
        'with_nan': pd.Series([100.0, 101.0, np.nan, 103.0, 104.0]),
        'with_inf': pd.Series([100.0, 101.0, np.inf, 103.0, 104.0]),
        'negative': pd.Series([-10.0, -20.0, -30.0, -40.0, -50.0]),
        'zero': pd.Series([0.0] * 10)
    }


@pytest.fixture
def sample_trades():
    """
    Sample trade data for testing performance metrics.

    Returns a list of trades with known outcomes.
    """
    dates = pd.date_range(start='2023-01-01', periods=6, freq='D')

    return [
        # First trade: Buy at 100, Sell at 110 (WIN)
        {'date': dates[0], 'type': 'BUY', 'price': 100.0, 'shares': 100, 'value': 10010.0},
        {'date': dates[1], 'type': 'SELL', 'price': 110.0, 'shares': 100, 'value': 10989.0},

        # Second trade: Buy at 105, Sell at 95 (LOSS)
        {'date': dates[2], 'type': 'BUY', 'price': 105.0, 'shares': 100, 'value': 10510.5},
        {'date': dates[3], 'type': 'SELL', 'price': 95.0, 'shares': 100, 'value': 9499.5},

        # Third trade: Buy at 90, Sell at 100 (WIN)
        {'date': dates[4], 'type': 'BUY', 'price': 90.0, 'shares': 100, 'value': 9009.0},
        {'date': dates[5], 'type': 'SELL', 'price': 100.0, 'shares': 100, 'value': 9990.0},
    ]


@pytest.fixture
def portfolio_values_data():
    """
    Sample portfolio values for drawdown and return calculations.
    """
    dates = pd.date_range(start='2023-01-01', periods=10, freq='D')

    # Portfolio values: peak at index 3, drawdown to index 7
    values = [100000, 105000, 110000, 115000, 112000, 108000, 105000, 102000, 108000, 112000]

    return pd.DataFrame({
        'portfolio_value': values,
        'cash': [50000] * 10,
        'shares': [500] * 10,
        'price': [100.0] * 10
    }, index=dates)
