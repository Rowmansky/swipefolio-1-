import logging
import sys
import time
from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_key_metrics_ttm
from fmp_fetcher.tasks.news_releases_tasks import fetch_and_store_press_releases
from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_profiles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

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

def test_profiles():
    print("\n===== TESTING STOCK PROFILES (PREREQUISITE) =====")
    success = fetch_and_store_profiles(test_symbols)
    print(f"Stock profiles result: {'SUCCESS' if success else 'FAILURE'}")
    return success

def test_metrics_ttm():
    print("\n===== TESTING OPTIMIZED KEY METRICS TTM =====")
    success = fetch_and_store_key_metrics_ttm(test_symbols)
    print(f"Key metrics TTM result: {'SUCCESS' if success else 'FAILURE'}")
    return success

def test_press_releases():
    print("\n===== TESTING FIXED PRESS RELEASES =====")
    # Test with a smaller subset of symbols for press releases
    test_subset = ["AAPL", "MSFT", "AMZN", "JPM", "JNJ"]
    success = fetch_and_store_press_releases(test_subset, limit=10)
    print(f"Press releases result: {'SUCCESS' if success else 'FAILURE'}")
    return success

if __name__ == "__main__":
    print("Testing financial data pipeline fixes...")
    
    # Step 1: First fetch stock profiles (prerequisite for metrics)
    profiles_success = test_profiles()
    
    # Wait a bit before next test
    time.sleep(3)
    
    # Step 2: Test metrics TTM with our combined parser
    metrics_success = test_metrics_ttm()
    
    # Wait a bit before next test
    time.sleep(3)
    
    # Step 3: Test press releases with the correct endpoint
    press_releases_success = test_press_releases()
    
    print("\n===== TEST SUMMARY =====")
    print(f"Stock Profiles: {'✅ PASSED' if profiles_success else '❌ FAILED'}")
    print(f"Key Metrics TTM: {'✅ PASSED' if metrics_success else '❌ FAILED'}")
    print(f"Press Releases: {'✅ PASSED' if press_releases_success else '❌ FAILED'}")
    
    if profiles_success and metrics_success and press_releases_success:
        print("\n🎉 All tests passed! The fixes are working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the log messages for details.")
