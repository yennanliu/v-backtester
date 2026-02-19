"""
MA Strategy Backtesting Engine

This module provides comprehensive backtesting functionality for Moving Average
golden cross/death cross strategies. It handles trade execution, portfolio tracking,
and performance metric calculations.

Features:
- Historical data fetching via yfinance
- Trade execution with position tracking
- Performance metrics: returns, win rate, max drawdown, Sharpe ratio
- Detailed trade log and portfolio value tracking
"""

import pandas as pd
import numpy as np
import yfinance as yf
from typing import Dict, Tuple, Optional, List
from datetime import datetime

from backend.indicators.ma_indicator import generate_ma_signals


class MABacktester:
    """
    Backtesting engine for Moving Average golden cross/death cross strategy.

    Attributes:
        initial_capital: Starting capital for the backtest
        commission: Commission rate per trade (e.g., 0.001 for 0.1%)
        short_period: Short MA period (e.g., 50 days)
        long_period: Long MA period (e.g., 200 days)
    """

    def __init__(
        self,
        initial_capital: float = 100000.0,
        commission: float = 0.001,
        short_period: int = 50,
        long_period: int = 200
    ):
        """
        Initialize the backtester.

        Args:
            initial_capital: Starting cash amount
            commission: Commission rate as decimal (0.001 = 0.1%)
            short_period: Period for short moving average
            long_period: Period for long moving average
        """
        self.initial_capital = initial_capital
        self.commission = commission
        self.short_period = short_period
        self.long_period = long_period

        # Results storage
        self.trades = []
        self.portfolio_values = []
        self.signals_df = None
        self.results_df = None

    def fetch_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Fetch historical price data using yfinance.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'SPY')
            start_date: Start date in 'YYYY-MM-DD' format
            end_date: End date in 'YYYY-MM-DD' format

        Returns:
            DataFrame with OHLCV data indexed by date

        Raises:
            ValueError: If data fetch fails or returns empty
        """
        try:
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False
            )

            if data.empty:
                raise ValueError(f"No data found for {ticker} between {start_date} and {end_date}")

            return data

        except Exception as e:
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")

    def run_backtest(
        self,
        prices: pd.Series,
        dates: Optional[pd.DatetimeIndex] = None
    ) -> Dict:
        """
        Execute the backtest on provided price data.

        Args:
            prices: Pandas Series of closing prices
            dates: Optional DatetimeIndex for the prices (uses prices.index if None)

        Returns:
            Dictionary containing:
                - trades: List of executed trades
                - portfolio_values: DataFrame of portfolio value over time
                - performance_metrics: Dictionary of performance statistics
                - signals: DataFrame with MA values and signals

        Example:
            >>> backtester = MABacktester(initial_capital=100000)
            >>> data = backtester.fetch_data('AAPL', '2020-01-01', '2023-12-31')
            >>> results = backtester.run_backtest(data['Close'])
        """
        if dates is None:
            dates = prices.index

        # Generate trading signals
        self.signals_df = generate_ma_signals(
            prices,
            self.short_period,
            self.long_period
        )

        # Initialize portfolio tracking
        cash = self.initial_capital
        shares = 0
        portfolio_value = self.initial_capital

        # Track portfolio over time
        portfolio_data = []

        # Execute trades based on signals
        for i, (date, row) in enumerate(self.signals_df.iterrows()):
            price = row['price']
            signal = row['signal']

            # Skip if price or MAs are NaN
            if pd.isna(price) or pd.isna(row['short_ma']) or pd.isna(row['long_ma']):
                portfolio_data.append({
                    'date': date,
                    'cash': cash,
                    'shares': shares,
                    'price': price if not pd.isna(price) else 0,
                    'portfolio_value': cash,
                    'signal': 0
                })
                continue

            # Execute BUY signal
            if signal == 1 and shares == 0:  # Golden cross - buy
                shares_to_buy = int(cash / (price * (1 + self.commission)))
                if shares_to_buy > 0:
                    cost = shares_to_buy * price * (1 + self.commission)
                    cash -= cost
                    shares += shares_to_buy

                    self.trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': price,
                        'shares': shares_to_buy,
                        'value': cost,
                        'cash_after': cash,
                        'portfolio_value': cash + shares * price
                    })

            # Execute SELL signal
            elif signal == -1 and shares > 0:  # Death cross - sell
                proceeds = shares * price * (1 - self.commission)
                cash += proceeds

                self.trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': price,
                    'shares': shares,
                    'value': proceeds,
                    'cash_after': cash,
                    'portfolio_value': cash
                })

                shares = 0

            # Calculate current portfolio value
            portfolio_value = cash + shares * price

            portfolio_data.append({
                'date': date,
                'cash': cash,
                'shares': shares,
                'price': price,
                'portfolio_value': portfolio_value,
                'signal': signal
            })

        # Create portfolio DataFrame
        self.results_df = pd.DataFrame(portfolio_data)
        self.results_df.set_index('date', inplace=True)

        # Calculate performance metrics
        performance_metrics = self.calculate_performance_metrics()

        return {
            'trades': self.trades,
            'portfolio_values': self.results_df,
            'performance_metrics': performance_metrics,
            'signals': self.signals_df
        }

    def calculate_performance_metrics(self) -> Dict:
        """
        Calculate comprehensive performance metrics for the backtest.

        Returns:
            Dictionary containing:
                - total_return: Total return percentage
                - total_return_pct: Total return as percentage
                - annualized_return: Annualized return percentage
                - num_trades: Total number of trades executed
                - num_winning_trades: Number of profitable trades
                - num_losing_trades: Number of unprofitable trades
                - win_rate: Percentage of winning trades
                - max_drawdown: Maximum drawdown percentage
                - max_drawdown_pct: Max drawdown as percentage
                - sharpe_ratio: Sharpe ratio (assuming 0% risk-free rate)
                - final_portfolio_value: Ending portfolio value
                - profit_loss: Total profit/loss amount

        Note:
            Requires run_backtest() to be executed first
        """
        if self.results_df is None or len(self.results_df) == 0:
            return {}

        # Basic return metrics
        final_value = self.results_df['portfolio_value'].iloc[-1]
        total_return = final_value - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100

        # Annualized return
        days = len(self.results_df)
        years = days / 252  # Trading days per year
        annualized_return = (((final_value / self.initial_capital) ** (1 / years)) - 1) * 100 if years > 0 else 0

        # Trade statistics
        num_trades = len(self.trades)
        winning_trades = 0
        losing_trades = 0

        if num_trades > 0:
            # Pair up buy and sell trades to calculate wins/losses
            buy_price = None
            for trade in self.trades:
                if trade['type'] == 'BUY':
                    buy_price = trade['price']
                elif trade['type'] == 'SELL' and buy_price is not None:
                    if trade['price'] > buy_price:
                        winning_trades += 1
                    else:
                        losing_trades += 1
                    buy_price = None

        win_rate = (winning_trades / (winning_trades + losing_trades) * 100) if (winning_trades + losing_trades) > 0 else 0

        # Maximum drawdown
        portfolio_values = self.results_df['portfolio_value']
        cummax = portfolio_values.cummax()
        drawdown = (portfolio_values - cummax) / cummax * 100
        max_drawdown = drawdown.min()

        # Sharpe ratio (assuming 0% risk-free rate)
        returns = portfolio_values.pct_change().dropna()
        sharpe_ratio = 0
        if len(returns) > 0 and returns.std() != 0:
            avg_return = returns.mean()
            std_return = returns.std()
            sharpe_ratio = (avg_return / std_return) * np.sqrt(252)  # Annualized

        metrics = {
            'initial_capital': self.initial_capital,
            'final_portfolio_value': final_value,
            'profit_loss': total_return,
            'total_return_pct': total_return_pct,
            'annualized_return_pct': annualized_return,
            'num_trades': num_trades,
            'num_buy_signals': sum(1 for t in self.trades if t['type'] == 'BUY'),
            'num_sell_signals': sum(1 for t in self.trades if t['type'] == 'SELL'),
            'num_winning_trades': winning_trades,
            'num_losing_trades': losing_trades,
            'win_rate_pct': win_rate,
            'max_drawdown_pct': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'trading_days': len(self.results_df),
            'years': years
        }

        return metrics

    def get_trades_df(self) -> pd.DataFrame:
        """
        Get trades as a formatted DataFrame.

        Returns:
            DataFrame with all executed trades
        """
        if not self.trades:
            return pd.DataFrame()

        return pd.DataFrame(self.trades)

    def print_summary(self):
        """
        Print a formatted summary of backtest results.

        Example output:
            ========================================
            MA GOLDEN CROSS BACKTEST SUMMARY
            ========================================
            Strategy: MA(50) / MA(200)
            Initial Capital: $100,000.00
            Final Portfolio Value: $125,430.50
            Total Return: $25,430.50 (25.43%)
            Annualized Return: 8.12%
            ...
        """
        if self.results_df is None:
            print("No backtest results available. Run backtest first.")
            return

        metrics = self.calculate_performance_metrics()

        print("\n" + "=" * 50)
        print("MA GOLDEN CROSS BACKTEST SUMMARY")
        print("=" * 50)
        print(f"Strategy: MA({self.short_period}) / MA({self.long_period})")
        print(f"Initial Capital: ${metrics['initial_capital']:,.2f}")
        print(f"Final Portfolio Value: ${metrics['final_portfolio_value']:,.2f}")
        print(f"Total Return: ${metrics['profit_loss']:,.2f} ({metrics['total_return_pct']:.2f}%)")
        print(f"Annualized Return: {metrics['annualized_return_pct']:.2f}%")
        print(f"\nTrading Period: {metrics['trading_days']} days ({metrics['years']:.2f} years)")
        print(f"Total Trades: {metrics['num_trades']}")
        print(f"  - Buy Signals: {metrics['num_buy_signals']}")
        print(f"  - Sell Signals: {metrics['num_sell_signals']}")
        print(f"Winning Trades: {metrics['num_winning_trades']}")
        print(f"Losing Trades: {metrics['num_losing_trades']}")
        print(f"Win Rate: {metrics['win_rate_pct']:.2f}%")
        print(f"\nMax Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
        print("=" * 50 + "\n")


def run_ma_backtest(
    ticker: str,
    start_date: str,
    end_date: str,
    initial_capital: float = 100000.0,
    short_period: int = 50,
    long_period: int = 200,
    commission: float = 0.001,
    verbose: bool = True
) -> Dict:
    """
    Convenience function to run a complete MA backtest.

    Args:
        ticker: Stock ticker symbol
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        initial_capital: Starting capital
        short_period: Short MA period
        long_period: Long MA period
        commission: Commission rate
        verbose: If True, print summary

    Returns:
        Dictionary with backtest results

    Example:
        >>> results = run_ma_backtest('AAPL', '2020-01-01', '2023-12-31')
        >>> print(f"Final value: ${results['performance_metrics']['final_portfolio_value']:,.2f}")
    """
    backtester = MABacktester(
        initial_capital=initial_capital,
        commission=commission,
        short_period=short_period,
        long_period=long_period
    )

    # Fetch data
    data = backtester.fetch_data(ticker, start_date, end_date)

    # Run backtest (squeeze to Series in case yfinance returns a single-column DataFrame)
    results = backtester.run_backtest(data['Close'].squeeze())

    # Print summary if verbose
    if verbose:
        backtester.print_summary()

    return results
