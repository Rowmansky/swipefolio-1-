#!/usr/bin/env python
# verify_fmp_api_access.py - Direct verification of FMP API access
import requests
import logging
import sys
import json
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

def test_api_access(symbol="AAPL"):
    """Test direct access to various FMP API endpoints"""
    # Load API key
    load_dotenv()
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        logger.error("FMP_API_KEY not found in environment variables")
        return False
    
    # Test profile endpoint first (this is the most basic endpoint)
    profile_url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}"
    params = {"apikey": api_key}
    
    logger.info(f"Testing profile API access for {symbol}...")
    try:
        response = requests.get(profile_url, params=params)
        status = response.status_code
        logger.info(f"Profile API response status code: {status}")
        
        if status == 200:
            data = response.json()
            if data and len(data) > 0:
                logger.info(f"✅ Successfully fetched profile data for {symbol}")
                logger.info(f"Company name: {data[0].get('companyName', 'N/A')}")
            else:
                logger.warning(f"⚠️ Empty response for profile of {symbol}")
        else:
            logger.error(f"❌ Error response from profile API: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error accessing profile API: {e}")
        return False
    
    # Now test income statement endpoint as recommended in the FMP example
    income_url = f"https://financialmodelingprep.com/api/v3/income-statement/{symbol}"
    params = {"apikey": api_key, "limit": 1}
    
    logger.info(f"Testing income statement API access for {symbol}...")
    try:
        response = requests.get(income_url, params=params)
        status = response.status_code
        logger.info(f"Income statement API response status code: {status}")
        
        if status == 200:
            data = response.json()
            if data and len(data) > 0:
                logger.info(f"✅ Successfully fetched income statement data for {symbol}")
                logger.info(f"Period: {data[0].get('period', 'N/A')}")
                logger.info(f"Fiscal Year: {data[0].get('calendarYear', 'N/A')}")
                
                # Save a sample for inspection
                with open('sample_income_statement.json', 'w') as f:
                    json.dump(data[0], f, indent=2)
                logger.info("Saved sample income statement to sample_income_statement.json")
            else:
                logger.warning(f"⚠️ Empty response for income statement of {symbol}")
        else:
            logger.error(f"❌ Error response from income statement API: {response.text}")
        
    except Exception as e:
        logger.error(f"❌ Error accessing income statement API: {e}")
    
    # Test bulk income statement endpoint (the one used in financial_statement_tasks.py)
    bulk_url = "https://financialmodelingprep.com/api/v3/income-statement-bulk"
    params = {"apikey": api_key, "year": 2023, "period": "FY"}
    
    logger.info(f"Testing bulk income statement API...")
    try:
        response = requests.get(bulk_url, params=params)
        status = response.status_code
        logger.info(f"Bulk income statement API response status code: {status}")
        
        if status == 200:
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"Content-Type: {content_type}")
            
            # Try to parse as JSON first
            try:
                data = response.json()
                if isinstance(data, list):
                    if data:
                        logger.info(f"✅ Successfully fetched bulk income statements. {len(data)} records found.")
                        # Check if our symbol is in the results
                        found = False
                        for item in data:
                            if item.get('symbol') == symbol:
                                found = True
                                logger.info(f"Found {symbol} in bulk data!")
                                break
                        
                        if not found:
                            logger.warning(f"⚠️ {symbol} not found in bulk income statement data")
                    else:
                        logger.warning("⚠️ Empty array returned from bulk income statement API")
                else:
                    logger.warning(f"⚠️ Unexpected response format: {type(data)}")
            except ValueError:
                # If not JSON, check if it's CSV
                content = response.text
                logger.info(f"Response is not JSON. First 200 chars: {content[:200]}")
                
                if ',' in content:
                    logger.info("Response appears to be CSV format")
                    
                    # Check if our symbol is in the CSV
                    if symbol in content:
                        logger.info(f"Found {symbol} in CSV data!")
                    else:
                        logger.warning(f"⚠️ {symbol} not found in CSV data")
        else:
            logger.error(f"❌ Error response from bulk API: {response.text}")
        
    except Exception as e:
        logger.error(f"❌ Error accessing bulk API: {e}")
    
    return True

if __name__ == "__main__":
    logger.info("🔍 Verifying FMP API access...")
    success = test_api_access()
    
    if success:
        logger.info("✅ Basic API access verification completed.")
    else:
        logger.error("❌ API access verification failed!")
