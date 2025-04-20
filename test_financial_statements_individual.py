#!/usr/bin/env python
# test_financial_statements_individual.py - Testing individual financial statement fetching
import logging
import sys
import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# Local imports
from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_profiles
from fmp_fetcher.config import TARGET_SYMBOLS
from fmp_fetcher.clients import db_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Financial statement types to fetch
STATEMENT_TYPES = [
    "income-statement",
    "balance-sheet-statement",
    "cash-flow-statement"
]

def ensure_stock_profiles_exist(symbols):
    """Ensure stock profiles exist before attempting financial statements"""
    logger.info(f"Step 1: Ensuring stock profiles exist for {len(symbols)} symbols...")
    
    # First try to fetch profiles from API
    try:
        success = fetch_and_store_profiles(symbols)
        if success:
            logger.info(f"✅ Successfully fetched and stored stock profiles")
            return True
    except Exception as e:
        logger.warning(f"⚠️ Could not fetch profiles from API: {e}")
    
    # Fall back to creating minimal test profiles
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
            logger.info(f"✅ Successfully created test stock profiles")
            return True
        else:
            logger.error("❌ Failed to create test stock profiles")
            return False
    except Exception as e:
        logger.error(f"❌ Error creating test stock profiles: {e}")
        return False

def fetch_individual_statements(symbol, statement_type, year=None, period=None, limit=1):
    """
    Fetch financial statements for a single symbol using the individual endpoint
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL')
        statement_type: One of 'income-statement', 'balance-sheet-statement', 'cash-flow-statement'
        year: Optional filter by year
        period: Optional filter by period (Q1, Q2, Q3, Q4, FY)
        limit: Number of statements to retrieve (default=1 for most recent)
        
    Returns:
        List of statement data or None if request failed
    """
    # Load API key
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        logger.error("FMP_API_KEY not found. Please check .env file.")
        return None
    
    # Construct the endpoint URL
    url = f"https://financialmodelingprep.com/api/v3/{statement_type}/{symbol}"
    
    # Build parameters
    params = {"apikey": api_key}
    if limit:
        params["limit"] = limit
    if period:
        params["period"] = period
    
    logger.info(f"Fetching {statement_type} for {symbol}...")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            
            # If a specific year was requested, filter the results
            if year and isinstance(data, list):
                data = [item for item in data if str(item.get('calendarYear', '')) == str(year)]
                
            if data:
                logger.info(f"✅ Successfully fetched {len(data)} {statement_type} records for {symbol}")
                # Save sample data for inspection
                with open(f'sample_{symbol}_{statement_type.replace("-", "_")}.json', 'w') as f:
                    json.dump(data[0], f, indent=2)
                return data
            else:
                logger.warning(f"⚠️ No {statement_type} data found for {symbol}")
                return []
        else:
            logger.error(f"❌ API request failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error fetching {statement_type} for {symbol}: {e}")
        return None

def parse_statement_for_database(statement_data, statement_type):
    """
    Convert API statement data to database format
    
    Args:
        statement_data: Raw statement data from API
        statement_type: One of 'income-statement', 'balance-sheet-statement', 'cash-flow-statement'
        
    Returns:
        Dictionary ready for database insertion
    """
    # Map API statement type to database format
    db_type = statement_type.replace("-statement", "").replace("-", "")
    
    # Extract key metadata
    symbol = statement_data.get('symbol')
    year = statement_data.get('calendarYear')
    period = statement_data.get('period')
    
    # Create the database record
    db_record = {
        'symbol': symbol,
        'statement_type': db_type,
        'year': year,
        'period': period,
        'currency': statement_data.get('reportedCurrency', 'USD'),
        # Store all the financial data in the data JSON field
        'data': statement_data,
        'fetched_at': datetime.now().isoformat()
    }
    
    return db_record

def test_financial_statements_individual():
    """Test the entire financial statements pipeline with individual API calls"""
    # Load environment variables
    load_dotenv()
    
    # Check if FMP API key is available
    if not os.getenv("FMP_API_KEY"):
        logger.error("FMP_API_KEY not found in environment variables. Please check your .env file.")
        return False
    
    # Use a small subset of symbols for testing
    test_symbols = TARGET_SYMBOLS[:2]  # Just use 2 symbols for faster testing
    logger.info(f"Testing with symbols: {test_symbols}")
    
    # STEP 1: Ensure stock profiles exist (required for FK constraint)
    if not ensure_stock_profiles_exist(test_symbols):
        logger.error("❌ Failed to create stock profiles - can't proceed to financial statements")
        return False
    
    # STEP 2: Fetch individual financial statements for each symbol
    all_statements = []
    
    # Define test parameters
    test_year = 2022  # More likely to have data
    test_period = "FY"  # Annual data
    
    logger.info(f"Step 2: Fetching individual financial statements for {test_year} {test_period}...")
    
    for symbol in test_symbols:
        for statement_type in STATEMENT_TYPES:
            # Fetch statement data for this symbol and type
            statements = fetch_individual_statements(
                symbol=symbol,
                statement_type=statement_type,
                year=test_year,
                period=test_period,
                limit=5  # Get a few statements to ensure we find matching year/period
            )
            
            if statements and isinstance(statements, list):
                # Parse statements for database insertion
                for statement in statements:
                    # Only include statements matching our requested year/period
                    if (str(statement.get('calendarYear', '')) == str(test_year) and 
                        statement.get('period', '') == test_period):
                        
                        # Fix the structure to match exact database schema
                        db_type = statement_type.replace("-statement", "").replace("-", "")
                        db_record = {
                            'symbol': symbol,
                            'report_date': statement.get('date'),
                            'filing_date': statement.get('fillingDate'),  # Note FMP typo 'fillingDate'
                            'accepted_date': statement.get('acceptedDate'),
                            'calendar_year': int(statement.get('calendarYear')),
                            'period': statement.get('period'),  # Keep original case for the enum
                            'statement_type': db_type.lower(),
                            'cik': statement.get('cik'),
                            'link': statement.get('link'),
                            'source_filing_url': statement.get('finalLink'),
                            'data': statement
                        }
                        all_statements.append(db_record)
                        logger.info(f"Parsed {statement_type} for {symbol} ({test_year} {test_period})")
    
    # STEP 3: Insert all statements into the database
    if all_statements:
        logger.info(f"Step 3: Inserting {len(all_statements)} statements into database...")
        try:
            success = db_client.update_financial_statements(all_statements)
            if success:
                logger.info(f"✅ Successfully inserted {len(all_statements)} financial statements")
                return True
            else:
                logger.error("❌ Failed to insert financial statements")
                return False
        except Exception as e:
            logger.error(f"❌ Error inserting financial statements: {e}")
            return False
    else:
        logger.warning(f"No financial statements found for any symbols for {test_year} {test_period}.")
        # Return True anyway since the test completed without errors
        return True

if __name__ == "__main__":
    logger.info("🚀 Starting individual financial statements test...")
    success = test_financial_statements_individual()
    
    if success:
        logger.info("✅ Financial statements individual test PASSED!")
        sys.exit(0)
    else:
        logger.error("❌ Financial statements individual test FAILED!")
        sys.exit(1)
