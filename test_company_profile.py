"""
FMP Pipeline - Company Profile Test
----------------------------------
This script tests the company profile fetching task specifically.
"""
import os
import sys
import logging
from datetime import datetime
import argparse

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def parse_arguments():
    """Parse command line arguments for credentials"""
    parser = argparse.ArgumentParser(description='Test Company Profile Task')
    parser.add_argument('--fmp-key', required=True, help='FMP API Key')
    parser.add_argument('--supabase-url', required=True, help='Supabase URL')
    parser.add_argument('--supabase-key', required=True, help='Supabase Service Key')
    parser.add_argument('--symbols', default="AAPL", help='Comma-separated symbols to test')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    return parser.parse_args()

def setup_env(args):
    """Set environment variables from args"""
    os.environ["FMP_API_KEY"] = args.fmp_key
    os.environ["SUPABASE_URL"] = args.supabase_url
    os.environ["SUPABASE_SERVICE_KEY"] = args.supabase_key

def main():
    """Main test function"""
    # Parse arguments and set environment variables
    args = parse_arguments()
    setup_env(args)
    
    # Now we can import our modules that depend on environment variables
    from fmp_fetcher.utils.logging_config import setup_logging
    from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_profiles
    
    # Setup logging
    setup_logging(level=logging.DEBUG if args.verbose else logging.INFO)
    logger = logging.getLogger("profile_test")
    
    # Parse symbols
    symbols = [s.strip() for s in args.symbols.split(',')]
    logger.info(f"Testing company profile fetch for symbols: {symbols}")
    
    try:
        # Start the test
        logger.info("Starting company profile fetch test...")
        
        # Fetch company profiles
        fetch_and_store_profiles(symbols)
        
        logger.info("✅ Test completed successfully")
        return 0
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=args.verbose)
        return 1

if __name__ == "__main__":
    sys.exit(main())
