"""
API Module for MA Golden Cross Backtesting

This module provides REST API endpoints to expose backtesting functionality.
"""

from .ma_routes import router

__all__ = ['router']
