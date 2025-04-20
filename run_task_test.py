"""
FMP Pipeline - Task Runner Test
------------------------------
This script tests individual tasks from the FMP pipeline.
Edit temp_env.py with your credentials before running.
"""
import sys
import os
import logging
import argparse
from datetime import date, timedelta

# Add the project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import our temporary environment settings first
import temp_env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("task_test")

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Test FMP Pipeline Tasks')
    parser.add_argument('task', choices=[
        'profile', 'price', 'metrics', 'statements',
        'news', 'insider', 'analyst', 'estimates',
        'dcf', 'scores', 'peers', 'dividends'
    ], help='The task to test')
    parser.add_argument('--symbols', default=None, 
                      help='Comma-separated symbols to test (default: use symbols from temp_env.py)')
    parser.add_argument('--limit', type=int, default=5,
                      help='Limit for requests that support it (default: 5)')
    return parser.parse_args()

def get_symbols(args):
    """Get symbols to test with"""
    if args.symbols:
        return [s.strip() for s in args.symbols.split(',')]
    return temp_env.TEST_SYMBOLS

def run_profile_test(symbols):
    """Test company profile fetching"""
    logger.info(f"Testing company profile fetch for: {symbols}")
    
    from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_profiles
    result = fetch_and_store_profiles(symbols)
    
    logger.info(f"Profile test completed: {result}")
    return result

def run_price_test(symbols):
    """Test price fetching"""
    logger.info(f"Testing daily price fetch for: {symbols}")
    
    # Fetch yesterday's prices
    yesterday = date.today() - timedelta(days=1)
    date_str = yesterday.isoformat()
    
    from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_daily_prices
    result = fetch_and_store_daily_prices(symbols, date_str)
    
    logger.info(f"Price test completed: {result}")
    return result

def run_metrics_test(symbols):
    """Test metrics fetching"""
    logger.info(f"Testing TTM metrics fetch for: {symbols}")
    
    from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_key_metrics_ttm
    result = fetch_and_store_key_metrics_ttm(symbols)
    
    logger.info(f"TTM metrics test completed: {result}")
    return result

def run_statements_test(symbols, limit=2):
    """Test financial statement fetching"""
    logger.info(f"Testing financial statements fetch for: {symbols}")
    
    from fmp_fetcher.tasks.financial_statement_tasks import fetch_and_store_statements
    result = fetch_and_store_statements(
        symbols, 
        statement_types=["income-statement", "balance-sheet"],
        periods=["annual"],
        limit=limit
    )
    
    logger.info(f"Financial statements test completed: {result}")
    return result

def run_news_test(symbols, limit=5):
    """Test stock news fetching"""
    logger.info(f"Testing stock news fetch for: {symbols}")
    
    from fmp_fetcher.tasks.news_releases_tasks import fetch_and_store_stock_news
    result = fetch_and_store_stock_news(symbols, limit=limit)
    
    logger.info(f"Stock news test completed: {result}")
    return result

def run_insider_test(symbols, limit=5):
    """Test insider trades fetching"""
    logger.info(f"Testing insider trades fetch for: {symbols}")
    
    from fmp_fetcher.tasks.insider_trading_tasks import fetch_and_store_insider_trades
    result = fetch_and_store_insider_trades(symbols, limit=limit)
    
    logger.info(f"Insider trades test completed: {result}")
    return result

def run_analyst_test(symbols):
    """Test analyst ratings fetching"""
    logger.info(f"Testing analyst ratings fetch for: {symbols}")
    
    from fmp_fetcher.tasks.analyst_tasks import fetch_and_store_price_target_consensus
    result = fetch_and_store_price_target_consensus(symbols)
    
    logger.info(f"Analyst ratings test completed: {result}")
    return result

def run_estimates_test(symbols):
    """Test financial estimates fetching"""
    logger.info(f"Testing financial estimates fetch for: {symbols}")
    
    from fmp_fetcher.tasks.estimates_tasks import fetch_and_store_financial_estimates
    result = fetch_and_store_financial_estimates(symbols, quarterly_limit=4, annual_limit=2)
    
    logger.info(f"Financial estimates test completed: {result}")
    return result

def run_dcf_test(symbols):
    """Test DCF valuations fetching"""
    logger.info(f"Testing DCF valuations fetch for: {symbols}")
    
    from fmp_fetcher.tasks.dcf_tasks import fetch_and_store_dcf_valuations
    result = fetch_and_store_dcf_valuations(symbols)
    
    logger.info(f"DCF valuations test completed: {result}")
    return result

def run_scores_test(symbols, limit=5):
    """Test FMP scores fetching"""
    logger.info(f"Testing FMP scores fetch for: {symbols}")
    
    from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_fmp_scores
    result = fetch_and_store_fmp_scores(symbols, limit=limit)
    
    logger.info(f"FMP scores test completed: {result}")
    return result

def run_peers_test(symbols):
    """Test stock peers fetching"""
    logger.info(f"Testing stock peers fetch for: {symbols}")
    
    from fmp_fetcher.tasks.misc_data_tasks import fetch_and_store_peers
    result = fetch_and_store_peers(symbols)
    
    logger.info(f"Stock peers test completed: {result}")
    return result

def run_dividends_test(symbols):
    """Test dividends fetching"""
    logger.info(f"Testing dividends fetch for: {symbols}")
    
    from fmp_fetcher.tasks.dividend_tasks import fetch_and_store_dividends_historical
    result = fetch_and_store_dividends_historical(symbols)
    
    logger.info(f"Dividends test completed: {result}")
    return result

def main():
    """Main function to run the tasks"""
    args = parse_args()
    symbols = get_symbols(args)
    
    logger.info(f"=== Testing {args.task} with symbols: {symbols} ===")
    
    try:
        # Run the appropriate task based on the command line argument
        if args.task == 'profile':
            run_profile_test(symbols)
        elif args.task == 'price':
            run_price_test(symbols)
        elif args.task == 'metrics':
            run_metrics_test(symbols)
        elif args.task == 'statements':
            run_statements_test(symbols, args.limit)
        elif args.task == 'news':
            run_news_test(symbols, args.limit)
        elif args.task == 'insider':
            run_insider_test(symbols, args.limit)
        elif args.task == 'analyst':
            run_analyst_test(symbols)
        elif args.task == 'estimates':
            run_estimates_test(symbols)
        elif args.task == 'dcf':
            run_dcf_test(symbols)
        elif args.task == 'scores':
            run_scores_test(symbols, args.limit)
        elif args.task == 'peers':
            run_peers_test(symbols)
        elif args.task == 'dividends':
            run_dividends_test(symbols)
        
        logger.info("✅ Test execution completed")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
