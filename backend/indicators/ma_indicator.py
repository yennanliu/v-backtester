"""
Moving Average (MA) Indicator Module

This module provides functions to calculate Simple Moving Averages (SMA)
and detect golden cross and death cross signals.

A golden cross occurs when a shorter-period MA crosses above a longer-period MA,
signaling a potential bullish trend (BUY signal).

A death cross occurs when a shorter-period MA crosses below a longer-period MA,
signaling a potential bearish trend (SELL signal).
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA) for a given period.

    Args:
        data: Pandas Series containing price data (typically closing prices)
        period: Number of periods for the moving average

    Returns:
        Pandas Series with the calculated SMA values

    Example:
        >>> prices = pd.Series([10, 11, 12, 13, 14, 15])
        >>> sma = calculate_sma(prices, period=3)
    """
    if period <= 0:
        raise ValueError("Period must be a positive integer")

    if len(data) < period:
        raise ValueError(f"Data length ({len(data)}) must be >= period ({period})")

    return data.rolling(window=period).mean()


def detect_crossover(short_ma: pd.Series, long_ma: pd.Series) -> pd.Series:
    """
    Detect when short MA crosses above long MA (golden cross - bullish signal).

    Args:
        short_ma: Short-period moving average series
        long_ma: Long-period moving average series

    Returns:
        Boolean Series where True indicates a golden cross occurred

    Example:
        Golden cross: short_ma[i-1] <= long_ma[i-1] AND short_ma[i] > long_ma[i]
    """
    # Previous values: short was below or equal to long
    prev_below = short_ma.shift(1) <= long_ma.shift(1)

    # Current values: short is above long
    curr_above = short_ma > long_ma

    # Golden cross: transition from below to above
    return prev_below & curr_above


def detect_crossunder(short_ma: pd.Series, long_ma: pd.Series) -> pd.Series:
    """
    Detect when short MA crosses below long MA (death cross - bearish signal).

    Args:
        short_ma: Short-period moving average series
        long_ma: Long-period moving average series

    Returns:
        Boolean Series where True indicates a death cross occurred

    Example:
        Death cross: short_ma[i-1] >= long_ma[i-1] AND short_ma[i] < long_ma[i]
    """
    # Previous values: short was above or equal to long
    prev_above = short_ma.shift(1) >= long_ma.shift(1)

    # Current values: short is below long
    curr_below = short_ma < long_ma

    # Death cross: transition from above to below
    return prev_above & curr_below


def generate_ma_signals(
    prices: pd.Series,
    short_period: int,
    long_period: int
) -> pd.DataFrame:
    """
    Generate buy/sell signals based on MA golden cross and death cross.

    Args:
        prices: Pandas Series containing price data (typically closing prices)
        short_period: Period for the short moving average (e.g., 50)
        long_period: Period for the long moving average (e.g., 200)

    Returns:
        DataFrame with columns:
            - 'price': Original price data
            - 'short_ma': Short-period moving average
            - 'long_ma': Long-period moving average
            - 'signal': Trading signal (1 for BUY, -1 for SELL, 0 for HOLD)
            - 'position': Current position (1 for long, 0 for neutral)

    Raises:
        ValueError: If short_period >= long_period

    Example:
        >>> signals = generate_ma_signals(close_prices, short_period=50, long_period=200)
    """
    if short_period >= long_period:
        raise ValueError(
            f"Short period ({short_period}) must be less than long period ({long_period})"
        )

    # Calculate moving averages
    short_ma = calculate_sma(prices, short_period)
    long_ma = calculate_sma(prices, long_period)

    # Detect crossovers
    golden_cross = detect_crossover(short_ma, long_ma)
    death_cross = detect_crossunder(short_ma, long_ma)

    # Create DataFrame with all information
    df = pd.DataFrame({
        'price': prices,
        'short_ma': short_ma,
        'long_ma': long_ma,
        'golden_cross': golden_cross,
        'death_cross': death_cross
    })

    # Generate signals: 1 for BUY, -1 for SELL, 0 for HOLD
    df['signal'] = 0
    df.loc[golden_cross, 'signal'] = 1  # BUY signal
    df.loc[death_cross, 'signal'] = -1  # SELL signal

    # Calculate position: 1 when holding long position, 0 when out
    # Start with no position
    df['position'] = 0

    # Forward fill positions based on signals
    position = 0
    positions = []
    for signal in df['signal']:
        if signal == 1:  # BUY signal
            position = 1
        elif signal == -1:  # SELL signal
            position = 0
        positions.append(position)

    df['position'] = positions

    return df


def get_trade_signals(signals_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract only the rows where actual trades occur (buy or sell signals).

    Args:
        signals_df: DataFrame from generate_ma_signals()

    Returns:
        DataFrame containing only rows where signal != 0

    Example:
        >>> all_signals = generate_ma_signals(prices, 50, 200)
        >>> trades = get_trade_signals(all_signals)
        >>> print(f"Total trades: {len(trades)}")
    """
    return signals_df[signals_df['signal'] != 0].copy()


def calculate_ma_cross_summary(signals_df: pd.DataFrame) -> dict:
    """
    Calculate summary statistics for MA cross signals.

    Args:
        signals_df: DataFrame from generate_ma_signals()

    Returns:
        Dictionary containing:
            - total_golden_crosses: Count of golden crosses
            - total_death_crosses: Count of death crosses
            - total_signals: Total number of trading signals
            - first_signal_date: Date of first signal
            - last_signal_date: Date of last signal

    Example:
        >>> signals = generate_ma_signals(prices, 50, 200)
        >>> summary = calculate_ma_cross_summary(signals)
        >>> print(f"Golden crosses: {summary['total_golden_crosses']}")
    """
    trades = get_trade_signals(signals_df)

    golden_crosses = (trades['signal'] == 1).sum()
    death_crosses = (trades['signal'] == -1).sum()

    summary = {
        'total_golden_crosses': int(golden_crosses),
        'total_death_crosses': int(death_crosses),
        'total_signals': len(trades),
        'first_signal_date': trades.index[0] if len(trades) > 0 else None,
        'last_signal_date': trades.index[-1] if len(trades) > 0 else None,
    }

    return summary
