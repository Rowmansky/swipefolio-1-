#!/usr/bin/env python
# fix_financial_statements.py - Dead simple with HARDCODED ENUM VALUES
import os
import sys
import logging
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from fmp_fetcher.clients import db_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

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

def fetch_financial_statements(symbols):
    """Fetch financial statements for given symbols"""
    # Load API key
    load_dotenv()
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        logger.error("FMP_API_KEY not found in environment")
        return False
    
    # Ensure profiles exist first (for FK constraint)
    if not ensure_profiles_exist(symbols):
        return False
    
    # Fetch statements for each symbol
    all_statements = []
    
    # Statement types to fetch with their corresponding DB enum values
    statement_configs = [
        {"endpoint": "income-statement", "db_enum": "income"},
        {"endpoint": "balance-sheet-statement", "db_enum": "balance"},
        {"endpoint": "cash-flow-statement", "db_enum": "cashflow"}
    ]
    
    for symbol in symbols:
        logger.info(f"Processing {symbol}...")
        
        for config in statement_configs:
            endpoint = config["endpoint"]
            db_type = config["db_enum"]
            
            # Build the URL
            url = f"https://financialmodelingprep.com/stable/{endpoint}"
            params = {"symbol": symbol, "apikey": api_key}
            
            logger.info(f"Fetching {endpoint} for {symbol}...")
            
            try:
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if isinstance(data, list) and data:
                        logger.info(f"✅ Got {len(data)} {endpoint} records for {symbol}")
                        
                        # Save a sample for debugging
                        with open(f"sample_{symbol}_{endpoint.replace('-', '_')}.json", "w") as f:
                            json.dump(data[0], f, indent=2)
                        
                        # Create records for database - with HARDCODED ENUM values
                        for item in data:
                            # HARDCODED: Only use values we KNOW are correct
                            record = {
                                'symbol': symbol,
                                'report_date': item.get('date'),
                                'filing_date': item.get('filingDate'),
                                'accepted_date': item.get('acceptedDate', None),
                                'calendar_year': int(item.get('fiscalYear', 0)),
                                'period': 'annual',  # HARDCODED: Use 'annual' for the enum
                                'statement_type': db_type,  # Use the correct enum value for each statement type
                                'cik': item.get('cik'),
                                'data': item
                            }
                            all_statements.append(record)
                    else:
                        logger.warning(f"No {endpoint} data found for {symbol}")
                else:
                    logger.error(f"API request failed: {response.status_code}")
            except Exception as e:
                logger.error(f"Error fetching {endpoint} for {symbol}: {e}")
    
    # Insert all statements into the database
    if all_statements:
        logger.info(f"Inserting {len(all_statements)} statements into database...")
        try:
            success = db_client.update_financial_statements(all_statements)
            if success:
                logger.info(f"✅ Successfully inserted {len(all_statements)} statements")
                return True
            else:
                logger.error("❌ Failed to insert statements")
                return False
        except Exception as e:
            logger.error(f"Error inserting statements: {e}")
            return False
    else:
        logger.warning("No statements to insert")
        return False

if __name__ == "__main__":
    # Get symbols from command line or use defaults
    symbols = sys.argv[1:] if len(sys.argv) > 1 else ["AAPL", "MSFT"]
    
    logger.info(f"Fetching financial statements for: {symbols}")
    success = fetch_financial_statements(symbols)
    
    if success:
        logger.info("✅ DONE! Financial statements fetched and stored.")
        sys.exit(0)
    else:
        logger.error("❌ Failed to fetch or store financial statements.")
        sys.exit(1)
