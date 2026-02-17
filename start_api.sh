#!/bin/bash

# Start the MA Golden Cross Backtester API
# This script starts the FastAPI server on http://localhost:8000

echo "=========================================="
echo "MA Golden Cross Backtester API"
echo "=========================================="
echo ""
echo "Starting API server..."
echo "API will be available at: http://localhost:8000"
echo "Interactive docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Start the server
python backend/app.py
