#!/usr/bin/env python
# test_dcf_functionality.py
import logging
import sys
import json
import pprint
from fmp_fetcher.tasks.dcf_tasks import fetch_and_store_dcf_valuations
from fmp_fetcher.config import TARGET_SYMBOLS
from fmp_fetcher.clients import fmp_client, db_client
from fmp_fetcher.utils import parsing
from fmp_fetcher.utils.parsing import safe_decimal
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

def debug_dcf_api_response(symbol):
    """Debug the DCF API response for a specific symbol."""
    # Define the DCF types to fetch
    dcf_types = [
        {"path": "/discounted-cash-flow", "type": "Standard"},
        {"path": "/levered-discounted-cash-flow", "type": "Levered"}
    ]
    
    for dcf_config in dcf_types:
        endpoint_path = dcf_config["path"]
        dcf_type = dcf_config["type"]
        params = {'symbol': symbol}
        
        logger.info(f"Fetching {dcf_type} DCF for {symbol} from {endpoint_path}")
        api_data = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
        
        if api_data is None:
            logger.error(f"No data returned for {dcf_type} DCF of {symbol}")
            continue
            
        # Print the raw API response
        logger.info(f"API Response TYPE for {dcf_type} DCF: {type(api_data)}")
        logger.info(f"API Response for {dcf_type} DCF of {symbol}:")
        pprint.pprint(api_data)
        
        # Check if it's a list and has items
        if isinstance(api_data, list):
            logger.info(f"Response is a list with {len(api_data)} items")
            if api_data:
                logger.info(f"First item keys: {api_data[0].keys() if isinstance(api_data[0], dict) else 'Not a dict'}")
        elif isinstance(api_data, dict):
            logger.info(f"Response is a dict with keys: {api_data.keys()}")
        
        # Try parsing manually to debug
        try:
            # Manual parsing to debug
            if isinstance(api_data, list):
                if not api_data:
                    logger.error("API returned empty list")
                    continue
                valuation_data = api_data[0]
            elif isinstance(api_data, dict):
                valuation_data = api_data
            else:
                logger.error(f"Unexpected data type: {type(api_data)}")
                continue
                
            logger.info(f"Valuation data: {valuation_data}")
            
            # Check required fields
            if not valuation_data.get('symbol'):
                logger.error("Missing 'symbol' field in valuation data")
            if not valuation_data.get('date'):
                logger.error("Missing 'date' field in valuation data")
                
            # Try to extract DCF value
            dcf_value = valuation_data.get('dcf')
            if dcf_value is None:
                logger.error("Missing 'dcf' field in valuation data")
            else:
                logger.info(f"DCF value: {dcf_value}")
                
            # Try to extract stock price
            stock_price = valuation_data.get('Stock Price') or valuation_data.get('stockPrice')
            if stock_price is None:
                logger.error("Missing stock price field in valuation data")
            else:
                logger.info(f"Stock price: {stock_price}")
                
            # Try creating the record manually
            record = {
                'symbol': valuation_data.get('symbol'),
                'date': valuation_data.get('date'),
                'dcf_type': dcf_type,
                'dcf_value': safe_decimal(dcf_value),
                'stock_price_at_calc': safe_decimal(stock_price)
            }
            logger.info(f"Manually created record: {record}")
            
            # Now try the actual parsing function
            parsed = parsing.parse_dcf_valuation(api_data, dcf_type)
            if parsed:
                logger.info(f"Successfully parsed {dcf_type} DCF: {parsed}")
            else:
                logger.error(f"Parsing returned None for {dcf_type} DCF")
        except Exception as e:
            logger.error(f"Error parsing {dcf_type} DCF: {e}")

def test_dcf_functionality():
    """Test the DCF valuation fetching and parsing functionality."""
    # Load environment variables
    load_dotenv()
    
    # Check if FMP API key is available
    if not os.getenv("FMP_API_KEY"):
        logger.error("FMP_API_KEY not found in environment variables. Please check your .env file.")
        return False
    
    # Use a small subset of symbols for testing
    test_symbols = TARGET_SYMBOLS[:3]  # Just use the first 3 symbols from the config
    logger.info(f"Testing with symbols: {test_symbols}")
    
    # Step 1: First create test stock profiles (required due to FK constraints)
    if not create_test_stock_profiles(test_symbols):
        logger.error("Failed to create stock profiles, which are required before DCF valuations.")
        return False
    
    # Step 2: Debug API responses for one symbol
    symbol = test_symbols[0]  # Use the first test symbol
    logger.info(f"Debugging DCF API responses for {symbol}")
    debug_dcf_api_response(symbol)
    
    # Step 3: Run the DCF fetching and storing function
    try:
        logger.info("Fetching and storing DCF valuations...")
        fetch_and_store_dcf_valuations(test_symbols)
        logger.info("DCF functionality test completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during DCF functionality test: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting DCF functionality test...")
    success = test_dcf_functionality()
    
    if success:
        logger.info("✅ DCF functionality test passed!")
        sys.exit(0)
    else:
        logger.error("❌ DCF functionality test failed!")
        sys.exit(1)
