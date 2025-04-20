#!/usr/bin/env python
# test_financial_statements.py - Testing the financial statements pipeline with proper dependency handling
import logging
import sys
import pprint
import json
from datetime import datetime
from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_profiles
from fmp_fetcher.tasks.financial_statement_tasks import fetch_and_store_statements, SUPPORTED_STATEMENT_TYPES
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

def ensure_stock_profiles_exist(symbols):
    """
    CRITICAL STEP: Ensure stock profiles exist in the database
    before attempting to fetch financial statements (FK constraint)
    """
    logger.info(f"Step 1: Ensuring stock profiles exist for {len(symbols)} symbols...")
    
    # First try to fetch profiles from FMP API
    try:
        success = fetch_and_store_profiles(symbols)
        if success:
            logger.info(f"✅ Successfully fetched and stored stock profiles from FMP API")
            return True
    except Exception as e:
        logger.warning(f"⚠️ Could not fetch profiles from FMP API: {e}")
    
    # Fall back to creating minimal test profiles if API fetch fails
    logger.info("Creating minimal stock profiles directly in the database...")
    
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

def debug_financial_statement_api(symbol, year, period):
    """Verify API response format and test parsing with real data"""
    logger.info(f"Step 2: Debugging financial statement API responses for {symbol}, {year} {period}")
    
    # Test one of the statement types
    for stmt_name in SUPPORTED_STATEMENT_TYPES[:1]:  # Just test income statement for debug
        # Use the correct endpoint format
        endpoint = f"stable/{stmt_name}-bulk"  # Critical fix: use stable/income-statement-bulk format
        params = {"year": year, "period": period}
        
        logger.info(f"Testing endpoint: {endpoint} with params: {params}")
        
        # Try with CSV handling (which is what we need for financial statements)
        api_data_csv = fmp_client.make_fmp_request(
            endpoint_path=endpoint,
            params=params,
            handle_csv=True  # Critical: enable CSV handling
        )
        
        if api_data_csv is not None:
            logger.info(f"CSV Response type: {type(api_data_csv)}")
            if isinstance(api_data_csv, list) and api_data_csv:
                # Find rows matching our target symbol
                matching_rows = [row for row in api_data_csv if row.get('symbol') == symbol]
                
                if matching_rows:
                    logger.info(f"Found {len(matching_rows)} rows matching symbol {symbol}")
                    logger.info(f"Sample row data: {matching_rows[0]}")
                    
                    # Save sample data for inspection
                    with open('sample_financial_data.json', 'w') as f:
                        json.dump(matching_rows[0], f, indent=2)
                    logger.info("Saved sample data to sample_financial_data.json for inspection")
                    
                    # Test parsing functionality
                    db_type = stmt_name.replace("-statement", "").replace("-", "")
                    try:
                        parsed = parsing.parse_bulk_financial_statements(
                            api_data_list=matching_rows,
                            statement_type=db_type,
                            target_symbols=[symbol]
                        )
                        if parsed:
                            logger.info(f"✅ Successfully parsed statement: {parsed[0]['statement_type']}")
                            # Show what will be stored in the data field
                            logger.info(f"Data field will contain {len(parsed[0]['data'].keys())} metrics")
                            return True
                        else:
                            logger.warning("❌ Parsing returned empty result")
                    except Exception as e:
                        logger.error(f"❌ Error parsing statement: {e}")
                else:
                    logger.warning(f"❌ No rows found matching symbol {symbol}")
            else:
                logger.warning("❌ CSV response had no data")
        else:
            logger.warning("❌ CSV response was None")
    
    return False

def test_financial_statements():
    """Test the complete financial statements pipeline with dependency handling"""
    # Load environment variables
    load_dotenv()
    
    # Check if FMP API key is available
    if not os.getenv("FMP_API_KEY"):
        logger.error("FMP_API_KEY not found in environment variables. Please check your .env file.")
        return False
    
    # Use a small subset of symbols for testing
    test_symbols = TARGET_SYMBOLS[:2]  # Just use 2 symbols to keep tests fast
    logger.info(f"Testing with symbols: {test_symbols}")
    
    # STEP 1: CRITICAL - Ensure stock profiles exist (required by FK constraint)
    if not ensure_stock_profiles_exist(test_symbols):
        logger.error("❌ Failed to create stock profiles - can't proceed to financial statements")
        return False
    
    # STEP 2: Debug API responses for one symbol
    symbol = test_symbols[0]  # Use the first test symbol
    
    # Try multiple years and periods to find available data
    test_combinations = [
        {"year": 2022, "period": "FY"},
        {"year": 2023, "period": "FY"},
        {"year": 2023, "period": "Q4"},
        {"year": 2024, "period": "Q1"}
    ]
    
    # Try each combination until we find data
    found_data = False
    for test_params in test_combinations:
        year = test_params["year"]
        period = test_params["period"]
        logger.info(f"Trying year={year}, period={period} for {symbol}...")
        
        if debug_financial_statement_api(symbol, year, period):
            logger.info(f"✅ Found data with year={year}, period={period}")
            found_data = True
            break
    
    if not found_data:
        logger.warning("⚠️ No financial data found in any of the test combinations")
    
    # STEP 3: Run the complete financial statements pipeline
    try:
        logger.info(f"Step 3: Full financial statements test for {year} {period}...")
        fetch_and_store_statements(test_symbols, year, period)
        logger.info("✅ Financial statements pipeline test completed")
        return True
    except Exception as e:
        logger.error(f"❌ Error during financial statements test: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting financial statements pipeline test...")
    success = test_financial_statements()
    
    if success:
        logger.info("✅ Financial statements pipeline test PASSED!")
        sys.exit(0)
    else:
        logger.error("❌ Financial statements pipeline test FAILED!")
        sys.exit(1)
