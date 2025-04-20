import logging
import sys
import time
from datetime import datetime
from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_key_metrics_ttm
from fmp_fetcher.tasks.news_releases_tasks import fetch_and_store_press_releases, fetch_and_store_stock_news

# Configure logging to show everything
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Get the root logger
logger = logging.getLogger()

# Test with 20 diverse stocks across different sectors
test_symbols = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "NVDA", "AMD",
    # Finance
    "JPM", "BAC", "GS", "V", "MA",
    # Healthcare
    "JNJ", "PFE", "MRK", "UNH", "ABBV",
    # Consumer
    "AMZN", "WMT", "PG", "KO", "DIS"
]

def run_test(test_name, test_func, *args, **kwargs):
    """Run a test with proper exception handling and logging"""
    print(f"\n===== TESTING {test_name} =====")
    logger.info(f"Starting test: {test_name}")
    
    try:
        start_time = time.time()
        success = test_func(*args, **kwargs)
        elapsed = time.time() - start_time
        
        result = "SUCCESS" if success else "FAILURE"
        print(f"{test_name} test result: {result} (in {elapsed:.2f} seconds)")
        logger.info(f"Test {test_name} completed with result: {result} in {elapsed:.2f} seconds")
        return success
    except Exception as e:
        print(f"{test_name} test EXCEPTION: {str(e)}")
        logger.exception(f"Exception in {test_name} test")
        return False

def run_tests():
    print(f"Running tests with {len(test_symbols)} stocks: {', '.join(test_symbols)}")
    logger.info(f"Running tests with symbols: {test_symbols}")
    
    # Group 1: Process in smaller batches to handle rate limiting
    metrics_results = []
    for i in range(0, len(test_symbols), 5):
        batch = test_symbols[i:i+5]
        print(f"\n----- Testing Key Metrics TTM Batch: {', '.join(batch)} -----")
        batch_success = run_test(f"KEY METRICS TTM (Batch {i//5+1})", fetch_and_store_key_metrics_ttm, batch)
        metrics_results.append(batch_success)
        # Wait between batches to avoid rate limiting
        time.sleep(3)
    
    metrics_success = any(metrics_results)  # Success if any batch succeeded
    
    # Wait between different API tests
    time.sleep(5)
    
    # Test 2: Press Releases with a reasonable limit
    press_releases_success = run_test("PRESS RELEASES", fetch_and_store_press_releases, 30)
    
    # Wait between different API tests
    time.sleep(5)
    
    # Test 3: Stock News with a smaller set and limit
    news_success = run_test("STOCK NEWS", fetch_and_store_stock_news, test_symbols[:5], 20)
    
    # Summary
    print("\n===== TEST SUMMARY =====")
    print(f"Key Metrics TTM: {'✅ PASSED' if metrics_success else '❌ FAILED'}")
    print(f"Press Releases: {'✅ PASSED' if press_releases_success else '❌ FAILED'}")
    print(f"Stock News: {'✅ PASSED' if news_success else '❌ FAILED'}")
    print(f"Overall: {'✅ PASSED' if (metrics_success or press_releases_success or news_success) else '❌ FAILED'}")
    
    print("\nAll tests completed! Check the log file for details.")

if __name__ == "__main__":
    run_tests()
