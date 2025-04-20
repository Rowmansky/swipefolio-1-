#!/usr/bin/env python
# fetch_financial_statements.py - Simple, direct financial statement fetching
import os
import sys
import logging
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from fmp_fetcher.clients import db_client
from fmp_fetcher.config import TARGET_SYMBOLS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Statement types to fetch
STATEMENT_TYPES = [
    "income-statement", 
    "balance-sheet-statement", 
    "cash-flow-statement"
]

def ensure_profiles_exist(symbols):
    """Create minimal stock profiles if needed"""
    profiles = []
    for symbol in symbols:
        profiles.append({
            'symbol': symbol,
            'company_name': f'Test Company {symbol}',
            'exchange': 'TEST',
            'industry': 'Testing',
            'sector': 'Technology',
            'country': 'USA',
            'is_actively_trading': True
        })
    
    success = db_client.update_stocks(profiles)
    if success:
        logger.info(f"✅ Stock profiles ready for {len(profiles)} symbols")
        return True
    else:
        logger.error("❌ Failed to create stock profiles")
        return False

def fetch_statements(symbols, year=None, period="FY"):
    """
    Fetch financial statements using direct API calls
    
    Args:
        symbols: List of stock symbols to fetch
        year: Calendar year (optional)
        period: FY, Q1, Q2, Q3, or Q4
    """
    # Load API key
    load_dotenv()
    api_key = os.getenv('FMP_API_KEY')
    
    if not api_key:
        logger.error("No FMP_API_KEY found in environment")
        return False
    
    # Make sure stock profiles exist first (for FK constraint)
    if not ensure_profiles_exist(symbols):
        return False
    
    all_statements = []
    
    # Process each symbol and statement type
    for symbol in symbols:
        logger.info(f"Processing {symbol}...")
        
        for stmt_type in STATEMENT_TYPES:
            # Map API statement type to database format
            db_type = stmt_type.replace("-statement", "").replace("-", "")
            
            # Construct URL exactly as shown in example
            url = f"https://financialmodelingprep.com/stable/{stmt_type}"
            params = {"symbol": symbol, "apikey": api_key}
            
            # Add period and year if specified
            if period:
                params["period"] = period
            if year:
                params["year"] = year
                
            logger.info(f"Fetching {stmt_type} for {symbol}...")
            
            try:
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list) and data:
                        logger.info(f"✅ Got {len(data)} {stmt_type} records for {symbol}")
                        
                        # Save sample for inspection
                        if len(data) > 0:
                            with open(f'sample_{symbol}_{stmt_type.replace("-", "_")}.json', 'w') as f:
                                json.dump(data[0], f, indent=2)
                        
                        # Create database records for each statement
                        for stmt in data:
                            # Create record matching database schema exactly
                            record = {
                                'symbol': symbol,
                                'report_date': stmt.get('date'),
                                'filing_date': stmt.get('filingDate'),
                                'accepted_date': stmt.get('acceptedDate'),
                                'calendar_year': int(stmt.get('fiscalYear', 0)),
                                'period': stmt.get('period'),  # Keep original case (FY, Q1, etc.)
                                'statement_type': db_type,
                                'cik': stmt.get('cik'),
                                'link': None,  # API doesn't provide this
                                'source_filing_url': None,  # API doesn't provide this
                                'data': stmt,
                                'last_fetched': datetime.now().isoformat()
                            }
                            all_statements.append(record)
                    else:
                        logger.warning(f"No {stmt_type} data found for {symbol}")
                else:
                    logger.error(f"API request failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching {stmt_type} for {symbol}: {e}")
    
    # Insert all statements into database
    if all_statements:
        logger.info(f"Inserting {len(all_statements)} statements into database...")
        try:
            # Use the update function from db_client
            success = db_client.update_financial_statements(all_statements)
            if success:
                logger.info(f"✅ Successfully inserted {len(all_statements)} statements")
                return True
            else:
                logger.error("❌ Failed to insert statements")
                return False
        except Exception as e:
            logger.error(f"Error during database insertion: {e}")
            return False
    else:
        logger.warning("No statements found to insert")
        return False

if __name__ == "__main__":
    # Use a subset of symbols for testing
    test_symbols = TARGET_SYMBOLS[:2]  # Just use first 2 for testing
    logger.info(f"Starting financial statements fetch for {test_symbols}...")
    
    # No year specified = get latest data
    success = fetch_statements(test_symbols, period="FY")
    
    if success:
        logger.info("✅ Financial statements fetch SUCCESSFUL!")
        sys.exit(0)
    else:
        logger.error("❌ Financial statements fetch FAILED!")
        sys.exit(1)
