"""
REST API Routes for MA Golden Cross Backtesting

This module provides FastAPI endpoints to run backtests and retrieve results.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import traceback

from backend.backtest.ma_backtest import run_ma_backtest

router = APIRouter(prefix="/api", tags=["backtest"])

# Global storage for latest backtest results (in-memory cache)
_latest_results: Optional[Dict[str, Any]] = None


# Request/Response Models
class BacktestRequest(BaseModel):
    """Request model for running a backtest"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL', 'SPY')")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    short_period: int = Field(default=50, ge=1, description="Short MA period (e.g., 50)")
    long_period: int = Field(default=200, ge=1, description="Long MA period (e.g., 200)")
    initial_capital: float = Field(default=100000.0, gt=0, description="Initial capital amount")
    commission: float = Field(default=0.001, ge=0, le=0.1, description="Commission rate (0.001 = 0.1%)")

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "start_date": "2020-01-01",
                "end_date": "2023-12-31",
                "short_period": 50,
                "long_period": 200,
                "initial_capital": 100000.0,
                "commission": 0.001
            }
        }


class SignalPoint(BaseModel):
    """Trading signal point"""
    date: str
    type: str  # 'golden_cross' or 'death_cross'
    price: float


class ChartData(BaseModel):
    """Chart data for visualization"""
    dates: List[str]
    prices: List[float]
    short_ma: List[float]
    long_ma: List[float]
    signals: List[SignalPoint]
    portfolio_values: List[float]


class PerformanceMetrics(BaseModel):
    """Performance metrics from backtest"""
    initial_capital: float
    final_portfolio_value: float
    profit_loss: float
    total_return_pct: float
    annualized_return_pct: float
    num_trades: int
    num_buy_signals: int
    num_sell_signals: int
    num_winning_trades: int
    num_losing_trades: int
    win_rate_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    trading_days: int
    years: float


class BacktestResponse(BaseModel):
    """Response model for backtest results"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# API Endpoints

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.

    Returns:
        dict: Status and timestamp
    """
    return {
        "status": "healthy",
        "service": "MA Golden Cross Backtester API",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    Run a MA golden cross backtest with the provided parameters.

    Args:
        request: BacktestRequest containing ticker, dates, and strategy parameters

    Returns:
        BacktestResponse with performance metrics and chart data

    Raises:
        HTTPException: If backtest fails (invalid ticker, date range, etc.)
    """
    global _latest_results

    try:
        # Validate date range
        try:
            start = datetime.strptime(request.start_date, "%Y-%m-%d")
            end = datetime.strptime(request.end_date, "%Y-%m-%d")
            if start >= end:
                raise ValueError("start_date must be before end_date")
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid date format or range: {str(e)}"
            )

        # Validate MA periods
        if request.short_period >= request.long_period:
            raise HTTPException(
                status_code=400,
                detail=f"short_period ({request.short_period}) must be less than long_period ({request.long_period})"
            )

        # Run the backtest
        results = run_ma_backtest(
            ticker=request.ticker.upper(),
            start_date=request.start_date,
            end_date=request.end_date,
            initial_capital=request.initial_capital,
            short_period=request.short_period,
            long_period=request.long_period,
            commission=request.commission,
            verbose=False  # Don't print to console
        )

        # Process results for API response
        performance_metrics = results['performance_metrics']
        signals_df = results['signals']
        portfolio_df = results['portfolio_values']
        trades = results['trades']

        # Extract chart data
        dates = [d.strftime("%Y-%m-%d") for d in signals_df.index]
        prices = signals_df['price'].fillna(0).tolist()
        short_ma = signals_df['short_ma'].fillna(0).tolist()
        long_ma = signals_df['long_ma'].fillna(0).tolist()
        portfolio_values = portfolio_df['portfolio_value'].fillna(request.initial_capital).tolist()

        # Extract signal points
        signal_points = []
        for idx, row in signals_df.iterrows():
            if row['signal'] == 1:  # Golden cross
                signal_points.append({
                    "date": idx.strftime("%Y-%m-%d"),
                    "type": "golden_cross",
                    "price": float(row['price']) if not pd.isna(row['price']) else 0.0
                })
            elif row['signal'] == -1:  # Death cross
                signal_points.append({
                    "date": idx.strftime("%Y-%m-%d"),
                    "type": "death_cross",
                    "price": float(row['price']) if not pd.isna(row['price']) else 0.0
                })

        # Format trades for response
        formatted_trades = []
        for trade in trades:
            formatted_trades.append({
                "date": trade['date'].strftime("%Y-%m-%d"),
                "type": trade['type'],
                "price": float(trade['price']),
                "shares": int(trade['shares']),
                "value": float(trade['value']),
                "cash_after": float(trade['cash_after']),
                "portfolio_value": float(trade['portfolio_value'])
            })

        # Build response
        response_data = {
            "request_params": {
                "ticker": request.ticker.upper(),
                "start_date": request.start_date,
                "end_date": request.end_date,
                "short_period": request.short_period,
                "long_period": request.long_period,
                "initial_capital": request.initial_capital,
                "commission": request.commission
            },
            "performance_metrics": {
                "initial_capital": float(performance_metrics['initial_capital']),
                "final_portfolio_value": float(performance_metrics['final_portfolio_value']),
                "profit_loss": float(performance_metrics['profit_loss']),
                "total_return_pct": round(float(performance_metrics['total_return_pct']), 2),
                "annualized_return_pct": round(float(performance_metrics['annualized_return_pct']), 2),
                "num_trades": int(performance_metrics['num_trades']),
                "num_buy_signals": int(performance_metrics['num_buy_signals']),
                "num_sell_signals": int(performance_metrics['num_sell_signals']),
                "num_winning_trades": int(performance_metrics['num_winning_trades']),
                "num_losing_trades": int(performance_metrics['num_losing_trades']),
                "win_rate_pct": round(float(performance_metrics['win_rate_pct']), 2),
                "max_drawdown_pct": round(float(performance_metrics['max_drawdown_pct']), 2),
                "sharpe_ratio": round(float(performance_metrics['sharpe_ratio']), 3),
                "trading_days": int(performance_metrics['trading_days']),
                "years": round(float(performance_metrics['years']), 2)
            },
            "chart_data": {
                "dates": dates,
                "prices": prices,
                "short_ma": short_ma,
                "long_ma": long_ma,
                "signals": signal_points,
                "portfolio_values": portfolio_values
            },
            "trades": formatted_trades
        }

        # Store in global cache
        _latest_results = response_data

        return BacktestResponse(
            success=True,
            data=response_data
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Backtest failed: {str(e)}"
        print(f"ERROR: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=error_msg
        )


@router.get("/backtest/results", response_model=BacktestResponse)
async def get_latest_results():
    """
    Retrieve the latest backtest results from cache.

    Returns:
        BacktestResponse with the most recent backtest data

    Raises:
        HTTPException: If no backtest has been run yet
    """
    global _latest_results

    if _latest_results is None:
        raise HTTPException(
            status_code=404,
            detail="No backtest results available. Please run a backtest first using POST /api/backtest"
        )

    return BacktestResponse(
        success=True,
        data=_latest_results
    )


@router.delete("/backtest/results")
async def clear_results():
    """
    Clear the cached backtest results.

    Returns:
        dict: Confirmation message
    """
    global _latest_results
    _latest_results = None

    return {
        "success": True,
        "message": "Cached results cleared successfully"
    }


# Import pandas for isna checks
import pandas as pd
