"""
Basic functionality test for MA indicator and backtest modules.

This script performs quick sanity checks without requiring network access.
"""

import pandas as pd
import numpy as np
from backend.indicators.ma_indicator import (
    calculate_sma,
    detect_crossover,
    detect_crossunder,
    generate_ma_signals
)


def test_sma_calculation():
    """Test basic SMA calculation."""
    print("Testing SMA calculation...")

    # Simple test data
    prices = pd.Series([10, 11, 12, 13, 14, 15, 16, 17, 18, 19])

    # Calculate 3-period SMA
    sma = calculate_sma(prices, period=3)

    # First two values should be NaN
    assert pd.isna(sma.iloc[0])
    assert pd.isna(sma.iloc[1])

    # Third value should be (10+11+12)/3 = 11
    assert sma.iloc[2] == 11.0

    # Fourth value should be (11+12+13)/3 = 12
    assert sma.iloc[3] == 12.0

    print("  ✓ SMA calculation working correctly")


def test_golden_cross_detection():
    """Test golden cross detection."""
    print("Testing golden cross detection...")

    # Create test data where short MA crosses above long MA
    dates = pd.date_range('2023-01-01', periods=10)

    # Short MA that crosses above long MA
    # At index 4: short (9) <= long (9), at index 5: short (10) > long (9) -> golden cross at 5
    short_ma = pd.Series([5, 6, 7, 8, 9, 10, 11, 12, 13, 14], index=dates)
    long_ma = pd.Series([10, 10, 10, 10, 9, 9, 9, 9, 9, 9], index=dates)

    # Detect crossover
    golden_cross = detect_crossover(short_ma, long_ma)

    # Should detect golden cross at index 5 (when short goes from <= to >)
    assert golden_cross.iloc[5] == True  # Crosses above at index 5

    print("  ✓ Golden cross detection working correctly")


def test_death_cross_detection():
    """Test death cross detection."""
    print("Testing death cross detection...")

    dates = pd.date_range('2023-01-01', periods=10)

    # Short MA that crosses below long MA
    # At index 4: short (11) >= long (11), at index 5: short (10) < long (11) -> death cross at 5
    short_ma = pd.Series([15, 14, 13, 12, 11, 10, 9, 8, 7, 6], index=dates)
    long_ma = pd.Series([10, 10, 10, 10, 11, 11, 11, 11, 11, 11], index=dates)

    # Detect crossunder
    death_cross = detect_crossunder(short_ma, long_ma)

    # Should detect death cross when short goes below long at index 5
    assert death_cross.iloc[5] == True  # Crosses below at index 5

    print("  ✓ Death cross detection working correctly")


def test_signal_generation():
    """Test full signal generation."""
    print("Testing signal generation...")

    # Create synthetic price data
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=300)

    # Create trending price data
    trend = np.linspace(100, 150, 300)
    noise = np.random.normal(0, 2, 300)
    prices = pd.Series(trend + noise, index=dates)

    # Generate signals with shorter periods for testing
    signals = generate_ma_signals(prices, short_period=10, long_period=30)

    # Verify DataFrame structure
    assert 'price' in signals.columns
    assert 'short_ma' in signals.columns
    assert 'long_ma' in signals.columns
    assert 'signal' in signals.columns
    assert 'position' in signals.columns

    # Verify signals are in expected range
    assert signals['signal'].isin([0, 1, -1]).all()

    # Verify positions are 0 or 1
    assert signals['position'].isin([0, 1]).all()

    print("  ✓ Signal generation working correctly")


def test_backtest_initialization():
    """Test backtester initialization."""
    print("Testing backtester initialization...")

    from backend.backtest.ma_backtest import MABacktester

    backtester = MABacktester(
        initial_capital=100000,
        commission=0.001,
        short_period=50,
        long_period=200
    )

    assert backtester.initial_capital == 100000
    assert backtester.commission == 0.001
    assert backtester.short_period == 50
    assert backtester.long_period == 200

    print("  ✓ Backtester initialization working correctly")


def test_backtest_on_synthetic_data():
    """Test backtest execution on synthetic data."""
    print("Testing backtest execution...")

    from backend.backtest.ma_backtest import MABacktester

    # Create synthetic trending data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=400)
    trend = np.linspace(100, 200, 400)
    noise = np.random.normal(0, 3, 400)
    prices = pd.Series(trend + noise, index=dates)

    # Run backtest
    backtester = MABacktester(
        initial_capital=100000,
        commission=0.001,
        short_period=20,
        long_period=50
    )

    results = backtester.run_backtest(prices)

    # Verify results structure
    assert 'trades' in results
    assert 'portfolio_values' in results
    assert 'performance_metrics' in results
    assert 'signals' in results

    # Verify metrics exist
    metrics = results['performance_metrics']
    assert 'total_return_pct' in metrics
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown_pct' in metrics
    assert 'win_rate_pct' in metrics

    print("  ✓ Backtest execution working correctly")
    print(f"    - Trades executed: {metrics['num_trades']}")
    print(f"    - Total return: {metrics['total_return_pct']:.2f}%")
    print(f"    - Win rate: {metrics['win_rate_pct']:.2f}%")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("RUNNING BASIC FUNCTIONALITY TESTS")
    print("=" * 60 + "\n")

    try:
        test_sma_calculation()
        test_golden_cross_detection()
        test_death_cross_detection()
        test_signal_generation()
        test_backtest_initialization()
        test_backtest_on_synthetic_data()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✓")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
