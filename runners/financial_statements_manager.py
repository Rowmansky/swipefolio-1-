#!/usr/bin/env python
# financial_statements_manager.py - Comprehensive financial statement fetching and storage
import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from fmp_fetcher.clients import db_client
from fmp_fetcher.clients.fmp_client import make_fmp_request
from fmp_fetcher.config import TARGET_SYMBOLS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Constants for statement types and database schema
STATEMENT_TYPES = [
    {"endpoint": "income-statement", "db_enum": "income", "description": "Income Statement"},
    {"endpoint": "balance-sheet-statement", "db_enum": "balance", "description": "Balance Sheet"},
    {"endpoint": "cash-flow-statement", "db_enum": "cashflow", "description": "Cash Flow"}
]

# Period mapping from API to database enum
PERIOD_MAP = {
    "FY": "annual",
    "Q1": "quarter", 
    "Q2": "quarter", 
    "Q3": "quarter",
    "Q4": "quarter"
}

def ensure_stock_profiles(symbols):
    """
    Ensure stock profiles exist in database (required for foreign key constraints)
    
    Args:
        symbols: List of stock symbols to check/create
        
    Returns:
        True if profiles exist or were created, False on failure
    """
    logger.info(f"Ensuring stock profiles exist for {len(symbols)} symbols...")
    
    # Create minimal stock profiles for testing
    profiles = []
    for symbol in symbols:
        profiles.append({
            'symbol': symbol,
            'company_name': f'Company {symbol}',
            'exchange': 'NASDAQ',
            'industry': 'Technology',
            'sector': 'Technology',
            'country': 'USA',
            'is_actively_trading': True
        })
    
    # Update database with profiles
    success = db_client.update_stocks(profiles)
    if success:
        logger.info(f"✅ Stock profiles ready for {len(symbols)} symbols")
        return True
    else:
        logger.error(f"❌ Failed to create/update stock profiles")
        return False

def fetch_financial_statements(symbols, period="FY", limit=5, save_samples=True):
    """
    Fetch and store financial statements for specified symbols
    
    Args:
        symbols: List of stock symbols to fetch
        period: Statement period (FY, Q1, Q2, Q3, Q4)
        limit: Max number of statements to fetch per symbol
        save_samples: Whether to save sample JSON files
        
    Returns:
        True if operation was successful, False on error
    """
    # Load API key from environment
    load_dotenv()
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        logger.error("FMP_API_KEY not found in environment")
        return False
    
    # First ensure stock profiles exist (required for foreign key constraints)
    if not ensure_stock_profiles(symbols):
        return False
    
    # Collection for all statements
    all_statements = []
    statements_by_type = {}
    verbose_output = []  # For collecting detailed info
    
    # Process each symbol
    for symbol in symbols:
        logger.info(f"Processing statements for {symbol}...")
        
        # Fetch each statement type
        for stmt_config in STATEMENT_TYPES:
            endpoint = stmt_config["endpoint"]
            db_type = stmt_config["db_enum"]
            description = stmt_config["description"]
            
            # Initialize counter for this statement type
            if db_type not in statements_by_type:
                statements_by_type[db_type] = 0
            
            # Prepare API call
            params = {"symbol": symbol, "limit": limit}
            # Include period filter
            if period:
                params["period"] = period
            
            logger.info(f"Fetching {description} for {symbol}...")
            
            # Add API key and fetch via client
            data = make_fmp_request(f"/{endpoint}", params=params)
            if not data:
                logger.warning(f"No {description} data returned for {symbol}")
                continue
            
            if isinstance(data, list) and data:
                stmt_count = len(data)
                logger.info(f"✅ Got {stmt_count} {description} records for {symbol}")
                statements_by_type[db_type] += stmt_count
                
                # Save sample if requested
                if save_samples:
                    sample_file = f"sample_{symbol}_{endpoint.replace('-', '_')}.json"
                    with open(sample_file, "w") as f:
                        json.dump(data[0], f, indent=2)
                    logger.info(f"Sample saved to {sample_file}")
                
                # Process each statement
                for item in data:
                    report_date = item.get('date') or item.get('reportDate')
                    filing_date = item.get('filingDate') or item.get('filing_date')
                    accepted_date = item.get('acceptedDate') or item.get('accepted_date')
                    api_period = item.get('period', period)
                    record = {
                        'symbol': symbol,
                        'report_date': report_date,
                        'filing_date': filing_date,
                        'accepted_date': accepted_date,
                        'calendar_year': int(item.get('fiscalYear', 0)),
                        'period': PERIOD_MAP.get(api_period, 'annual'),
                        'statement_type': db_type,
                        'cik': item.get('cik'),
                        'data': item
                    }
                    all_statements.append(record)
    
    # After processing all symbols, insert statements into database
    if all_statements:
        logger.info("Statement details BEFORE insertion:")
        for stmt_type, count in statements_by_type.items():
            if count > 0:
                logger.info(f"  - {count} {stmt_type} statements")
        try:
            success = db_client.update_financial_statements(all_statements)
            if success:
                logger.info(f"✅ Successfully stored {len(all_statements)} financial statements")
                return True
            else:
                logger.error("❌ Failed to insert statements into database")
                return False
        except Exception as e:
            logger.error(f"Error inserting statements: {e}")
            return False
    else:
        logger.warning("No financial statements found to insert")
        return False

def main():
    """Main entry point with command line argument handling"""
    # Check for symbols passed as arguments
    if len(sys.argv) > 1:
        symbols = sys.argv[1:]
    else:
        # Default symbols including Google and Prologis as requested
        symbols = ["AAPL", "MSFT", "GOOG", "PLD"]
    
    # Make logging more verbose
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the fetching process
    logger.info(f"Starting financial statement fetch for {len(symbols)} symbols: {symbols}")
    success = fetch_financial_statements(symbols, period="FY", limit=2)
    
    # EXTRA VERIFICATION: Confirm what was stored in the database
    try:
        logger.info("🔍 VERIFYING WHAT WAS STORED IN DATABASE...")
        
        # Connect to Supabase directly to check
        from fmp_fetcher.config import get_supabase_client
        supabase = get_supabase_client()
        
        # Query for each statement type to verify storage
        for stmt_type in ["income", "balance", "cashflow"]:
            for symbol in symbols:
                result = supabase.table("financial_statements").select("id, symbol, statement_type, report_date").eq("symbol", symbol).eq("statement_type", stmt_type).execute()
                
                if hasattr(result, 'data') and result.data:
                    logger.info(f"✅ VERIFIED: Found {len(result.data)} {stmt_type} statements for {symbol} in database")
                    # Show the first record for confirmation
                    if result.data:
                        logger.info(f"  Sample record: {result.data[0]}")
                else:
                    logger.error(f"❌ VERIFICATION FAILED: No {stmt_type} statements found for {symbol} in database")
    except Exception as e:
        logger.error(f"❌ Database verification error: {e}")
    
    if success:
        logger.info("✅ Financial statement update completed successfully")
        return 0
    else:
        logger.error("❌ Financial statement update failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
