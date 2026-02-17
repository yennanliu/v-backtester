# MA Golden Cross Backtester API

REST API for running Moving Average golden cross backtests on stock data.

## Quick Start

### 1. Start the API Server

**Option A: Using the startup script**
```bash
./start_api.sh
```

**Option B: Using Python directly**
```bash
python backend/app.py
```

**Option C: Using uvicorn**
```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. View Interactive Documentation

Open your browser and navigate to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Root Endpoint
```
GET /
```
Returns API information and available endpoints.

### Health Check
```
GET /api/health
```
Verify the API is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "MA Golden Cross Backtester API",
  "timestamp": "2023-12-31T12:00:00"
}
```

### Run Backtest
```
POST /api/backtest
```
Execute a MA golden cross backtest with specified parameters.

**Request Body:**
```json
{
  "ticker": "AAPL",
  "start_date": "2020-01-01",
  "end_date": "2023-12-31",
  "short_period": 50,
  "long_period": 200,
  "initial_capital": 100000.0,
  "commission": 0.001
}
```

**Parameters:**
- `ticker` (required): Stock ticker symbol (e.g., "AAPL", "SPY")
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `short_period` (optional): Short MA period, default 50
- `long_period` (optional): Long MA period, default 200
- `initial_capital` (optional): Initial capital, default 100000.0
- `commission` (optional): Commission rate, default 0.001 (0.1%)

**Response:**
```json
{
  "success": true,
  "data": {
    "request_params": {
      "ticker": "AAPL",
      "start_date": "2020-01-01",
      "end_date": "2023-12-31",
      "short_period": 50,
      "long_period": 200,
      "initial_capital": 100000.0,
      "commission": 0.001
    },
    "performance_metrics": {
      "initial_capital": 100000.0,
      "final_portfolio_value": 125500.0,
      "profit_loss": 25500.0,
      "total_return_pct": 25.5,
      "annualized_return_pct": 7.2,
      "num_trades": 12,
      "num_buy_signals": 6,
      "num_sell_signals": 6,
      "num_winning_trades": 7,
      "num_losing_trades": 5,
      "win_rate_pct": 58.3,
      "max_drawdown_pct": -15.2,
      "sharpe_ratio": 1.234,
      "trading_days": 1000,
      "years": 3.97
    },
    "chart_data": {
      "dates": ["2020-01-01", "2020-01-02", ...],
      "prices": [150.5, 151.2, ...],
      "short_ma": [148.2, 149.1, ...],
      "long_ma": [145.8, 146.0, ...],
      "signals": [
        {
          "date": "2020-03-15",
          "type": "golden_cross",
          "price": 155.5
        },
        {
          "date": "2020-09-20",
          "type": "death_cross",
          "price": 142.3
        }
      ],
      "portfolio_values": [100000.0, 100500.0, ...]
    },
    "trades": [
      {
        "date": "2020-03-15",
        "type": "BUY",
        "price": 155.5,
        "shares": 642,
        "value": 99954.1,
        "cash_after": 45.9,
        "portfolio_value": 100000.0
      }
    ]
  }
}
```

### Get Latest Results
```
GET /api/backtest/results
```
Retrieve the most recent backtest results from cache.

**Response:**
Same format as POST /api/backtest response.

**Error Response (404):**
```json
{
  "success": false,
  "error": "No backtest results available. Please run a backtest first."
}
```

### Clear Cached Results
```
DELETE /api/backtest/results
```
Clear the cached backtest results.

**Response:**
```json
{
  "success": true,
  "message": "Cached results cleared successfully"
}
```

## Usage Examples

### cURL Examples

**Run a backtest:**
```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "short_period": 20,
    "long_period": 50,
    "initial_capital": 100000.0
  }'
```

**Get latest results:**
```bash
curl -X GET "http://localhost:8000/api/backtest/results"
```

**Health check:**
```bash
curl -X GET "http://localhost:8000/api/health"
```

### Python Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Run a backtest
payload = {
    "ticker": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "short_period": 20,
    "long_period": 50,
    "initial_capital": 100000.0
}

response = requests.post(f"{BASE_URL}/api/backtest", json=payload)
data = response.json()

if data['success']:
    metrics = data['data']['performance_metrics']
    print(f"Total Return: {metrics['total_return_pct']}%")
    print(f"Win Rate: {metrics['win_rate_pct']}%")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']}")
else:
    print(f"Error: {data['error']}")
```

### JavaScript Example

```javascript
const BASE_URL = "http://localhost:8000";

async function runBacktest() {
  const payload = {
    ticker: "AAPL",
    start_date: "2023-01-01",
    end_date: "2023-12-31",
    short_period: 20,
    long_period: 50,
    initial_capital: 100000.0
  };

  try {
    const response = await fetch(`${BASE_URL}/api/backtest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (data.success) {
      const metrics = data.data.performance_metrics;
      console.log(`Total Return: ${metrics.total_return_pct}%`);
      console.log(`Win Rate: ${metrics.win_rate_pct}%`);
      console.log(`Sharpe Ratio: ${metrics.sharpe_ratio}`);

      // Use chart_data for visualization
      const chartData = data.data.chart_data;
      // ... plot charts
    } else {
      console.error(`Error: ${data.error}`);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}

runBacktest();
```

## Testing

Run the test suite to verify all endpoints:

```bash
python backend/test_api.py
```

Make sure the API server is running before executing the tests.

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (no cached results)
- `500`: Internal Server Error (backtest execution failed)

Error responses include a descriptive message:
```json
{
  "success": false,
  "error": "Detailed error message here"
}
```

## CORS Configuration

The API is configured to accept requests from any origin (localhost, file://, etc.) for development purposes. This allows the frontend HTML file to call the API directly.

**Note**: In production, you should restrict CORS to specific trusted origins.

## Dependencies

- FastAPI - Modern web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- pandas, numpy - Data processing
- yfinance - Stock data fetching

All dependencies are managed through `pyproject.toml` and can be installed with:
```bash
uv sync
```

## Architecture

```
backend/
├── app.py              # Main FastAPI application
├── api/
│   ├── __init__.py     # API module initialization
│   └── ma_routes.py    # API route handlers
├── backtest/
│   └── ma_backtest.py  # Backtesting engine
└── indicators/
    └── ma_indicator.py # MA calculation functions
```

The API layer is a thin wrapper around the core backtesting engine, providing:
- Request validation
- Error handling
- JSON serialization
- Result caching
- CORS support

## Tips

1. **Date Range**: Ensure sufficient historical data for the MA periods (e.g., for MA(200), you need at least 200 days of data)

2. **Performance**: Large date ranges may take longer to process due to data fetching from yfinance

3. **Caching**: Results are cached in memory. Restart the server to clear all cached data.

4. **Interactive Docs**: Use the Swagger UI at `/docs` to test endpoints interactively

5. **Frontend Integration**: The API returns chart-ready data that can be directly used with charting libraries like Chart.js, Plotly, or D3.js

## Next Steps

- Integrate with the frontend HTML visualization
- Add authentication for production deployment
- Implement persistent storage (database) for results
- Add rate limiting to prevent abuse
- Support batch backtests
- Add more strategy parameters
