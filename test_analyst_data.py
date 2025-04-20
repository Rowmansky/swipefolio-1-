#!/usr/bin/env python
# test_analyst_data.py
import logging
import sys
import pprint
from fmp_fetcher.tasks.analyst_tasks import (
    fetch_and_store_price_target_consensus,
    fetch_and_store_ratings_snapshot,
    fetch_and_store_current_grades
)
from fmp_fetcher.config import TARGET_SYMBOLS
from fmp_fetcher.clients import db_client, fmp_client
from fmp_fetcher.utils import parsing
from dotenv import load_dotenv
import os

# Configure root logging at DEBUG for full visibility
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_test_stock_profiles(symbols):
    """Create minimal stock profiles directly in the database for testing."""
    logger.info(f"Creating minimal stock profiles for {len(symbols)} symbols...")
    
    # Create and upsert minimal stock profiles for testing
    profiles = []
    for symbol in symbols:
        profiles.append({
            'symbol': symbol,
            'company_name': f'Test Company {symbol}',
            'exchange': 'TEST',
            'industry': 'Testing',
            'is_actively_trading': True,
        })
    success = db_client.update_stocks(profiles)
    if success:
        logger.info("✅ Test stock profiles upserted for %d symbols.", len(symbols))
    else:
        logger.error("❌ Failed to upsert test stock profiles.")

def debug_analyst_api_response(symbol):
    """Debug the analyst API response for a specific symbol."""
    logger.info(f"Debugging analyst API response for {symbol}")
    
    # Test price target consensus endpoint
    endpoint_path = "/price-target-consensus"
    params = {'symbol': symbol}
    
    api_data = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
    
    if api_data is None:
        logger.error(f"No data returned for price target consensus of {symbol}")
    else:
        # Print the raw API response
        logger.info(f"API Response TYPE for price target consensus: {type(api_data)}")
        logger.info(f"API Response for price target consensus of {symbol}:")
        pprint.pprint(api_data)
        
        # Try parsing if it's a list
        if isinstance(api_data, list) and api_data:
            try:
                parsed = parsing.parse_analyst_rating(api_data[0], source='FMP Price Target Consensus')
                if parsed:
                    logger.info(f"Successfully parsed price target consensus: {parsed}")
                else:
                    logger.error(f"Parsing returned None for price target consensus")
            except Exception as e:
                logger.error(f"Error parsing price target consensus: {e}")

def test_analyst_data():
    """Test the analyst data fetching and parsing functionality."""
    # Load environment variables
    load_dotenv()
    
    # Check if FMP API key is available
    if not os.getenv("FMP_API_KEY"):
        logger.error("FMP_API_KEY not found in environment variables. Please check your .env file.")
        return False
    
    # Use a small subset of symbols for testing
    test_symbols = TARGET_SYMBOLS[:2]  # Just use the first 2 symbols from the config
    logger.info(f"Testing with symbols: {test_symbols}")
    
    # Step 1: First create test stock profiles (required due to FK constraints)
    if not create_test_stock_profiles(test_symbols):
        logger.error("Failed to create stock profiles, which are required before analyst data.")
        return False
    
    # Step 2: Debug API responses for one symbol
    symbol = test_symbols[0]  # Use the first test symbol
    debug_analyst_api_response(symbol)
    
    # Step 3: Run the analyst data fetching and storing functions
    success = True
    try:
        # Test price target consensus
        logger.info("Fetching and storing price target consensus...")
        fetch_and_store_price_target_consensus(test_symbols)
        
        # Test ratings snapshot
        logger.info("Fetching and storing ratings snapshot...")
        fetch_and_store_ratings_snapshot(test_symbols)
        
        # Test current grades
        logger.info("Fetching and storing current grades...")
        fetch_and_store_current_grades(test_symbols)
        
        logger.info("Analyst data tests completed successfully")
    except Exception as e:
        logger.error(f"Error during analyst data test: {e}")
        success = False
    
    return success

if __name__ == "__main__":
    # Load environment and prepare symbols
    load_dotenv()
    symbols = sys.argv[1:] if len(sys.argv) > 1 else TARGET_SYMBOLS
    logger.info("Preparing test run for symbols: %s", symbols)

    # Ensure stock profiles exist for FK constraints
    create_test_stock_profiles(symbols)

    # Fetch and store analyst data types
    fetch_and_store_price_target_consensus(symbols)
    fetch_and_store_ratings_snapshot(symbols)
    fetch_and_store_current_grades(symbols)
    logger.info("✅ Completed analyst data fetch and upsert.")
