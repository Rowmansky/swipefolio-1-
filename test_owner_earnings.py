#!/usr/bin/env python
# test_owner_earnings.py
import logging
import sys
import pprint
from fmp_fetcher.tasks.owner_earnings_tasks import fetch_and_store_owner_earnings_historical
from fmp_fetcher.config import TARGET_SYMBOLS
from fmp_fetcher.clients import db_client, fmp_client
from fmp_fetcher.utils import parsing
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def create_test_stock_profiles(symbols):
    """Create minimal stock profiles directly in the database for testing."""
    logger.info(f"Creating minimal stock profiles for {len(symbols)} symbols...")
    
    # Create minimal stock profiles for testing
    profiles = []
    for symbol in symbols:
        profile = {
            'symbol': symbol,
            'company_name': f'Test Company {symbol}',
            'exchange': 'TEST',
            'industry': 'Testing',
            'sector': 'Technology',
            'country': 'USA',
            'is_actively_trading': True
        }
        profiles.append(profile)
    
    try:
        # Insert directly into the stocks table
        success = db_client.update_stocks(profiles)
        if success:
            logger.info(f"✅ Successfully created {len(profiles)} test stock profiles")
            return True
        else:
            logger.error("❌ Failed to create test stock profiles")
            return False
    except Exception as e:
        logger.error(f"❌ Error creating test stock profiles: {e}")
        return False

def debug_owner_earnings_api_response(symbol, limit=5):
    """Debug the owner earnings API response for a specific symbol."""
    logger.info(f"Debugging owner earnings API response for {symbol} with limit {limit}")
    
    endpoint_path = f"/owner-earnings/{symbol}"
    params = {'limit': limit}
    
    api_data = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
    
    if api_data is None:
        logger.error(f"No data returned for owner earnings of {symbol}")
        return
        
    # Print the raw API response
    logger.info(f"API Response TYPE for owner earnings: {type(api_data)}")
    logger.info(f"API Response for owner earnings of {symbol}:")
    pprint.pprint(api_data[:2] if isinstance(api_data, list) and len(api_data) > 2 else api_data)
    
    # Check if it's a list and has items
    if isinstance(api_data, list):
        logger.info(f"Response is a list with {len(api_data)} items")
        if api_data:
            logger.info(f"First item keys: {api_data[0].keys() if isinstance(api_data[0], dict) else 'Not a dict'}")
            
            # Try parsing the first item
            try:
                parsed = parsing.parse_owner_earnings(api_data[0], symbol)
                if parsed:
                    logger.info(f"Successfully parsed owner earnings: {parsed}")
                else:
                    logger.error(f"Parsing returned None for owner earnings")
            except Exception as e:
                logger.error(f"Error parsing owner earnings: {e}")
    else:
        logger.error(f"Unexpected data type: {type(api_data)}")

def test_owner_earnings():
    """Test the owner earnings fetching and parsing functionality."""
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
        logger.error("Failed to create stock profiles, which are required before owner earnings.")
        return False
    
    # Step 2: Debug API responses for one symbol
    symbol = test_symbols[0]  # Use the first test symbol
    debug_owner_earnings_api_response(symbol, limit=5)
    
    # Step 3: Run the owner earnings fetching and storing function
    try:
        logger.info("Fetching and storing owner earnings...")
        fetch_and_store_owner_earnings_historical(test_symbols, limit=5)
        logger.info("Owner earnings test completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during owner earnings test: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting owner earnings functionality test...")
    success = test_owner_earnings()
    
    if success:
        logger.info("✅ Owner earnings test passed!")
        sys.exit(0)
    else:
        logger.error("❌ Owner earnings test failed!")
        sys.exit(1)
