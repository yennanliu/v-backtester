"""
Main FastAPI Application Entry Point

This module initializes the FastAPI application and includes all API routes.
Run with: uvicorn backend.app:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.ma_routes import router

# Create FastAPI application
app = FastAPI(
    title="MA Golden Cross Backtester API",
    description="REST API for running Moving Average golden cross backtests",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend integration
# Allow all origins for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (localhost, file://, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include API routes
app.include_router(router)


# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "service": "MA Golden Cross Backtester API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/api/health",
        "endpoints": {
            "POST /api/backtest": "Run a backtest",
            "GET /api/backtest/results": "Get latest backtest results",
            "DELETE /api/backtest/results": "Clear cached results",
            "GET /api/health": "Health check"
        }
    }


if __name__ == "__main__":
    import uvicorn

    # Run the server
    print("Starting MA Golden Cross Backtester API...")
    print("API Documentation: http://localhost:8000/docs")
    print("Root endpoint: http://localhost:8000/")
    print("Health check: http://localhost:8000/api/health")

    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
