#!/usr/bin/env python
# debug_financial_statements.py
import logging
import sys
import json
import pprint
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def make_direct_api_call(statement_type="income-statement", symbol="AAPL", year=2023, period="FY"):
    """Make a direct API call to FMP to understand the response format."""
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        logger.error("FMP_API_KEY not found in environment variables.")
        return None
    
    # Try both with and without the -bulk suffix
    endpoints = [
        f"https://financialmodelingprep.com/api/v3/{statement_type}/{symbol}?period={period}&limit=1",
        f"https://financialmodelingprep.com/api/v3/{statement_type}-bulk?year={year}&period={period}"
    ]
    
    for endpoint in endpoints:
        try:
            full_url = f"{endpoint}&apikey={api_key}"
            logger.info(f"Trying endpoint: {endpoint}")
            
            response = requests.get(full_url, timeout=30)
            response.raise_for_status()
            
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"Content-Type: {content_type}")
            
            if 'application/json' in content_type:
                data = response.json()
                logger.info(f"Response is JSON with {len(data) if isinstance(data, list) else 'non-list'} data")
                
                # Print a sample of the data
                if isinstance(data, list) and data:
                    sample = data[0]
                    # Print top-level keys
                    logger.info(f"Top-level keys: {list(sample.keys())}")
                    return data
            elif 'text/csv' in content_type or 'text/plain' in content_type:
                # Handle CSV data
                csv_text = response.text
                logger.info(f"Response appears to be CSV. First 200 chars: {csv_text[:200]}")
                return csv_text
            else:
                logger.warning(f"Unknown content type: {content_type}")
                logger.info(f"First 200 chars of response: {response.text[:200]}")
                
        except Exception as e:
            logger.error(f"Error with endpoint {endpoint}: {e}")
    
    return None

def debug_parsing_function():
    """Look at the parsing function to understand how it maps data to the DB schema."""
    from fmp_fetcher.utils import parsing
    
    # Get the source code of the parsing function
    import inspect
    parse_func = parsing.parse_bulk_financial_statements
    source = inspect.getsource(parse_func)
    
    logger.info("Financial Statement Parsing Function Source:")
    print(source)
    
    # Also look at any helper functions it might call
    if hasattr(parsing, 'parse_financial_statement'):
        helper_func = parsing.parse_financial_statement
        helper_source = inspect.getsource(helper_func)
        logger.info("Helper Function Source:")
        print(helper_source)

def test_csv_handling():
    """Test the CSV handling functionality directly."""
    import csv
    import io
    from fmp_fetcher.utils import parsing
    
    # Sample CSV string (this is a placeholder - replace with actual headers/data from API)
    csv_data = """date,symbol,reportedCurrency,cik,fillingDate,acceptedDate,calendarYear,period,revenue,costOfRevenue,grossProfit
2023-12-31,AAPL,USD,320193,2023-12-31,2023-12-31,2023,FY,394328000000,248891000000,145437000000"""
    
    try:
        # Parse CSV to dictionaries
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        
        if rows:
            logger.info(f"CSV parsed successfully. First row: {rows[0]}")
            
            # Try parsing with the bulk parser
            parsed = parsing.parse_bulk_financial_statements(
                api_data_list=rows,
                statement_type="income",
                target_symbols=["AAPL"]
            )
            
            if parsed:
                logger.info(f"Successfully parsed via parsing function. First item: {parsed[0]}")
            else:
                logger.warning("Parsing function returned empty results")
        else:
            logger.warning("CSV parsing yielded no rows")
    except Exception as e:
        logger.error(f"Error testing CSV handling: {e}")

if __name__ == "__main__":
    logger.info("Starting financial statements debug...")
    
    # Step 1: Make direct API calls to understand response format
    api_data = make_direct_api_call()
    
    # Step 2: Debug the parsing function
    debug_parsing_function()
    
    # Step 3: Test CSV handling
    test_csv_handling()
    
    logger.info("Debug completed")
