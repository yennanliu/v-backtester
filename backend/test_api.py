"""
API Testing Script

Simple script to test the MA Golden Cross Backtester API endpoints.
Make sure the API server is running before executing this script.

Usage:
    python backend/test_api.py
"""

import requests
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_response(title: str, response: requests.Response):
    """Pretty print API response"""
    print(f"\n{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2, default=str))
    except:
        print(response.text)
    print(f"{'=' * 70}\n")


def test_health_check():
    """Test health check endpoint"""
    print("\n[TEST 1] Testing Health Check Endpoint...")
    response = requests.get(f"{BASE_URL}/api/health")
    print_response("Health Check", response)
    assert response.status_code == 200
    print("✓ Health check passed")


def test_root_endpoint():
    """Test root endpoint"""
    print("\n[TEST 2] Testing Root Endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print_response("Root Endpoint", response)
    assert response.status_code == 200
    print("✓ Root endpoint passed")


def test_run_backtest():
    """Test running a backtest"""
    print("\n[TEST 3] Testing Run Backtest...")

    payload = {
        "ticker": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "short_period": 20,
        "long_period": 50,
        "initial_capital": 100000.0,
        "commission": 0.001
    }

    print(f"Request payload: {json.dumps(payload, indent=2)}")

    response = requests.post(f"{BASE_URL}/api/backtest", json=payload)
    print_response("Backtest Results", response)

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'data' in data
    assert 'performance_metrics' in data['data']
    assert 'chart_data' in data['data']

    print("✓ Backtest passed")
    return data['data']


def test_get_latest_results():
    """Test retrieving latest results"""
    print("\n[TEST 4] Testing Get Latest Results...")
    response = requests.get(f"{BASE_URL}/api/backtest/results")
    print_response("Latest Results", response)

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True

    print("✓ Get latest results passed")


def test_invalid_ticker():
    """Test with invalid ticker"""
    print("\n[TEST 5] Testing Invalid Ticker...")

    payload = {
        "ticker": "INVALIDTICKER123",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "short_period": 20,
        "long_period": 50,
        "initial_capital": 100000.0
    }

    response = requests.post(f"{BASE_URL}/api/backtest", json=payload)
    print_response("Invalid Ticker Response", response)

    # Should return 500 error for invalid ticker
    assert response.status_code == 500
    print("✓ Invalid ticker handling passed")


def test_invalid_date_range():
    """Test with invalid date range"""
    print("\n[TEST 6] Testing Invalid Date Range...")

    payload = {
        "ticker": "AAPL",
        "start_date": "2023-12-31",
        "end_date": "2023-01-01",  # End before start
        "short_period": 20,
        "long_period": 50
    }

    response = requests.post(f"{BASE_URL}/api/backtest", json=payload)
    print_response("Invalid Date Range Response", response)

    # Should return 400 error
    assert response.status_code == 400
    print("✓ Invalid date range handling passed")


def test_invalid_ma_periods():
    """Test with invalid MA periods"""
    print("\n[TEST 7] Testing Invalid MA Periods...")

    payload = {
        "ticker": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "short_period": 200,  # Short > Long
        "long_period": 50
    }

    response = requests.post(f"{BASE_URL}/api/backtest", json=payload)
    print_response("Invalid MA Periods Response", response)

    # Should return 400 error
    assert response.status_code == 400
    print("✓ Invalid MA periods handling passed")


def test_clear_results():
    """Test clearing cached results"""
    print("\n[TEST 8] Testing Clear Results...")

    # First run a backtest
    payload = {
        "ticker": "SPY",
        "start_date": "2023-01-01",
        "end_date": "2023-06-30",
        "short_period": 10,
        "long_period": 20
    }
    requests.post(f"{BASE_URL}/api/backtest", json=payload)

    # Clear results
    response = requests.delete(f"{BASE_URL}/api/backtest/results")
    print_response("Clear Results", response)

    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True

    # Try to get results (should fail)
    response = requests.get(f"{BASE_URL}/api/backtest/results")
    assert response.status_code == 404

    print("✓ Clear results passed")


def run_all_tests():
    """Run all API tests"""
    print("\n" + "=" * 70)
    print("MA GOLDEN CROSS BACKTESTER API - TEST SUITE")
    print("=" * 70)

    try:
        # Check if server is running
        try:
            requests.get(BASE_URL, timeout=2)
        except requests.exceptions.ConnectionError:
            print("\n❌ ERROR: API server is not running!")
            print("Please start the server first:")
            print("  python backend/app.py")
            print("  OR")
            print("  uvicorn backend.app:app --reload")
            return

        # Run tests
        test_health_check()
        test_root_endpoint()
        test_run_backtest()
        test_get_latest_results()
        test_invalid_ticker()
        test_invalid_date_range()
        test_invalid_ma_periods()
        test_clear_results()

        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED!")
        print("=" * 70 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
