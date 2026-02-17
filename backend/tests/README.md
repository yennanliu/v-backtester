# MA Golden Cross Backtesting Test Suite

Comprehensive unit test suite for the MA Golden Cross backtesting system.

## Quick Start

```bash
# Run all tests
uv run pytest backend/tests/test_ma_strategy.py -v

# Run with coverage
uv run pytest backend/tests/test_ma_strategy.py --cov=backend.indicators --cov=backend.backtest --cov-report=term-missing

# Run specific test class
uv run pytest backend/tests/test_ma_strategy.py::TestMACalculation -v
```

## Test Structure

### Test Files
- `test_ma_strategy.py` - Main test suite (62 tests)
- `conftest.py` - Pytest fixtures and test data
- `__init__.py` - Module initialization

### Test Suites

1. **TestMACalculation** (10 tests) - MA calculation correctness
2. **TestGoldenCrossDetection** (6 tests) - Golden cross signal detection
3. **TestDeathCrossDetection** (5 tests) - Death cross signal detection
4. **TestSignalGeneration** (7 tests) - Complete signal generation pipeline
5. **TestBacktestingLogic** (12 tests) - Trade execution and portfolio tracking
6. **TestPerformanceMetrics** (7 tests) - Performance metric calculations
7. **TestIntegration** (7 tests) - End-to-end integration tests
8. **TestEdgeCases** (8 tests) - Edge cases and error handling

## Coverage

Current coverage: **91%**

```
Module                           Coverage
backend/indicators/ma_indicator.py  100%
backend/backtest/ma_backtest.py      87%
Overall                              91%
```

## Test Data Fixtures

Available in `conftest.py`:

- `simple_price_data` - Simple integer sequence
- `golden_cross_data` - Synthetic data with golden cross
- `death_cross_data` - Synthetic data with death cross
- `multi_cross_data` - Multiple crossovers
- `flat_price_data` - Flat prices (no trend)
- `realistic_backtest_data` - 500 days of realistic data
- `known_ma_values` - Data with known MA values
- `edge_case_data` - Edge case scenarios
- `sample_trades` - Sample trade data
- `portfolio_values_data` - Portfolio values for testing

## Running Specific Tests

```bash
# Run MA calculation tests
uv run pytest backend/tests/test_ma_strategy.py::TestMACalculation -v

# Run golden cross detection tests
uv run pytest backend/tests/test_ma_strategy.py::TestGoldenCrossDetection -v

# Run performance metrics tests
uv run pytest backend/tests/test_ma_strategy.py::TestPerformanceMetrics -v

# Run single test
uv run pytest backend/tests/test_ma_strategy.py::TestMACalculation::test_calculate_sma_basic -v
```

## Coverage Reports

```bash
# Terminal coverage report
uv run pytest backend/tests/test_ma_strategy.py --cov=backend --cov-report=term

# HTML coverage report
uv run pytest backend/tests/test_ma_strategy.py --cov=backend --cov-report=html
open htmlcov/index.html
```

## Test Results

All 62 tests passing:
- 10 MA calculation tests ✓
- 6 golden cross detection tests ✓
- 5 death cross detection tests ✓
- 7 signal generation tests ✓
- 12 backtesting logic tests ✓
- 7 performance metrics tests ✓
- 7 integration tests ✓
- 8 edge case tests ✓

## What's Tested

### MA Calculation
- Basic SMA calculations
- Rolling window behavior
- Edge cases (empty data, single value, insufficient data)
- Error handling (invalid periods, NaN values)

### Golden/Death Cross Detection
- Correct crossover identification
- Equality edge cases
- Multiple crosses in oscillating data
- No false positives

### Backtesting Engine
- Buy/sell execution
- Commission calculations
- Portfolio value tracking
- Position state machine
- Cash and shares balance

### Performance Metrics
- Total return calculation
- Win rate calculation
- Maximum drawdown
- Sharpe ratio
- Annualized returns

### Integration
- End-to-end workflow
- Result consistency
- Various MA period combinations
- Multiple crossover scenarios

## Dependencies

```bash
pytest==9.0.2
pytest-cov==7.0.0
```

Installed via:
```bash
uv add pytest pytest-cov
```

## Test Quality

- **Total Tests**: 62
- **Code Coverage**: 91%
- **Assertions**: 200+
- **Test Classes**: 8
- **Fixtures**: 10
- **Edge Cases**: 15+

## Notes

- Two expected warnings in zero capital edge case test (division by zero)
- Network-dependent functions (`fetch_data`, `run_ma_backtest`) not fully covered (require mocking)
- Core logic has 100% coverage
