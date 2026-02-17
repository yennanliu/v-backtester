"""
Example script demonstrating MA Golden Cross backtesting.

This script shows how to:
1. Fetch historical stock data
2. Run a backtest with MA golden cross strategy
3. Display performance metrics
4. Show trade history

Usage:
    python backend/example_backtest.py
"""

from backend.backtest.ma_backtest import run_ma_backtest, MABacktester
import pandas as pd


def main():
    """Run example backtest on SPY (S&P 500 ETF)."""

    print("\n" + "=" * 60)
    print("MA GOLDEN CROSS BACKTEST - EXAMPLE")
    print("=" * 60)

    # Configuration
    ticker = "SPY"  # S&P 500 ETF
    start_date = "2020-01-01"
    end_date = "2023-12-31"
    initial_capital = 100000.0
    short_period = 50   # 50-day MA
    long_period = 200   # 200-day MA

    print(f"\nBacktesting {ticker} from {start_date} to {end_date}")
    print(f"Strategy: MA({short_period}) / MA({long_period}) Golden Cross")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print("\nFetching data and running backtest...\n")

    try:
        # Run the backtest
        results = run_ma_backtest(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            short_period=short_period,
            long_period=long_period,
            commission=0.001,  # 0.1% commission
            verbose=True  # Print summary
        )

        # Display trade history
        print("\nTRADE HISTORY:")
        print("-" * 60)
        trades_df = pd.DataFrame(results['trades'])
        if not trades_df.empty:
            trades_df['date'] = pd.to_datetime(trades_df['date']).dt.strftime('%Y-%m-%d')
            print(trades_df.to_string(index=False))
        else:
            print("No trades executed during this period.")

        # Additional analysis
        metrics = results['performance_metrics']
        print("\n" + "=" * 60)
        print("ADDITIONAL INSIGHTS")
        print("=" * 60)

        if metrics['num_trades'] > 0:
            avg_gain_per_trade = metrics['profit_loss'] / (metrics['num_trades'] / 2)
            print(f"Average gain per complete trade cycle: ${avg_gain_per_trade:,.2f}")

        # Buy and hold comparison
        portfolio_df = results['portfolio_values']
        first_price = portfolio_df['price'].iloc[0]
        last_price = portfolio_df['price'].iloc[-1]
        buy_hold_return = ((last_price - first_price) / first_price) * 100

        print(f"\nBuy & Hold Strategy:")
        print(f"  - Return: {buy_hold_return:.2f}%")
        print(f"MA Strategy:")
        print(f"  - Return: {metrics['total_return_pct']:.2f}%")
        print(f"Strategy Outperformance: {metrics['total_return_pct'] - buy_hold_return:.2f}%")

        print("\n" + "=" * 60)
        print("Backtest completed successfully!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\nError running backtest: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
