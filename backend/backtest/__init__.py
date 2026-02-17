"""
Backtesting engine module.

Provides backtesting functionality for trading strategies with performance analytics.
"""

from .ma_backtest import MABacktester, run_ma_backtest

__all__ = [
    'MABacktester',
    'run_ma_backtest'
]
