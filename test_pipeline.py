"""
FMP Pipeline Test Script
------------------------
This script tests specific components of the FMP data pipeline
with a small set of stocks to verify functionality.
"""
import os
import sys
import logging
import argparse
from datetime import date, timedelta

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def parse_arguments():
    """Parse command line arguments for API credentials"""
    parser = argparse.ArgumentParser(description='FMP Pipeline Test Runner')
    parser.add_argument('--fmp-key', required=True, help='FMP API Key')
    parser.add_argument('--supabase-url', required=True, help='Supabase URL')
    parser.add_argument('--supabase-key', required=True, help='Supabase Service Key')
    parser.add_argument('--symbols', default="AAPL,MSFT,JPM,JNJ,XOM", 
                       help='Comma-separated list of symbols to test (default: AAPL,MSFT,JPM,JNJ,XOM)')
    parser.add_argument('--test', default='all',
                       help='Specific test to run, or "all" for all tests')
    parser.add_argument('--limit', type=int, default=5,
                       help='Limit number of items to fetch per request (default: 5)')
    return parser.parse_args()

def main():
    """Main test runner function."""
    # Parse command line arguments
    args = parse_arguments()
    
    # Set environment variables from command line arguments
    os.environ["FMP_API_KEY"] = args.fmp_key
    os.environ["SUPABASE_URL"] = args.supabase_url
    os.environ["SUPABASE_SERVICE_KEY"] = args.supabase_key
    
    # Now import modules that require environment variables
    from fmp_fetcher.utils.logging_config import setup_logging
    from fmp_fetcher.utils.db_client import supabase, get_client
    from fmp_fetcher.tasks.stock_data_tasks import (
        fetch_and_store_profiles,
        fetch_and_store_daily_prices
    )
    from fmp_fetcher.tasks.financial_statement_tasks import fetch_and_store_statements
    from fmp_fetcher.tasks.metrics_tasks import (
        fetch_and_store_key_metrics_ttm,
        fetch_and_store_fmp_scores
    )
    from fmp_fetcher.tasks.insider_trading_tasks import fetch_and_store_insider_trades
    from fmp_fetcher.tasks.news_releases_tasks import fetch_and_store_stock_news
    from fmp_fetcher.tasks.analyst_tasks import fetch_and_store_price_target_consensus
    from fmp_fetcher.tasks.dcf_tasks import fetch_and_store_dcf_valuations
    
    # Configure logging
    setup_logging()
    logger = logging.getLogger("fmp_pipeline_test")
    
    # Parse test symbols from command line
    TEST_SYMBOLS = args.symbols.split(',')
    logger.info(f"Running tests with symbols: {TEST_SYMBOLS}")
    
    # Define test functions
    def test_database_connection():
        """Test the Supabase database connection."""
        logger.info("Testing database connection...")
        try:
            client = get_client()
            # Simple query to verify connection
            result = client.table('companies').select('*').limit(1).execute()
            logger.info(f"Database connection successful. Retrieved: {result}")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    def run_company_profile_test():
        """Test fetching and storing company profiles."""
        logger.info("Testing company profile fetching...")
        try:
            result = fetch_and_store_profiles(TEST_SYMBOLS)
            logger.info(f"Company profile test completed. Result: {result}")
            return True
        except Exception as e:
            logger.error(f"Company profile test failed: {e}")
            return False

    def run_daily_prices_test():
        """Test fetching and storing daily prices."""
        yesterday = date.today() - timedelta(days=1)
        fetch_date_str = yesterday.isoformat()
        
        logger.info(f"Testing daily prices fetching for {fetch_date_str}...")
        try:
            result = fetch_and_store_daily_prices(TEST_SYMBOLS, fetch_date_str)
            logger.info(f"Daily prices test completed. Result: {result}")
            return True
        except Exception as e:
            logger.error(f"Daily prices test failed: {e}")
            return False

    def run_financial_statements_test():
        """Test fetching and storing financial statements."""
        logger.info("Testing financial statements fetching...")
        try:
            # Limiting to just a few statements for testing
            result = fetch_and_store_statements(
                TEST_SYMBOLS[:2],  # Limit to first 2 stocks for this heavy operation
                statement_types=["income-statement", "balance-sheet"],
                periods=["annual"],
                limit=2  # Just the 2 most recent statements
            )
            logger.info(f"Financial statements test completed. Result: {result}")
            return True
        except Exception as e:
            logger.error(f"Financial statements test failed: {e}")
            return False

    def run_key_metrics_test():
        """Test fetching and storing key metrics TTM."""
        logger.info("Testing key metrics TTM fetching...")
        try:
            result = fetch_and_store_key_metrics_ttm(TEST_SYMBOLS)
            logger.info(f"Key metrics TTM test completed. Result: {result}")
            return True
        except Exception as e:
            logger.error(f"Key metrics TTM test failed: {e}")
            return False

    def run_insider_trades_test():
        """Test fetching and storing insider trades."""
        logger.info("Testing insider trades fetching...")
        try:
            result = fetch_and_store_insider_trades(TEST_SYMBOLS, limit=args.limit)
            logger.info(f"Insider trades test completed. Result: {result}")
            return True
        except Exception as e:
            logger.error(f"Insider trades test failed: {e}")
            return False

    def run_stock_news_test():
        """Test fetching and storing stock news."""
        logger.info("Testing stock news fetching...")
        try:
            result = fetch_and_store_stock_news(TEST_SYMBOLS, limit=args.limit)
            logger.info(f"Stock news test completed. Result: {result}")
            return True
        except Exception as e:
            logger.error(f"Stock news test failed: {e}")
            return False

    def run_analyst_ratings_test():
        """Test fetching and storing analyst ratings."""
        logger.info("Testing analyst ratings fetching...")
        try:
            result = fetch_and_store_price_target_consensus(TEST_SYMBOLS)
            logger.info(f"Analyst ratings test completed. Result: {result}")
            return True
        except Exception as e:
            logger.error(f"Analyst ratings test failed: {e}")
            return False

    def run_dcf_valuations_test():
        """Test fetching and storing DCF valuations."""
        logger.info("Testing DCF valuations fetching...")
        try:
            result = fetch_and_store_dcf_valuations(TEST_SYMBOLS)
            logger.info(f"DCF valuations test completed. Result: {result}")
            return True
        except Exception as e:
            logger.error(f"DCF valuations test failed: {e}")
            return False

    def run_fmp_scores_test():
        """Test fetching and storing FMP scores."""
        logger.info("Testing FMP scores fetching...")
        try:
            result = fetch_and_store_fmp_scores(TEST_SYMBOLS, limit=args.limit)
            logger.info(f"FMP scores test completed. Result: {result}")
            return True
        except Exception as e:
            logger.error(f"FMP scores test failed: {e}")
            return False
    
    logger.info("=== Starting FMP Pipeline Tests ===")
    
    # First test the database connection
    if not test_database_connection():
        logger.error("Database connection test failed. Aborting further tests.")
        return
    
    # Define the test functions to run with descriptive names
    all_tests = {
        "profiles": run_company_profile_test,
        "prices": run_daily_prices_test,
        "metrics": run_key_metrics_test,
        "insider": run_insider_trades_test,
        "news": run_stock_news_test,
        "analyst": run_analyst_ratings_test,
        "scores": run_fmp_scores_test,
        "financials": run_financial_statements_test,
        "dcf": run_dcf_valuations_test,
    }
    
    # Determine which tests to run
    if args.test.lower() == 'all':
        tests_to_run = all_tests.items()
    elif args.test in all_tests:
        tests_to_run = [(args.test, all_tests[args.test])]
    else:
        logger.error(f"Unknown test: {args.test}. Available tests: {', '.join(all_tests.keys())} or 'all'")
        return
    
    # Track test results
    results = {}
    
    # Run each test
    for name, test_func in tests_to_run:
        logger.info(f"\n=== Running Test: {name} ===")
        success = test_func()
        results[name] = "SUCCESS" if success else "FAILED"
    
    # Print summary
    logger.info("\n=== Test Results Summary ===")
    for name, result in results.items():
        logger.info(f"{name}: {result}")
    
    # Overall assessment
    if all(result == "SUCCESS" for result in results.values()):
        logger.info("\n✅ All tests passed successfully!")
    else:
        failed = [name for name, result in results.items() if result != "SUCCESS"]
        logger.info(f"\n❌ Some tests failed: {failed}")

if __name__ == "__main__":
    main()
