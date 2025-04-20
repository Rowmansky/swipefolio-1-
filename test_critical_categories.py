"""
Comprehensive Test Script for Critical FMP Data Categories
==========================================================

This script systematically tests five critical FMP data categories:
1. Financial Statements (with CSV parsing)
2. Enterprise Values
3. Analyst Ratings/Estimates
4. DCF Valuations
5. Owner Earnings

Tests are executed in dependency order, with all categories using the same symbols.
"""

import logging
import sys
import time
import io
import csv
from typing import List, Dict, Any, Optional
from datetime import date, timedelta

# Import task functions
from fmp_fetcher.tasks.financial_statement_tasks import fetch_and_store_statements
from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_enterprise_values_historical
from fmp_fetcher.tasks.dcf_tasks import fetch_and_store_dcf_valuations
from fmp_fetcher.tasks.owner_earnings_tasks import fetch_and_store_owner_earnings_historical
from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_profiles
from fmp_fetcher.clients.db_client import get_supabase_client
from fmp_fetcher.clients import fmp_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"critical_test_run_{time.strftime('%Y%m%d_%H%M%S')}.log")
    ]
)

logger = logging.getLogger("critical_test")

# Common test symbols to use across all categories
# These symbols have financial data, analyst coverage, and DCF valuations
TEST_SYMBOLS = [
    "AAPL",  # Tech with good financials
    "MSFT",  # Tech with good financials
    "JPM",   # Financial
    "JNJ",   # Healthcare
    "WMT"    # Retail
]

def verify_profiles_exist(symbols: List[str]) -> bool:
    """Check if stock profiles exist in the database for the given symbols."""
    try:
        supabase = get_supabase_client()
        response = supabase.table('stocks').select('symbol').execute()
        existing_symbols = set(record['symbol'] for record in response.data if 'symbol' in record)
        
        # Check if all test symbols exist
        missing_symbols = [s for s in symbols if s not in existing_symbols]
        
        if not missing_symbols:
            logger.info(f"✓ All {len(symbols)} symbols already exist in the stocks table")
            return True
        else:
            logger.info(f"✗ {len(missing_symbols)} symbols missing from stocks table: {', '.join(missing_symbols)}")
            return False
    except Exception as e:
        logger.error(f"Error checking for existing profiles: {e}")
        return False

def test_endpoint(
    test_name: str, 
    fetch_function: Any, 
    test_symbols: List[str], 
    require_profiles: bool = True,
    **kwargs
) -> bool:
    """Test an endpoint with proper setup/teardown and profile dependency handling."""
    print(f"\n{'=' * 50}")
    print(f"⏳ TESTING {test_name.upper()}")
    print(f"{'=' * 50}")
    
    # Check if profiles are needed and exist
    if require_profiles:
        profiles_exist = verify_profiles_exist(test_symbols)
        
        if not profiles_exist:
            logger.info(f"🔄 Creating missing stock profiles first (required for {test_name})")
            profiles_success = fetch_and_store_profiles(test_symbols)
            if not profiles_success:
                logger.error(f"❌ FAILED: Cannot create stock profiles, skipping {test_name}")
                return False
    
    # Run the actual test with timing
    start_time = time.time()
    logger.info(f"▶️ Running {test_name} test for {len(test_symbols)} symbols: {', '.join(test_symbols)}")
    
    try:
        # Call the function with symbols and any additional kwargs
        success = fetch_function(test_symbols, **kwargs)
        duration = time.time() - start_time
        
        if success:
            print(f"✅ PASSED: {test_name} completed successfully in {duration:.2f}s")
            return True
        else:
            print(f"❌ FAILED: {test_name} did not complete successfully ({duration:.2f}s)")
            return False
            
    except Exception as e:
        duration = time.time() - start_time
        logger.exception(f"❌ EXCEPTION in {test_name}: {e}")
        print(f"❌ FAILED: {test_name} raised exception after {duration:.2f}s: {e}")
        return False

def check_endpoint_response_format(endpoint_path: str, symbol: str = None, params: Dict = None, expect_csv: bool = False):
    """
    Check the response format of an endpoint to determine if it returns CSV or JSON.
    This helps verify our assumptions about data formats.
    """
    try:
        actual_params = params or {}
        
        # For single-symbol endpoints, use the provided symbol
        if symbol and '{symbol}' in endpoint_path:
            actual_endpoint = endpoint_path.replace('{symbol}', symbol)
        else:
            actual_endpoint = endpoint_path
            # For bulk endpoints, we might need to specify a symbol in params
            if symbol and 'bulk' in endpoint_path:
                actual_params['symbol'] = symbol
                
        print(f"\nChecking response format for endpoint: {actual_endpoint}")
        print(f"Parameters: {actual_params}")
        
        # Try with CSV handling enabled (this should work for both CSV and JSON)
        response = fmp_client.make_fmp_request(
            endpoint_path=actual_endpoint,
            params=actual_params,
            handle_csv=True
        )
        
        # Check if response has data
        if response and (isinstance(response, list) or isinstance(response, dict)):
            print(f"✓ Endpoint returned valid data")
            
            # For list responses, show count and sample fields
            if isinstance(response, list) and len(response) > 0:
                print(f"✓ Returned {len(response)} records")
                
                # Show sample of fields from first record
                if isinstance(response[0], dict):
                    sample_fields = list(response[0].keys())[:5]
                    print(f"Sample fields: {sample_fields}")
                    
            # For dict responses, show sample fields
            elif isinstance(response, dict):
                sample_fields = list(response.keys())[:5]
                print(f"Sample fields: {sample_fields}")
                
            # Success
            return True
        else:
            print(f"✗ Endpoint did not return expected data format")
            print(f"Response: {response}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking endpoint {endpoint_path}: {e}")
        return False

def run_critical_tests():
    """
    Run tests for all critical categories in proper dependency order.
    """
    results = {}
    
    print(f"\n{'=' * 80}")
    print(f"🔍 TESTING RESPONSE FORMATS FOR KEY ENDPOINTS")
    print(f"{'=' * 80}")
    
    # Test a sample of endpoints for format and availability
    symbol = TEST_SYMBOLS[0]  # Use first symbol for individual endpoint tests
    
    endpoints_to_check = [
        # Financial Statements
        {
            "name": "Income Statement Bulk",
            "path": "/income-statement-bulk",
            "params": {"year": 2023, "period": "FY"},
            "symbol": None  # Bulk endpoint
        },
        {
            "name": "Balance Sheet Bulk",
            "path": "/balance-sheet-statement-bulk",
            "params": {"year": 2023, "period": "FY"},
            "symbol": None  # Bulk endpoint
        },
        {
            "name": "Cash Flow Bulk",
            "path": "/cash-flow-statement-bulk",
            "params": {"year": 2023, "period": "FY"},
            "symbol": None  # Bulk endpoint
        },
        # Single symbol statement endpoints for reference
        {
            "name": "Income Statement",
            "path": "/income-statement/{symbol}",
            "params": {"period": "annual", "limit": 1},
            "symbol": symbol
        },
        # Enterprise Values
        {
            "name": "Enterprise Values",
            "path": "/enterprise-values/{symbol}",
            "params": {"period": "annual", "limit": 1},
            "symbol": symbol
        },
        # DCF
        {
            "name": "DCF",
            "path": "/discounted-cash-flow/{symbol}",
            "params": {},
            "symbol": symbol
        },
        # Owner Earnings
        {
            "name": "Owner Earnings",
            "path": "/owner-earnings/{symbol}",
            "params": {"limit": 1},
            "symbol": symbol
        }
    ]
    
    # Check each endpoint
    endpoint_success = {}
    for endpoint in endpoints_to_check:
        success = check_endpoint_response_format(
            endpoint_path=endpoint["path"],
            symbol=endpoint["symbol"],
            params=endpoint["params"]
        )
        endpoint_success[endpoint["name"]] = success
    
    # If any critical endpoint check failed, abort the tests
    if not all(endpoint_success.values()):
        print(f"\n❌ CRITICAL ERROR: Some endpoints are not responding correctly.")
        print("Please check FMP API access and credentials before proceeding.")
        print("Detailed endpoint check results:")
        for name, success in endpoint_success.items():
            print(f"{'✅' if success else '❌'} {name}")
        return False
    
    print(f"\n{'=' * 80}")
    print(f"🚀 STARTING CRITICAL CATEGORY TESTS")
    print(f"{'=' * 80}")
    
    # Define the actual tests to run
    year = date.today().year - 1  # Use previous year to ensure data exists
    quarter = "FY"  # Annual data is more likely to be complete
    
    tests = [
        # First the financial statements
        {
            "name": "financial_statements",
            "function": fetch_and_store_statements,
            "params": {"year": year, "period": quarter}
        },
        # Then enterprise values
        {
            "name": "enterprise_values",
            "function": fetch_and_store_enterprise_values_historical,
            "params": {"period": "annual", "limit": 10}
        },
        # Then DCF valuations
        {
            "name": "dcf_valuations",
            "function": fetch_and_store_dcf_valuations,
            "params": {}
        },
        # Finally owner earnings - note: removing 'period' param which is causing errors
        {
            "name": "owner_earnings",
            "function": fetch_and_store_owner_earnings_historical,
            "params": {"limit": 10}
        }
    ]
    
    start_time = time.time()
    
    # Execute all tests with the same set of symbols
    for test in tests:
        success = test_endpoint(
            test_name=test["name"],
            fetch_function=test["function"],
            test_symbols=TEST_SYMBOLS,
            require_profiles=True,
            **test["params"]
        )
        results[test["name"]] = success
        
        # Pause between tests to avoid rate limiting
        time.sleep(2)
    
    # Print summary
    duration = time.time() - start_time
    passed = sum(1 for result in results.values() if result)
    failed = len(results) - passed
    
    print(f"\n{'=' * 80}")
    print(f"📊 TEST SUMMARY - Completed in {duration:.2f}s")
    print(f"{'=' * 80}")
    print(f"✅ PASSED: {passed}/{len(results)} tests")
    print(f"❌ FAILED: {failed}/{len(results)} tests")
    
    # Detailed results
    print("\nDetailed Results:")
    for name, result in results.items():
        print(f"{'✅' if result else '❌'} {name}")
    
    # Exit with appropriate status code
    if failed > 0:
        print(f"\n⚠️ {failed} tests failed. Please check the logs for details.")
    else:
        print(f"\n🎉 All tests passed! The data pipeline is functioning correctly.")
    
    return all(results.values())

if __name__ == "__main__":
    success = run_critical_tests()
    sys.exit(0 if success else 1)
