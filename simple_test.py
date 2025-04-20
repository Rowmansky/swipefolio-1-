"""
Simple FMP Pipeline Test
------------------------
Run this and input your API keys when prompted.
"""
import os
import sys
import logging
import requests
import getpass
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def get_credentials():
    """Get API credentials from user input"""
    print("Please enter your API credentials:")
    fmp_key = getpass.getpass("FMP API Key: ")
    supabase_url = input("Supabase URL: ")
    supabase_key = getpass.getpass("Supabase Service Key: ")
    
    # Set environment variables
    os.environ["FMP_API_KEY"] = fmp_key
    os.environ["SUPABASE_URL"] = supabase_url
    os.environ["SUPABASE_SERVICE_KEY"] = supabase_key
    
    return bool(fmp_key and supabase_url and supabase_key)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("simple_test")

# Test symbol
TEST_SYMBOL = "AAPL"

def test_fmp_api():
    """Test FMP API connection"""
    logger.info(f"Testing FMP API with symbol: {TEST_SYMBOL}")
    
    try:
        # Import after environment variables are set
        from fmp_fetcher.config import FMP_API_KEY, FMP_BASE_URL
        
        url = f"{FMP_BASE_URL}/profile/{TEST_SYMBOL}?apikey={FMP_API_KEY}"
        logger.info(f"Making request to: {url.replace(FMP_API_KEY, 'API_KEY_HIDDEN')}")
        
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"API Response status: {response.status_code}")
            
            if data and isinstance(data, list) and len(data) > 0:
                company = data[0]
                logger.info(f"✅ Successfully fetched company profile:")
                logger.info(f"  - Symbol: {company.get('symbol')}")
                logger.info(f"  - Name: {company.get('companyName')}")
                logger.info(f"  - Industry: {company.get('industry')}")
                return True
            else:
                logger.error(f"Error: Unexpected response format: {data}")
                return False
        else:
            logger.error(f"Error: API request failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing FMP API: {str(e)}")
        return False

def test_supabase_connection():
    """Test Supabase connection"""
    logger.info("Testing Supabase connection")
    
    try:
        # Import after environment variables are set
        from fmp_fetcher.utils.db_client import get_client
        
        client = get_client()
        
        # Try to execute a simple query to verify connection
        # We'll just check if the stocks table exists
        response = client.table('stocks').select('symbol').limit(1).execute()
        
        if response.data is not None:
            logger.info(f"✅ Successfully connected to Supabase")
            logger.info(f"  - Found {len(response.data)} records in stocks table")
            return True
        else:
            logger.error("Error: Couldn't retrieve data from stocks table")
            return False
    except Exception as e:
        logger.error(f"Error testing Supabase connection: {str(e)}")
        return False

def test_profile_fetch():
    """Test fetching and storing company profiles"""
    logger.info(f"Testing profile fetch for {TEST_SYMBOL}")
    
    try:
        # Import after environment variables are set
        from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_profiles
        
        # Fetch and store the profile
        result = fetch_and_store_profiles([TEST_SYMBOL])
        logger.info(f"✅ Successfully ran fetch_and_store_profiles")
        logger.info(f"  - Result: {result}")
        return True
    except Exception as e:
        logger.error(f"Error testing profile fetch: {str(e)}")
        return False

def run_tests():
    """Run all tests"""
    logger.info("=== STARTING SIMPLE TESTS ===")
    
    # Get credentials first
    if not get_credentials():
        logger.error("Failed to get valid credentials. Exiting.")
        return
    
    # Test FMP API connection
    api_success = test_fmp_api()
    
    # Test Supabase connection
    db_success = test_supabase_connection()
    
    # If both API and DB are working, test the actual profile fetch
    if api_success and db_success:
        profile_success = test_profile_fetch()
    else:
        profile_success = False
    
    # Overall results
    if api_success and db_success and profile_success:
        logger.info("✅ All tests passed successfully!")
    else:
        logger.error("❌ Some tests failed:")
        logger.error(f"  - FMP API: {'✅ Passed' if api_success else '❌ Failed'}")
        logger.error(f"  - Supabase: {'✅ Passed' if db_success else '❌ Failed'}")
        logger.error(f"  - Profile Fetch: {'✅ Passed' if profile_success else '❌ Failed'}")

if __name__ == "__main__":
    run_tests()
