# v-backtester

MA (Moving Average) Golden Cross Backtesting System - A comprehensive backtesting platform for testing Moving Average crossover strategies on stock data.

## Features

- MA Golden Cross/Death Cross signal detection
- Complete backtesting engine with performance metrics
- REST API for programmatic access
- Interactive web-based visualization
- Comprehensive test coverage

## Quick Start

### 1. Install Dependencies

```bash
uv sync
```

### 2. Run a Backtest (Python)

```bash
python backend/example_backtest.py
```

### 3. Start the API Server

```bash
./start_api.sh
```

API will be available at: http://localhost:8000
Interactive docs: http://localhost:8000/docs

### 4. Open the Frontend

```bash
open frontend/index.html
```

## Project Structure

```
v-backtester/
├── backend/
│   ├── indicators/          # MA calculation and signal detection
│   ├── backtest/            # Backtesting engine
│   ├── api/                 # REST API endpoints
│   ├── app.py              # FastAPI application
│   ├── example_backtest.py  # Example usage
│   ├── test_basic.py       # Unit tests
│   └── test_api.py         # API tests
├── frontend/
│   └── index.html          # Web visualization interface
├── start_api.sh            # API startup script
└── pyproject.toml          # Dependencies
```

## Documentation

- [API Documentation](backend/API_README.md) - Complete REST API reference
- [Quick Start Guide](QUICK_START_API.md) - API quick reference
- [Backend README](backend/README.md) - Backend implementation details
- [API Engineer Summary](API_ENGINEER_SUMMARY.md) - API completion report

## Usage Examples

### Python API

```python
from backend.backtest.ma_backtest import run_ma_backtest

results = run_ma_backtest(
    ticker='AAPL',
    start_date='2023-01-01',
    end_date='2023-12-31',
    short_period=50,
    long_period=200
)

print(f"Total Return: {results['performance_metrics']['total_return_pct']}%")
```

### REST API

```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "ticker": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2023-12-31",
    "short_period": 50,
    "long_period": 200
  }'
```

## Testing

```bash
# Backend tests
python backend/test_basic.py

# API tests (requires server running)
python backend/test_api.py
```

## Setup

### step 1. enable claude code agent team setting
- https://youtu.be/Jxp3ruMdKxY?si=ePIGzU1U23xeer3v&t=291
- https://code.claude.com/docs/en/agent-teams#enable-agent-teams

- `open ~/.claude`

- update `settings.json` as below:
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "enabledPlugins": {
    "everything-claude-code@everything-claude-code": true,
    "us-stock-analysis@invest-skill": true
  },
  "extraKnownMarketplaces": {
    "everything-claude-code": {
      "source": {
        "source": "github",
        "repo": "affaan-m/everything-claude-code"
      }
    }
  },
  "feedbackSurveyState": {
    "lastShownTime": 1754277421728
  }
}
```

### step 2. run claude code

```bash
claude --dangerously-skip-permissions
```

### step 2. run below prompt in Claude code CLI

- [prompt](https://github.com/yennanliu/v-backtester/blob/main/prompt/agent_team.txt)



### step 3. ask QA agent test, validte the project



## Ref

- Claude code Agent Teams
  - https://code.claude.com/docs/en/agent-teams
- LargitData - 大數軟體 (example:BackTester - 投資回測系統)
  - 完整影片教學: https://www.largitdata.com/course/258/
  - 程式碼: https://github.com/ywchiu/vibe-backtester
