"""
Quick Test Script for FMP Pipeline
---------------------------------
Tests a single FMP API endpoint and database connection
"""
import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# You'll need to set these environment variables before running
# export FMP_API_KEY="your_key"
# export SUPABASE_URL="your_url"
# export SUPABASE_SERVICE_KEY="your_key"

# Import after adding project root to path
from fmp_fetcher.utils.logging_config import setup_logging
from fmp_fetcher.config import get_supabase_client, FMP_API_KEY, SUPABASE_URL, SUPABASE_KEY

# Setup logging
setup_logging()
logger = logging.getLogger("focused_test")

def test_db_connection():
    """Test if we can connect to Supabase"""
    logger.info(f"Testing Supabase connection to: {SUPABASE_URL}")
    logger.info(f"FMP API Key exists: {bool(FMP_API_KEY)}")
    
    # Don't log full API key for security, just first/last chars
    if FMP_API_KEY:
        key_preview = f"{FMP_API_KEY[:4]}...{FMP_API_KEY[-4:]}"
        logger.info(f"FMP API Key preview: {key_preview}")
    
    try:
        client = get_supabase_client()
        # Simple query to verify connection works
        result = client.table('companies').select('*').limit(1).execute()
        data = result.data
        logger.info(f"Connected successfully! Found {len(data)} companies")
        
        # Try another table
        result = client.table('daily_prices').select('*').limit(1).execute()
        data = result.data
        logger.info(f"Can query prices table. Found {len(data)} price records")
        
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def test_stock_profile_api():
    """Test if we can fetch from FMP API directly"""
    import requests
    
    symbol = "AAPL"
    logger.info(f"Testing FMP API - fetching profile for {symbol}")
    
    try:
        url = f"https://financialmodelingprep.com/stable/profile/{symbol}?apikey={FMP_API_KEY}"
        logger.info(f"Making request to: {url.replace(FMP_API_KEY, 'API_KEY_HIDDEN')}")
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        logger.info(f"API Response: {data}")
        
        if data and isinstance(data, list) and len(data) > 0:
            logger.info(f"Successfully fetched {symbol} profile from FMP!")
            logger.info(f"Company name: {data[0].get('companyName')}")
            return True
        else:
            logger.error(f"Response format unexpected: {data}")
            return False
    except Exception as e:
        logger.error(f"FMP API request failed: {e}")
        return False

def run_test():
    """Run all tests"""
    logger.info("=== STARTING FOCUSED TEST ===")
    
    # First test DB connection
    if not test_db_connection():
        logger.error("⛔ Database connection test failed! Can't proceed.")
        return
    
    logger.info("✅ Database connection successful!")
    
    # Then test API connection
    if not test_stock_profile_api():
        logger.error("⛔ FMP API connection test failed!")
        return
    
    logger.info("✅ FMP API connection successful!")
    logger.info("Both database and API connections are working!")

if __name__ == "__main__":
    run_test()
