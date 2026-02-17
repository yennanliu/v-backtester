# Backend Module - MA Golden Cross Backtesting System

## Overview

This backend module implements a complete Moving Average (MA) golden cross/death cross trading strategy with backtesting capabilities. The implementation is pure Python (no TA-Lib dependency) and provides comprehensive performance metrics.

## Project Structure

```
backend/
├── __init__.py
├── indicators/
│   ├── __init__.py
│   └── ma_indicator.py        # MA calculation and cross detection
├── backtest/
│   ├── __init__.py
│   └── ma_backtest.py         # Backtesting engine
├── example_backtest.py        # Example usage script
├── test_basic.py             # Basic functionality tests
└── README.md                 # This file
```

## Features

### MA Indicator Module (`indicators/ma_indicator.py`)

- **Simple Moving Average (SMA) Calculation**: Calculate SMA for any period
- **Golden Cross Detection**: Detects when short MA crosses above long MA (bullish signal)
- **Death Cross Detection**: Detects when short MA crosses below long MA (bearish signal)
- **Signal Generation**: Complete signal generation with position tracking

### Backtesting Engine (`backtest/ma_backtest.py`)

- **Historical Data Fetching**: Uses yfinance to fetch stock data
- **Trade Execution**: Simulates buy/sell orders with commission
- **Position Tracking**: Tracks cash, shares, and portfolio value
- **Performance Metrics**:
  - Total Return (%)
  - Annualized Return (%)
  - Number of Trades
  - Win Rate (%)
  - Maximum Drawdown (%)
  - Sharpe Ratio
  - Buy & Hold Comparison

## Installation

Dependencies are managed in `pyproject.toml`:

```toml
dependencies = [
    "numpy>=2.4.2",
    "pandas>=3.0.0",
    "yfinance>=1.2.0",
]
```

Install with:
```bash
uv sync
```

## Usage Examples

### Basic Usage - Quick Backtest

```python
from backend.backtest.ma_backtest import run_ma_backtest

# Run a simple backtest
results = run_ma_backtest(
    ticker='AAPL',
    start_date='2020-01-01',
    end_date='2023-12-31',
    initial_capital=100000,
    short_period=50,
    long_period=200,
    commission=0.001,
    verbose=True
)

# Access results
print(f"Total Return: {results['performance_metrics']['total_return_pct']:.2f}%")
print(f"Sharpe Ratio: {results['performance_metrics']['sharpe_ratio']:.3f}")
```

### Advanced Usage - Custom Backtester

```python
from backend.backtest.ma_backtest import MABacktester

# Initialize backtester
backtester = MABacktester(
    initial_capital=100000,
    commission=0.001,
    short_period=50,
    long_period=200
)

# Fetch data
data = backtester.fetch_data('SPY', '2020-01-01', '2023-12-31')

# Run backtest
results = backtester.run_backtest(data['Close'])

# Print summary
backtester.print_summary()

# Get trades as DataFrame
trades_df = backtester.get_trades_df()
print(trades_df)

# Access detailed results
portfolio_values = results['portfolio_values']
signals = results['signals']
metrics = results['performance_metrics']
```

### Using MA Indicators Directly

```python
from backend.indicators.ma_indicator import (
    calculate_sma,
    generate_ma_signals,
    get_trade_signals
)
import pandas as pd

# Calculate SMA
prices = pd.Series([100, 102, 104, 103, 105, 107, 106, 108])
sma_5 = calculate_sma(prices, period=5)

# Generate trading signals
signals = generate_ma_signals(
    prices,
    short_period=20,
    long_period=50
)

# Extract only actual trade signals
trades = get_trade_signals(signals)
print(f"Number of trades: {len(trades)}")
```

## Running Examples

### Test Basic Functionality

```bash
PYTHONPATH=/Users/jerryliu/v-backtester .venv/bin/python backend/test_basic.py
```

This runs comprehensive tests on:
- SMA calculation
- Golden cross detection
- Death cross detection
- Signal generation
- Backtester initialization
- Backtest execution

### Run Example Backtest

```bash
PYTHONPATH=/Users/jerryliu/v-backtester .venv/bin/python backend/example_backtest.py
```

This demonstrates a complete backtest on SPY (S&P 500 ETF) from 2020-2023 with detailed output.

## API Reference

### MA Indicator Functions

#### `calculate_sma(data: pd.Series, period: int) -> pd.Series`
Calculate Simple Moving Average for a given period.

#### `detect_crossover(short_ma: pd.Series, long_ma: pd.Series) -> pd.Series`
Detect golden cross (short MA crosses above long MA).

#### `detect_crossunder(short_ma: pd.Series, long_ma: pd.Series) -> pd.Series`
Detect death cross (short MA crosses below long MA).

#### `generate_ma_signals(prices: pd.Series, short_period: int, long_period: int) -> pd.DataFrame`
Generate complete trading signals with MA values and positions.

Returns DataFrame with columns:
- `price`: Original price data
- `short_ma`: Short-period MA
- `long_ma`: Long-period MA
- `signal`: Trading signal (1=BUY, -1=SELL, 0=HOLD)
- `position`: Current position (1=long, 0=neutral)

### Backtester Class

#### `MABacktester.__init__(initial_capital, commission, short_period, long_period)`
Initialize backtester with configuration.

#### `fetch_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame`
Fetch historical OHLCV data using yfinance.

#### `run_backtest(prices: pd.Series) -> Dict`
Execute backtest and return comprehensive results.

Returns:
- `trades`: List of executed trades
- `portfolio_values`: DataFrame of portfolio over time
- `performance_metrics`: Dictionary of performance statistics
- `signals`: DataFrame with MA signals

#### `calculate_performance_metrics() -> Dict`
Calculate performance metrics after backtest.

Returns metrics including:
- `total_return_pct`: Total return percentage
- `annualized_return_pct`: Annualized return
- `num_trades`: Number of trades
- `win_rate_pct`: Percentage of winning trades
- `max_drawdown_pct`: Maximum drawdown
- `sharpe_ratio`: Risk-adjusted return metric

## Strategy Logic

### Golden Cross Strategy

1. **Calculate Moving Averages**:
   - Short MA (e.g., 50-day)
   - Long MA (e.g., 200-day)

2. **Generate Signals**:
   - **BUY (Golden Cross)**: When short MA crosses above long MA
   - **SELL (Death Cross)**: When short MA crosses below long MA

3. **Position Management**:
   - Enter long position on golden cross
   - Exit position on death cross
   - Stay flat when out of position

### Performance Calculation

- **Total Return**: (Final Value - Initial Capital) / Initial Capital
- **Win Rate**: Winning Trades / Total Completed Trades
- **Max Drawdown**: Maximum peak-to-trough decline
- **Sharpe Ratio**: (Average Return / Std Dev of Returns) × √252

## Implementation Details

### Data Requirements

- Minimum data points: `long_period + 1` (e.g., 201 days for 200-day MA)
- Data format: Pandas Series or DataFrame with datetime index
- Data source: yfinance for historical stock data

### Trade Execution

- Commission is applied on both buy and sell
- Fractional shares are supported (calculated as integers)
- All available cash is used for buying
- Positions are fully liquidated on sell signals

### Edge Cases Handled

- NaN values in early MA periods
- Insufficient data for MA calculation
- Zero or negative prices
- Missing data points
- Multiple consecutive signals

## Testing

The module includes comprehensive tests:

```python
# Run all tests
PYTHONPATH=/Users/jerryliu/v-backtester .venv/bin/python backend/test_basic.py
```

Tests cover:
- ✓ SMA calculation accuracy
- ✓ Golden cross detection
- ✓ Death cross detection
- ✓ Signal generation
- ✓ Backtester initialization
- ✓ Complete backtest execution

## Performance Considerations

- Uses pandas vectorized operations for efficiency
- Avoids loops where possible
- Memory-efficient rolling window calculations
- Suitable for datasets with millions of data points

## Next Steps

This backend module is ready for integration with:

1. **REST API** - Expose backtesting functionality via API endpoints
2. **Frontend** - Visualize signals, portfolio values, and performance metrics
3. **Unit Tests** - Comprehensive test suite with edge cases
4. **Extended Features**:
   - Multiple MA periods testing
   - Optimization algorithms
   - Risk management rules
   - Portfolio backtesting

## Dependencies

- **numpy**: Numerical computations
- **pandas**: Data manipulation and time series
- **yfinance**: Historical stock data fetching

## License

Part of the v-backtester project.
