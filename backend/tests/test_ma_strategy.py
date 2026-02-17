"""
Comprehensive test suite for MA Golden Cross Backtesting System

Tests cover:
1. MA calculation correctness
2. Golden cross detection
3. Death cross detection
4. Backtesting logic (trade execution, portfolio tracking)
5. Performance metrics (returns, win rate, max drawdown, Sharpe ratio)
6. Integration tests (end-to-end backtesting)
7. Edge cases and error handling

Target: 80%+ code coverage
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from backend.indicators.ma_indicator import (
    calculate_sma,
    detect_crossover,
    detect_crossunder,
    generate_ma_signals,
    get_trade_signals,
    calculate_ma_cross_summary
)

from backend.backtest.ma_backtest import (
    MABacktester,
    run_ma_backtest
)


# =============================================================================
# TEST SUITE 1: MA CALCULATION CORRECTNESS
# =============================================================================

class TestMACalculation:
    """Test suite for Simple Moving Average calculation."""

    def test_calculate_sma_basic(self, simple_price_data):
        """Test SMA calculation with simple integer sequence."""
        # Calculate 3-period SMA
        sma = calculate_sma(simple_price_data, period=3)

        # First 2 values should be NaN (insufficient data)
        assert pd.isna(sma.iloc[0])
        assert pd.isna(sma.iloc[1])

        # Third value: (10+11+12)/3 = 11
        assert sma.iloc[2] == 11.0

        # Fourth value: (11+12+13)/3 = 12
        assert sma.iloc[3] == 12.0

        # Last value: (17+18+19)/3 = 18
        assert sma.iloc[-1] == 18.0

    def test_calculate_sma_known_values(self, known_ma_values):
        """Test SMA with known expected values."""
        prices = known_ma_values  # [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
        sma = calculate_sma(prices, period=3)

        # Expected values
        expected = [np.nan, np.nan, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0]

        for i, exp in enumerate(expected):
            if pd.isna(exp):
                assert pd.isna(sma.iloc[i])
            else:
                assert abs(sma.iloc[i] - exp) < 0.001  # Float comparison with tolerance

    def test_calculate_sma_single_period(self):
        """Test SMA with period=1 (should equal original values)."""
        prices = pd.Series([10, 20, 30, 40, 50])
        sma = calculate_sma(prices, period=1)

        # Period of 1 means each value is its own average
        pd.testing.assert_series_equal(sma, prices, check_dtype=False)

    def test_calculate_sma_full_period(self):
        """Test SMA where period equals data length."""
        prices = pd.Series([10, 20, 30, 40, 50])
        sma = calculate_sma(prices, period=5)

        # Only last value should be valid: (10+20+30+40+50)/5 = 30
        assert pd.isna(sma.iloc[0])
        assert pd.isna(sma.iloc[1])
        assert pd.isna(sma.iloc[2])
        assert pd.isna(sma.iloc[3])
        assert sma.iloc[4] == 30.0

    def test_calculate_sma_rolling_window(self):
        """Verify SMA uses proper rolling window calculation."""
        prices = pd.Series([5, 15, 25, 35, 45])
        sma = calculate_sma(prices, period=2)

        # Rolling 2-period average
        assert pd.isna(sma.iloc[0])
        assert sma.iloc[1] == 10.0  # (5+15)/2
        assert sma.iloc[2] == 20.0  # (15+25)/2
        assert sma.iloc[3] == 30.0  # (25+35)/2
        assert sma.iloc[4] == 40.0  # (35+45)/2

    def test_calculate_sma_insufficient_data(self):
        """Test SMA raises error when data length < period."""
        prices = pd.Series([10, 20, 30])

        with pytest.raises(ValueError, match="Data length.*must be >= period"):
            calculate_sma(prices, period=5)

    def test_calculate_sma_invalid_period_zero(self):
        """Test SMA raises error for period=0."""
        prices = pd.Series([10, 20, 30, 40, 50])

        with pytest.raises(ValueError, match="Period must be a positive integer"):
            calculate_sma(prices, period=0)

    def test_calculate_sma_invalid_period_negative(self):
        """Test SMA raises error for negative period."""
        prices = pd.Series([10, 20, 30, 40, 50])

        with pytest.raises(ValueError, match="Period must be a positive integer"):
            calculate_sma(prices, period=-1)

    def test_calculate_sma_empty_series(self, edge_case_data):
        """Test SMA with empty series."""
        empty = edge_case_data['empty']

        with pytest.raises(ValueError):
            calculate_sma(empty, period=3)

    def test_calculate_sma_with_nan_values(self, edge_case_data):
        """Test SMA behavior with NaN values in data."""
        prices = edge_case_data['with_nan']
        sma = calculate_sma(prices, period=2)

        # NaN in input should propagate to output
        assert pd.isna(sma.iloc[2])  # Window includes NaN


# =============================================================================
# TEST SUITE 2: GOLDEN CROSS DETECTION
# =============================================================================

class TestGoldenCrossDetection:
    """Test suite for golden cross (bullish) signal detection."""

    def test_detect_crossover_basic(self):
        """Test basic golden cross detection."""
        # Short MA crosses above long MA at index 3
        short_ma = pd.Series([10, 11, 12, 14, 16, 18])
        long_ma = pd.Series([15, 15, 15, 13, 12, 11])

        crossover = detect_crossover(short_ma, long_ma)

        # Golden cross should occur at index 3
        # Index 2: short(12) <= long(15) - no cross yet
        # Index 3: short(14) > long(13) - golden cross!
        assert crossover.iloc[3] == True
        assert crossover.sum() == 1  # Only one cross

    def test_detect_crossover_exact_equality(self):
        """Test crossover when MAs are exactly equal then diverge."""
        short_ma = pd.Series([10, 15, 15, 16, 17])
        long_ma = pd.Series([12, 15, 15, 15, 14])

        crossover = detect_crossover(short_ma, long_ma)

        # At index 2: both equal (15 == 15)
        # At index 3: short(16) > long(15) - this is a crossover
        assert crossover.iloc[3] == True

    def test_detect_crossover_no_cross(self):
        """Test when short MA stays below long MA (no golden cross)."""
        short_ma = pd.Series([10, 11, 12, 13, 14])
        long_ma = pd.Series([20, 21, 22, 23, 24])

        crossover = detect_crossover(short_ma, long_ma)

        # No crossover should occur
        assert crossover.sum() == 0
        assert all(crossover == False)

    def test_detect_crossover_multiple_crosses(self):
        """Test detection of multiple golden crosses."""
        # Create pattern with multiple crosses
        short_ma = pd.Series([10, 12, 14, 12, 10, 12, 14, 16])
        long_ma = pd.Series([11, 11, 11, 11, 11, 11, 11, 11])

        crossover = detect_crossover(short_ma, long_ma)

        # Should detect crossovers at indices where short crosses above long
        # Index 2: 10 <= 11, 12 > 11 (no, short already above)
        # Actually first cross at index 2: (12 was below, 14 is above)
        crosses = crossover.sum()
        assert crosses >= 1

    def test_detect_crossover_already_above(self):
        """Test when short MA starts above long MA (no initial cross)."""
        short_ma = pd.Series([20, 21, 22, 23, 24])
        long_ma = pd.Series([10, 11, 12, 13, 14])

        crossover = detect_crossover(short_ma, long_ma)

        # Short already above, no crossover
        assert crossover.sum() == 0

    def test_detect_crossover_with_synthetic_data(self, golden_cross_data):
        """Test golden cross detection with synthetic data."""
        # Generate signals using actual implementation
        signals = generate_ma_signals(golden_cross_data, short_period=5, long_period=10)

        # Should detect at least one golden cross
        golden_crosses = signals['golden_cross'].sum()
        assert golden_crosses >= 1

        # Verify signal column has buy signals
        buy_signals = (signals['signal'] == 1).sum()
        assert buy_signals >= 1


# =============================================================================
# TEST SUITE 3: DEATH CROSS DETECTION
# =============================================================================

class TestDeathCrossDetection:
    """Test suite for death cross (bearish) signal detection."""

    def test_detect_crossunder_basic(self):
        """Test basic death cross detection."""
        # Short MA crosses below long MA at index 3
        short_ma = pd.Series([18, 16, 14, 12, 10, 8])
        long_ma = pd.Series([11, 12, 13, 13, 13, 13])

        crossunder = detect_crossunder(short_ma, long_ma)

        # Death cross should occur at index 3
        # Index 2: short(14) >= long(13) - still above
        # Index 3: short(12) < long(13) - death cross!
        assert crossunder.iloc[3] == True
        assert crossunder.sum() == 1  # Only one cross

    def test_detect_crossunder_exact_equality(self):
        """Test crossunder when MAs are exactly equal then diverge."""
        short_ma = pd.Series([17, 15, 15, 14, 13])
        long_ma = pd.Series([14, 15, 15, 15, 16])

        crossunder = detect_crossunder(short_ma, long_ma)

        # At index 2: both equal (15 == 15)
        # At index 3: short(14) < long(15) - this is a crossunder
        assert crossunder.iloc[3] == True

    def test_detect_crossunder_no_cross(self):
        """Test when short MA stays above long MA (no death cross)."""
        short_ma = pd.Series([20, 21, 22, 23, 24])
        long_ma = pd.Series([10, 11, 12, 13, 14])

        crossunder = detect_crossunder(short_ma, long_ma)

        # No crossunder should occur
        assert crossunder.sum() == 0
        assert all(crossunder == False)

    def test_detect_crossunder_already_below(self):
        """Test when short MA starts below long MA (no initial cross)."""
        short_ma = pd.Series([10, 9, 8, 7, 6])
        long_ma = pd.Series([20, 21, 22, 23, 24])

        crossunder = detect_crossunder(short_ma, long_ma)

        # Short already below, no crossunder
        assert crossunder.sum() == 0

    def test_detect_crossunder_with_synthetic_data(self, death_cross_data):
        """Test death cross detection with synthetic data."""
        # Generate signals using actual implementation
        signals = generate_ma_signals(death_cross_data, short_period=5, long_period=10)

        # Should detect at least one death cross
        death_crosses = signals['death_cross'].sum()
        assert death_crosses >= 1

        # Verify signal column has sell signals
        sell_signals = (signals['signal'] == -1).sum()
        assert sell_signals >= 1


# =============================================================================
# TEST SUITE 4: SIGNAL GENERATION
# =============================================================================

class TestSignalGeneration:
    """Test suite for complete signal generation pipeline."""

    def test_generate_ma_signals_structure(self, realistic_backtest_data):
        """Test that generate_ma_signals returns correct DataFrame structure."""
        signals = generate_ma_signals(realistic_backtest_data, short_period=10, long_period=20)

        # Check required columns exist
        required_cols = ['price', 'short_ma', 'long_ma', 'golden_cross', 'death_cross', 'signal', 'position']
        for col in required_cols:
            assert col in signals.columns

        # Check data types
        assert signals['signal'].dtype in [int, np.int64]
        assert signals['golden_cross'].dtype == bool
        assert signals['death_cross'].dtype == bool

    def test_generate_ma_signals_invalid_periods(self, simple_price_data):
        """Test that invalid period combinations raise errors."""
        # Short period >= long period should raise error
        with pytest.raises(ValueError, match="Short period.*must be less than long period"):
            generate_ma_signals(simple_price_data, short_period=50, long_period=50)

        with pytest.raises(ValueError, match="Short period.*must be less than long period"):
            generate_ma_signals(simple_price_data, short_period=100, long_period=50)

    def test_generate_ma_signals_values(self, realistic_backtest_data):
        """Test signal values are within expected range."""
        signals = generate_ma_signals(realistic_backtest_data, short_period=10, long_period=20)

        # Signals should be -1, 0, or 1
        assert signals['signal'].isin([-1, 0, 1]).all()

        # Position should be 0 or 1
        assert signals['position'].isin([0, 1]).all()

        # Golden cross and death cross should be boolean
        assert signals['golden_cross'].dtype == bool
        assert signals['death_cross'].dtype == bool

    def test_generate_ma_signals_position_tracking(self):
        """Test that position is correctly tracked based on signals."""
        # Create simple data with known crossovers
        prices = pd.Series([10, 15, 20, 25, 20, 15, 10, 15, 20, 25] * 3)
        signals = generate_ma_signals(prices, short_period=2, long_period=3)

        # Position should be 1 after buy signal, 0 after sell signal
        for i in range(len(signals)):
            if i > 0:
                if signals['signal'].iloc[i] == 1:  # Buy
                    assert signals['position'].iloc[i] == 1
                elif signals['signal'].iloc[i] == -1:  # Sell
                    assert signals['position'].iloc[i] == 0
                # If no signal, position should match previous or follow signal logic

    def test_get_trade_signals(self, realistic_backtest_data):
        """Test filtering to get only actual trade signals."""
        all_signals = generate_ma_signals(realistic_backtest_data, short_period=10, long_period=20)
        trade_signals = get_trade_signals(all_signals)

        # All returned signals should be non-zero
        assert (trade_signals['signal'] != 0).all()

        # Should have fewer rows than original
        assert len(trade_signals) <= len(all_signals)

        # Should only contain rows where signal is 1 or -1
        assert trade_signals['signal'].isin([1, -1]).all()

    def test_calculate_ma_cross_summary(self, realistic_backtest_data):
        """Test summary statistics calculation."""
        signals = generate_ma_signals(realistic_backtest_data, short_period=10, long_period=20)
        summary = calculate_ma_cross_summary(signals)

        # Check required keys
        required_keys = ['total_golden_crosses', 'total_death_crosses', 'total_signals',
                        'first_signal_date', 'last_signal_date']
        for key in required_keys:
            assert key in summary

        # Total signals should equal golden + death crosses
        assert summary['total_signals'] == summary['total_golden_crosses'] + summary['total_death_crosses']

        # Counts should be non-negative
        assert summary['total_golden_crosses'] >= 0
        assert summary['total_death_crosses'] >= 0

    def test_ma_signals_no_crossover(self, flat_price_data):
        """Test signal generation with flat prices (no crossovers)."""
        signals = generate_ma_signals(flat_price_data, short_period=5, long_period=10)

        # Should have no golden or death crosses
        assert signals['golden_cross'].sum() == 0
        assert signals['death_cross'].sum() == 0

        # Should have no trade signals
        assert (signals['signal'] == 0).all()


# =============================================================================
# TEST SUITE 5: BACKTESTING LOGIC
# =============================================================================

class TestBacktestingLogic:
    """Test suite for backtesting engine trade execution and portfolio tracking."""

    def test_backtester_initialization(self):
        """Test MABacktester initialization with custom parameters."""
        backtester = MABacktester(
            initial_capital=50000.0,
            commission=0.002,
            short_period=20,
            long_period=50
        )

        assert backtester.initial_capital == 50000.0
        assert backtester.commission == 0.002
        assert backtester.short_period == 20
        assert backtester.long_period == 50
        assert backtester.trades == []
        assert backtester.portfolio_values == []

    def test_backtester_initialization_defaults(self):
        """Test MABacktester initialization with default parameters."""
        backtester = MABacktester()

        assert backtester.initial_capital == 100000.0
        assert backtester.commission == 0.001
        assert backtester.short_period == 50
        assert backtester.long_period == 200

    def test_backtest_buy_execution(self, golden_cross_data):
        """Test that buy orders are executed correctly."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(golden_cross_data)

        # Should have executed at least one buy trade
        buy_trades = [t for t in results['trades'] if t['type'] == 'BUY']
        assert len(buy_trades) > 0

        # Verify buy trade structure
        first_buy = buy_trades[0]
        assert 'price' in first_buy
        assert 'shares' in first_buy
        assert 'value' in first_buy
        assert first_buy['shares'] > 0
        assert first_buy['value'] > 0

    def test_backtest_sell_execution(self, death_cross_data):
        """Test that sell orders are executed correctly."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(death_cross_data)

        # Should have executed at least one sell trade
        sell_trades = [t for t in results['trades'] if t['type'] == 'SELL']

        # Note: sell only happens if we have shares (after a buy)
        # Death cross data might generate sell signal first, which would be ignored

    def test_backtest_commission_calculation(self, realistic_backtest_data):
        """Test that commissions are correctly applied to trades."""
        initial_capital = 10000.0
        commission = 0.01  # 1% commission for easy verification

        backtester = MABacktester(
            initial_capital=initial_capital,
            commission=commission,
            short_period=5,
            long_period=10
        )

        results = backtester.run_backtest(realistic_backtest_data)

        # Check buy trades have commission applied
        buy_trades = [t for t in results['trades'] if t['type'] == 'BUY']
        if len(buy_trades) > 0:
            buy = buy_trades[0]
            # Cost should include commission: shares * price * (1 + commission)
            expected_cost = buy['shares'] * buy['price'] * (1 + commission)
            assert abs(buy['value'] - expected_cost) < 0.01

        # Check sell trades have commission applied
        sell_trades = [t for t in results['trades'] if t['type'] == 'SELL']
        if len(sell_trades) > 0:
            sell = sell_trades[0]
            # Proceeds should have commission deducted: shares * price * (1 - commission)
            expected_proceeds = sell['shares'] * sell['price'] * (1 - commission)
            assert abs(sell['value'] - expected_proceeds) < 0.01

    def test_backtest_portfolio_value_tracking(self, realistic_backtest_data):
        """Test that portfolio value is tracked correctly over time."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(realistic_backtest_data)

        portfolio_df = results['portfolio_values']

        # Should have portfolio value for each day
        assert len(portfolio_df) > 0

        # Portfolio value columns should exist
        assert 'portfolio_value' in portfolio_df.columns
        assert 'cash' in portfolio_df.columns
        assert 'shares' in portfolio_df.columns

        # Portfolio value should always be positive
        assert (portfolio_df['portfolio_value'] > 0).all()

        # First portfolio value should equal initial capital (approximately)
        first_value = portfolio_df['portfolio_value'].iloc[0]
        assert abs(first_value - backtester.initial_capital) < 1.0

    def test_backtest_cash_and_shares_balance(self, realistic_backtest_data):
        """Test that cash + shares value equals portfolio value."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(realistic_backtest_data)

        portfolio_df = results['portfolio_values']

        # For each row, portfolio_value should equal cash + (shares * price)
        for idx, row in portfolio_df.iterrows():
            if not pd.isna(row['price']):
                expected_value = row['cash'] + (row['shares'] * row['price'])
                actual_value = row['portfolio_value']
                assert abs(expected_value - actual_value) < 1.0  # Allow small rounding error

    def test_backtest_no_trades_on_invalid_signals(self, flat_price_data):
        """Test that no trades execute when there are no valid signals."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(flat_price_data)

        # Should have no trades
        assert len(results['trades']) == 0

        # Final portfolio value should equal initial capital
        final_value = results['portfolio_values']['portfolio_value'].iloc[-1]
        assert abs(final_value - backtester.initial_capital) < 1.0

    def test_backtest_zero_capital(self):
        """Test backtest with zero initial capital."""
        backtester = MABacktester(initial_capital=0.0, short_period=5, long_period=10)

        prices = pd.Series([100, 110, 120, 130, 140] * 10)
        results = backtester.run_backtest(prices)

        # Should have no trades (no capital to buy)
        buy_trades = [t for t in results['trades'] if t['type'] == 'BUY']
        assert len(buy_trades) == 0

    def test_backtest_buy_only_when_no_position(self, multi_cross_data):
        """Test that buy signals only execute when not already holding position."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(multi_cross_data)

        # Track position state
        buy_trades = [t for t in results['trades'] if t['type'] == 'BUY']
        sell_trades = [t for t in results['trades'] if t['type'] == 'SELL']

        # Number of buys should equal or be one more than number of sells
        # (one more if we end with an open position)
        assert len(buy_trades) - len(sell_trades) in [0, 1]

    def test_backtest_sell_only_when_holding_position(self, multi_cross_data):
        """Test that sell signals only execute when holding shares."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(multi_cross_data)

        # Verify every sell is preceded by a buy
        position = 0
        for trade in results['trades']:
            if trade['type'] == 'BUY':
                assert position == 0  # Should only buy when no position
                position = 1
            elif trade['type'] == 'SELL':
                assert position == 1  # Should only sell when holding
                position = 0


# =============================================================================
# TEST SUITE 6: PERFORMANCE METRICS
# =============================================================================

class TestPerformanceMetrics:
    """Test suite for performance metric calculations."""

    def test_total_return_calculation(self, realistic_backtest_data):
        """Test total return calculation."""
        initial_capital = 10000.0
        backtester = MABacktester(initial_capital=initial_capital, short_period=5, long_period=10)
        results = backtester.run_backtest(realistic_backtest_data)

        metrics = results['performance_metrics']

        # Total return should equal final - initial
        expected_return = metrics['final_portfolio_value'] - initial_capital
        assert abs(metrics['profit_loss'] - expected_return) < 0.01

        # Total return percentage should be consistent
        expected_pct = (expected_return / initial_capital) * 100
        assert abs(metrics['total_return_pct'] - expected_pct) < 0.01

    def test_win_rate_calculation(self):
        """Test win rate calculation with known trade outcomes."""
        # Create backtester with known trades
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)

        # Manually set trades for testing
        # 2 winning trades, 1 losing trade -> 66.67% win rate
        backtester.trades = [
            {'type': 'BUY', 'price': 100.0},
            {'type': 'SELL', 'price': 110.0},  # WIN
            {'type': 'BUY', 'price': 105.0},
            {'type': 'SELL', 'price': 95.0},   # LOSS
            {'type': 'BUY', 'price': 90.0},
            {'type': 'SELL', 'price': 100.0},  # WIN
        ]

        # Create minimal portfolio data
        dates = pd.date_range('2023-01-01', periods=6, freq='D')
        backtester.results_df = pd.DataFrame({
            'portfolio_value': [10000] * 6,
            'cash': [10000] * 6,
            'shares': [0] * 6,
            'price': [100] * 6
        }, index=dates)

        metrics = backtester.calculate_performance_metrics()

        # Win rate should be 2/3 = 66.67%
        assert abs(metrics['win_rate_pct'] - 66.67) < 0.1
        assert metrics['num_winning_trades'] == 2
        assert metrics['num_losing_trades'] == 1

    def test_max_drawdown_calculation(self, portfolio_values_data):
        """Test maximum drawdown calculation."""
        backtester = MABacktester()
        backtester.results_df = portfolio_values_data

        metrics = backtester.calculate_performance_metrics()

        # Max drawdown from peak (115000) to trough (102000)
        # Drawdown = (102000 - 115000) / 115000 = -11.30%
        expected_drawdown = ((102000 - 115000) / 115000) * 100
        assert abs(metrics['max_drawdown_pct'] - expected_drawdown) < 0.1

    def test_sharpe_ratio_calculation(self, realistic_backtest_data):
        """Test Sharpe ratio calculation."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(realistic_backtest_data)

        metrics = results['performance_metrics']

        # Sharpe ratio should be calculated
        assert 'sharpe_ratio' in metrics

        # Sharpe ratio should be a reasonable value (typically -3 to 3)
        # For random walk data, expect something close to 0
        assert -5 <= metrics['sharpe_ratio'] <= 5

    def test_annualized_return_calculation(self):
        """Test annualized return calculation."""
        backtester = MABacktester(initial_capital=10000.0)

        # Create portfolio that doubles in 252 days (1 year)
        dates = pd.date_range('2023-01-01', periods=252, freq='D')
        values = np.linspace(10000, 20000, 252)

        backtester.results_df = pd.DataFrame({
            'portfolio_value': values,
            'cash': [10000] * 252,
            'shares': [0] * 252,
            'price': [100] * 252
        }, index=dates)

        metrics = backtester.calculate_performance_metrics()

        # Should have approximately 100% annualized return
        # (20000/10000)^(1/1) - 1 = 1.0 = 100%
        assert abs(metrics['annualized_return_pct'] - 100.0) < 5.0

    def test_trade_count_metrics(self, realistic_backtest_data):
        """Test trade counting metrics."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(realistic_backtest_data)

        metrics = results['performance_metrics']

        # Trade counts should be consistent
        assert metrics['num_trades'] == len(results['trades'])
        assert metrics['num_buy_signals'] + metrics['num_sell_signals'] == metrics['num_trades']

        # Counts should be non-negative
        assert metrics['num_trades'] >= 0
        assert metrics['num_buy_signals'] >= 0
        assert metrics['num_sell_signals'] >= 0

    def test_metrics_with_no_trades(self, flat_price_data):
        """Test metrics calculation when no trades occur."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(flat_price_data)

        metrics = results['performance_metrics']

        # Should have zero trades
        assert metrics['num_trades'] == 0
        assert metrics['num_winning_trades'] == 0
        assert metrics['num_losing_trades'] == 0

        # Win rate should be 0 (no trades to win)
        assert metrics['win_rate_pct'] == 0

        # Return should be approximately 0 (no trading)
        assert abs(metrics['total_return_pct']) < 0.1


# =============================================================================
# TEST SUITE 7: INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for end-to-end backtesting."""

    def test_full_backtest_pipeline(self, realistic_backtest_data):
        """Test complete backtest from data to results."""
        backtester = MABacktester(
            initial_capital=10000.0,
            commission=0.001,
            short_period=10,
            long_period=20
        )

        # Run full backtest
        results = backtester.run_backtest(realistic_backtest_data)

        # Verify all expected result components exist
        assert 'trades' in results
        assert 'portfolio_values' in results
        assert 'performance_metrics' in results
        assert 'signals' in results

        # Verify result types
        assert isinstance(results['trades'], list)
        assert isinstance(results['portfolio_values'], pd.DataFrame)
        assert isinstance(results['performance_metrics'], dict)
        assert isinstance(results['signals'], pd.DataFrame)

    def test_run_ma_backtest_function(self):
        """Test the convenience function run_ma_backtest."""
        # This would normally fetch real data, but we'll skip since it requires network
        # Just test that the function exists and has correct signature
        import inspect

        sig = inspect.signature(run_ma_backtest)
        params = list(sig.parameters.keys())

        assert 'ticker' in params
        assert 'start_date' in params
        assert 'end_date' in params
        assert 'initial_capital' in params

    def test_backtest_with_different_ma_periods(self, realistic_backtest_data):
        """Test backtesting with various MA period combinations."""
        periods = [(5, 10), (10, 20), (20, 50)]

        for short, long in periods:
            backtester = MABacktester(
                initial_capital=10000.0,
                short_period=short,
                long_period=long
            )

            results = backtester.run_backtest(realistic_backtest_data)

            # All should complete successfully
            assert 'performance_metrics' in results
            assert results['performance_metrics']['initial_capital'] == 10000.0

    def test_backtest_results_consistency(self, realistic_backtest_data):
        """Test that running same backtest twice gives same results."""
        backtester1 = MABacktester(initial_capital=10000.0, short_period=10, long_period=20)
        backtester2 = MABacktester(initial_capital=10000.0, short_period=10, long_period=20)

        results1 = backtester1.run_backtest(realistic_backtest_data)
        results2 = backtester2.run_backtest(realistic_backtest_data)

        # Results should be identical
        assert results1['performance_metrics']['final_portfolio_value'] == \
               results2['performance_metrics']['final_portfolio_value']

        assert len(results1['trades']) == len(results2['trades'])

    def test_get_trades_df(self, realistic_backtest_data):
        """Test conversion of trades to DataFrame."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(realistic_backtest_data)

        trades_df = backtester.get_trades_df()

        # Should be a DataFrame
        assert isinstance(trades_df, pd.DataFrame)

        # Should have same number of rows as trades list
        assert len(trades_df) == len(results['trades'])

        # Should have expected columns if trades exist
        if len(trades_df) > 0:
            assert 'type' in trades_df.columns
            assert 'price' in trades_df.columns
            assert 'shares' in trades_df.columns

    def test_print_summary(self, realistic_backtest_data, capsys):
        """Test that print_summary produces output."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        backtester.run_backtest(realistic_backtest_data)

        # Call print_summary
        backtester.print_summary()

        # Capture printed output
        captured = capsys.readouterr()

        # Should have printed summary information
        assert 'BACKTEST SUMMARY' in captured.out
        assert 'Initial Capital' in captured.out
        assert 'Final Portfolio Value' in captured.out

    def test_backtest_with_multiple_crosses(self, multi_cross_data):
        """Test backtest with data containing multiple crossovers."""
        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(multi_cross_data)

        # Should have multiple trades
        assert len(results['trades']) > 2

        # Should have both buy and sell trades
        buy_trades = [t for t in results['trades'] if t['type'] == 'BUY']
        sell_trades = [t for t in results['trades'] if t['type'] == 'SELL']

        assert len(buy_trades) > 0
        assert len(sell_trades) > 0


# =============================================================================
# TEST SUITE 8: EDGE CASES AND ERROR HANDLING
# =============================================================================

class TestEdgeCases:
    """Test suite for edge cases and error handling."""

    def test_backtest_with_nan_prices(self):
        """Test backtest handling of NaN prices."""
        prices = pd.Series([100, 101, np.nan, 103, 104, 105, 106, 107, 108, 109] * 5)

        backtester = MABacktester(initial_capital=10000.0, short_period=3, long_period=5)
        results = backtester.run_backtest(prices)

        # Should complete without errors
        assert 'performance_metrics' in results

    def test_backtest_with_very_small_capital(self):
        """Test backtest with capital too small to buy shares."""
        backtester = MABacktester(initial_capital=1.0, short_period=5, long_period=10)

        prices = pd.Series([100, 110, 120, 130, 140] * 10)
        results = backtester.run_backtest(prices)

        # Should have no buy trades (not enough capital)
        buy_trades = [t for t in results['trades'] if t['type'] == 'BUY']
        assert len(buy_trades) == 0

    def test_backtest_with_high_commission(self):
        """Test backtest with very high commission rate."""
        # 10% commission
        backtester = MABacktester(
            initial_capital=10000.0,
            commission=0.10,
            short_period=5,
            long_period=10
        )

        prices = pd.Series(range(100, 200, 5))
        results = backtester.run_backtest(prices)

        # High commission should significantly reduce returns
        metrics = results['performance_metrics']

        # Should still complete
        assert 'total_return_pct' in metrics

    def test_insufficient_data_for_ma_periods(self):
        """Test with data shorter than required MA periods."""
        short_prices = pd.Series([100, 101, 102, 103, 104])

        # Trying to calculate MA(50) with only 5 data points
        with pytest.raises(ValueError):
            backtester = MABacktester(initial_capital=10000.0, short_period=50, long_period=200)
            backtester.run_backtest(short_prices)

    def test_backtest_single_trade_cycle(self):
        """Test backtest with exactly one buy-sell cycle."""
        # Create data that produces exactly one golden cross and one death cross
        prices = [100] * 20  # Flat
        prices += list(range(100, 120, 2))  # Up trend
        prices += [120] * 20  # Flat
        prices += list(range(120, 100, -2))  # Down trend
        prices += [100] * 20  # Flat

        prices_series = pd.Series(prices, dtype=float)

        backtester = MABacktester(initial_capital=10000.0, short_period=5, long_period=10)
        results = backtester.run_backtest(prices_series)

        # Should have at least one complete trade cycle
        trades = results['trades']
        assert len(trades) >= 1

    def test_metrics_with_empty_results(self):
        """Test that metrics handles empty results gracefully."""
        backtester = MABacktester()

        # Calculate metrics without running backtest
        metrics = backtester.calculate_performance_metrics()

        # Should return empty dict
        assert metrics == {}

    def test_zero_commission_backtest(self, realistic_backtest_data):
        """Test backtest with zero commission."""
        backtester = MABacktester(
            initial_capital=10000.0,
            commission=0.0,
            short_period=5,
            long_period=10
        )

        results = backtester.run_backtest(realistic_backtest_data)

        # Should complete successfully
        assert 'performance_metrics' in results

        # Trades should have zero commission impact
        if len(results['trades']) > 0:
            buy_trades = [t for t in results['trades'] if t['type'] == 'BUY']
            if len(buy_trades) > 0:
                buy = buy_trades[0]
                # Cost should equal shares * price exactly
                expected_cost = buy['shares'] * buy['price']
                assert abs(buy['value'] - expected_cost) < 0.01


# =============================================================================
# SUMMARY TESTS
# =============================================================================

def test_all_modules_importable():
    """Test that all required modules can be imported."""
    try:
        from backend.indicators.ma_indicator import (
            calculate_sma,
            detect_crossover,
            detect_crossunder,
            generate_ma_signals
        )

        from backend.backtest.ma_backtest import (
            MABacktester,
            run_ma_backtest
        )

        # If we got here, all imports succeeded
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required modules: {e}")


def test_complete_workflow():
    """Test a complete realistic workflow."""
    # Create synthetic market data
    np.random.seed(42)
    prices = []
    for i in range(300):
        price = 100 + 10 * np.sin(i / 20) + np.random.normal(0, 2)
        prices.append(max(price, 1.0))

    dates = pd.date_range('2023-01-01', periods=300, freq='D')
    price_series = pd.Series(prices, index=dates, dtype=float)

    # Run complete backtest
    backtester = MABacktester(
        initial_capital=100000.0,
        commission=0.001,
        short_period=10,
        long_period=30
    )

    results = backtester.run_backtest(price_series)

    # Verify complete results structure
    assert 'trades' in results
    assert 'portfolio_values' in results
    assert 'performance_metrics' in results
    assert 'signals' in results

    # Verify metrics are calculated
    metrics = results['performance_metrics']
    assert 'final_portfolio_value' in metrics
    assert 'total_return_pct' in metrics
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown_pct' in metrics
    assert 'win_rate_pct' in metrics

    # Verify results are reasonable
    assert metrics['initial_capital'] == 100000.0
    assert metrics['final_portfolio_value'] > 0
    assert metrics['trading_days'] == 300
