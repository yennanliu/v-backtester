# MA Golden Cross Backtester API - Quick Start Guide

## Start the Server

```bash
# Option 1: Use the startup script (recommended)
./start_api.sh

# Option 2: Direct Python
python backend/app.py

# Option 3: Uvicorn command
uvicorn backend.app:app --reload
```

Server will start at: **http://localhost:8000**

---

## Quick Test

### 1. Health Check
```bash
curl http://localhost:8000/api/health
```

### 2. Run a Backtest
```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "short_period": 20,
    "long_period": 50
  }'
```

### 3. Get Latest Results
```bash
curl http://localhost:8000/api/backtest/results
```

---

## Test Suite

```bash
# Run all tests (server must be running)
python backend/test_api.py
```

---

## Interactive Documentation

Open in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/api/health` | Health check |
| POST | `/api/backtest` | Run backtest |
| GET | `/api/backtest/results` | Get latest results |
| DELETE | `/api/backtest/results` | Clear cache |

---

## Request Example (Python)

```python
import requests

response = requests.post('http://localhost:8000/api/backtest', json={
    'ticker': 'AAPL',
    'start_date': '2023-01-01',
    'end_date': '2023-12-31',
    'short_period': 20,
    'long_period': 50,
    'initial_capital': 100000.0
})

data = response.json()
print(f"Return: {data['data']['performance_metrics']['total_return_pct']}%")
```

---

## Request Example (JavaScript)

```javascript
fetch('http://localhost:8000/api/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    ticker: 'AAPL',
    start_date: '2023-01-01',
    end_date: '2023-12-31',
    short_period: 20,
    long_period: 50
  })
})
.then(res => res.json())
.then(data => {
  console.log('Return:', data.data.performance_metrics.total_return_pct + '%');
});
```

---

## Files Created

```
backend/
├── app.py                    # Main FastAPI application
├── api/
│   ├── __init__.py          # API module init
│   └── ma_routes.py         # API endpoints (298 lines)
├── test_api.py              # Test suite
└── API_README.md            # Full documentation

Root:
├── start_api.sh             # Startup script
├── QUICK_START_API.md       # This file
└── API_ENGINEER_SUMMARY.md  # Completion report
```

---

## Dependencies Added

- fastapi
- uvicorn
- pydantic
- requests

(Already installed via `uv add`)

---

## Common Issues

**Port already in use?**
```bash
# Change port in backend/app.py or use:
uvicorn backend.app:app --reload --port 8001
```

**Import errors?**
```bash
# Activate virtual environment:
source .venv/bin/activate
```

**CORS errors from frontend?**
- CORS is already enabled for all origins
- Make sure server is running at http://localhost:8000

---

For detailed documentation, see: **backend/API_README.md**
