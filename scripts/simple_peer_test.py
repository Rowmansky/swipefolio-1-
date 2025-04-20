"""
Simple direct test of our updated stock peers implementation
"""
import logging
from fmp_fetcher.tasks.misc_data_tasks import fetch_and_store_peers

# Configure logging
logging.basicConfig(level=logging.INFO)

# Test with known working symbols
test_symbols = ["AMZN", "BABA", "ETSY"]
print(f"\nTesting stock peers with symbols: {test_symbols}")

# Call the function directly
result = fetch_and_store_peers(test_symbols)
print(f"\nFetch and store result: {result}")
