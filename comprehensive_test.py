"""
Comprehensive FMP Pipeline Testing Script
----------------------------------------
Tests all pipeline tasks with a diverse set of stocks
to validate the entire system end-to-end.
"""
import os
import sys
import logging
import argparse
import time
from datetime import date, timedelta

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import our environment config which contains API keys
import temp_env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('pipeline_test_results.log')
    ]
)
logger = logging.getLogger("comprehensive_test")

# Use ASCII success/failure indicators instead of Unicode emoji
SUCCESS_MARK = "[SUCCESS]"
FAILURE_MARK = "[FAILED]"

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Comprehensive FMP Pipeline Test')
    parser.add_argument('--tasks', default='all', 
                      help='Comma-separated list of tasks to test, or "all" (default)')
    parser.add_argument('--symbols', default=None,
                      help='Comma-separated list of symbols to test (default: use 10 symbols from temp_env.py)')
    parser.add_argument('--limit', type=int, default=3,
                      help='Limit for data fetching (default: 3)')
    return parser.parse_args()

def get_symbols(args):
    """Get test symbols from arguments or temp_env"""
    if args.symbols:
        return [s.strip() for s in args.symbols.split(',')]
    return temp_env.TEST_SYMBOLS

def test_task(task_name, test_function, symbols, limit=3):
    """Test a specific task and log results"""
    logger.info(f"{'-' * 30} TESTING: {task_name} {'-' * 30}")
    try:
        start_time = time.time()
        result = test_function(symbols, limit)
        duration = time.time() - start_time
        
        status = SUCCESS_MARK if result else FAILURE_MARK
        logger.info(f"Task {task_name}: {status} [Duration: {duration:.2f}s]")
        return result
    except Exception as e:
        logger.error(f"Task {task_name} raised exception: {e}", exc_info=True)
        return False

def run_profile_test(symbols, limit=None):
    """Test company profile fetching"""
    from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_profiles
    logger.info(f"Testing profiles for {len(symbols)} symbols")
    return fetch_and_store_profiles(symbols)

def run_prices_test(symbols, limit=None):
    """Test historical prices fetching"""
    from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_daily_prices
    yesterday = date.today() - timedelta(days=1)
    date_str = yesterday.isoformat()
    logger.info(f"Testing daily prices for {len(symbols)} symbols with date {date_str}")
    return fetch_and_store_daily_prices(symbols, date_str)

def run_metrics_ttm_test(symbols, limit=None):
    """Test TTM metrics fetching"""
    from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_key_metrics_ttm
    logger.info(f"Testing TTM metrics for {len(symbols)} symbols")
    return fetch_and_store_key_metrics_ttm(symbols)

def run_metrics_historical_test(symbols, limit=None):
    """Test historical metrics fetching"""
    from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_key_metrics_historical
    logger.info(f"Testing historical metrics for {len(symbols[:3])} symbols with limit {limit}")
    # Use only first few symbols for heavy historical queries
    return fetch_and_store_key_metrics_historical(symbols[:3], "quarter", limit)

def run_ratios_historical_test(symbols, limit=None):
    """Test historical financial ratios fetching"""
    from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_financial_ratios_historical
    logger.info(f"Testing historical ratios for {len(symbols[:3])} symbols with limit {limit}")
    # Use only first few symbols for heavy historical queries
    return fetch_and_store_financial_ratios_historical(symbols[:3], "quarter", limit)

def run_statements_test(symbols, limit=None):
    """Test financial statement fetching"""
    from fmp_fetcher.tasks.financial_statement_tasks import fetch_and_store_statements
    logger.info(f"Testing financial statements for {len(symbols[:3])} symbols")
    # Use only a subset of symbols and statement types for this heavy-duty task
    return fetch_and_store_statements(
        symbols[:3],
        statement_types=["income-statement", "balance-sheet"],
        periods=["quarter"],
        limit=limit
    )

def run_statement_growth_test(symbols, limit=None):
    """Test financial statement growth fetching"""
    from fmp_fetcher.tasks.financial_statement_growth_tasks import fetch_and_store_statement_growth
    logger.info(f"Testing statement growth for {len(symbols[:3])} symbols")
    # Use only a subset of symbols for this task
    return fetch_and_store_statement_growth(
        symbols[:3], 
        statement_types=["income-statement-growth"], 
        periods=["quarter"], 
        limit=limit
    )

def run_enterprise_values_test(symbols, limit=None):
    """Test enterprise values fetching"""
    from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_enterprise_values_historical
    logger.info(f"Testing enterprise values for {len(symbols[:3])} symbols with limit {limit}")
    # Use only first few symbols for enterprise values
    return fetch_and_store_enterprise_values_historical(symbols[:3], "quarter", limit)

def run_dividends_test(symbols, limit=None):
    """Test dividends fetching"""
    from fmp_fetcher.tasks.dividend_tasks import fetch_and_store_dividends_historical
    logger.info(f"Testing dividends for {len(symbols)} symbols")
    return fetch_and_store_dividends_historical(symbols)

def run_earnings_test(symbols, limit=None):
    """Test earnings reports fetching"""
    from fmp_fetcher.tasks.earnings_tasks import fetch_and_store_earnings_reports
    logger.info(f"Testing earnings reports for {len(symbols)} symbols with limit {limit}")
    return fetch_and_store_earnings_reports(symbols, limit)

def run_estimates_test(symbols, limit=None):
    """Test financial estimates fetching"""
    from fmp_fetcher.tasks.estimates_tasks import fetch_and_store_financial_estimates
    logger.info(f"Testing financial estimates for {len(symbols)} symbols")
    return fetch_and_store_financial_estimates(symbols, quarterly_limit=limit, annual_limit=limit)

def run_scores_test(symbols, limit=None):
    """Test FMP scores fetching"""
    from fmp_fetcher.tasks.metrics_tasks import fetch_and_store_fmp_scores
    logger.info(f"Testing FMP scores for {len(symbols)} symbols with limit {limit}")
    return fetch_and_store_fmp_scores(symbols, limit)

def run_news_test(symbols, limit=None):
    """Test stock news fetching"""
    from fmp_fetcher.tasks.news_releases_tasks import fetch_and_store_stock_news
    logger.info(f"Testing stock news for {len(symbols)} symbols with limit {limit}")
    return fetch_and_store_stock_news(symbols, limit)

def run_press_releases_test(symbols, limit=None):
    """Test press releases fetching"""
    from fmp_fetcher.tasks.news_releases_tasks import fetch_and_store_press_releases
    logger.info(f"Testing press releases with limit {limit}")
    return fetch_and_store_press_releases(limit)

def run_insider_trades_test(symbols, limit=None):
    """Test insider trades fetching"""
    from fmp_fetcher.tasks.insider_trading_tasks import fetch_and_store_insider_trades
    logger.info(f"Testing insider trades for {len(symbols)} symbols with limit {limit}")
    return fetch_and_store_insider_trades(symbols, limit)

def run_insider_stats_test(symbols, limit=None):
    """Test insider trading stats fetching"""
    from fmp_fetcher.tasks.insider_trading_tasks import fetch_and_store_insider_trading_stats
    logger.info(f"Testing insider trading stats for {len(symbols)} symbols")
    return fetch_and_store_insider_trading_stats(symbols)

def run_political_disclosures_test(symbols, limit=None):
    """Test political disclosures fetching"""
    from fmp_fetcher.tasks.political_disclosure_tasks import fetch_and_store_political_disclosures
    logger.info(f"Testing political disclosures with limit {limit}")
    return fetch_and_store_political_disclosures(symbols, limit)

def run_peers_test(symbols, limit=None):
    """Test stock peers fetching"""
    from fmp_fetcher.tasks.misc_data_tasks import fetch_and_store_peers
    logger.info(f"Testing stock peers for {len(symbols[:5])} symbols")
    # Use subset to avoid too many peer relationships
    return fetch_and_store_peers(symbols[:5])

def run_dcf_test(symbols, limit=None):
    """Test DCF valuations fetching"""
    from fmp_fetcher.tasks.dcf_tasks import fetch_and_store_dcf_valuations
    logger.info(f"Testing DCF valuations for {len(symbols)} symbols")
    return fetch_and_store_dcf_valuations(symbols)

def run_inst_ownership_test(symbols, limit=None):
    """Test institutional ownership fetching"""
    from fmp_fetcher.tasks.ownership_tasks import fetch_and_store_inst_own_summary
    logger.info(f"Testing institutional ownership for {len(symbols[:5])} symbols")
    # Use subset to avoid too many institutional holdings
    return fetch_and_store_inst_own_summary(symbols[:5])

def run_inst_holdings_test(symbols, limit=None):
    """Test institutional holdings fetching"""
    from fmp_fetcher.tasks.ownership_tasks import fetch_and_store_inst_holdings
    logger.info(f"Testing institutional holdings for {len(symbols[:3])} symbols with limit {limit}")
    # Use subset to avoid too many institutional holdings
    return fetch_and_store_inst_holdings(symbols[:3], limit)

def run_analyst_ratings_test(symbols, limit=None):
    """Test analyst ratings fetching"""
    from fmp_fetcher.tasks.analyst_tasks import fetch_and_store_price_target_consensus
    logger.info(f"Testing analyst ratings for {len(symbols)} symbols")
    return fetch_and_store_price_target_consensus(symbols)

def run_esg_test(symbols, limit=None):
    """Test ESG scores fetching"""
    from fmp_fetcher.tasks.esg_tasks import fetch_and_store_esg_scores
    logger.info(f"Testing ESG scores for {len(symbols)} symbols")
    return fetch_and_store_esg_scores(symbols)

def run_calculated_metrics_test(symbols, limit=None):
    """Test calculated metrics"""
    from fmp_fetcher.tasks.calculator_tasks import calculate_and_store_derived_metrics
    logger.info(f"Testing calculated metrics for {len(symbols)} symbols")
    return calculate_and_store_derived_metrics(symbols)

def main():
    """Main test runner function"""
    args = parse_args()
    symbols = get_symbols(args)
    
    logger.info(f"Starting comprehensive testing with {len(symbols)} symbols")
    logger.info(f"Selected symbols: {symbols}")
    
    # Define all available tasks with their test functions
    all_tasks = {
        # Core data
        "profiles": run_profile_test,
        "prices": run_prices_test,
        
        # Metrics & financial data
        "metrics_ttm": run_metrics_ttm_test,
        "metrics_historical": run_metrics_historical_test,
        "ratios": run_ratios_historical_test,
        "statements": run_statements_test,
        "statement_growth": run_statement_growth_test,
        "enterprise_values": run_enterprise_values_test,
        "scores": run_scores_test,
        
        # Dividends & earnings
        "dividends": run_dividends_test,
        "earnings": run_earnings_test,
        "estimates": run_estimates_test,
        
        # News & events
        "news": run_news_test,
        "press_releases": run_press_releases_test,
        
        # Ownership & trading
        "insider_trades": run_insider_trades_test,
        "insider_stats": run_insider_stats_test,
        "political": run_political_disclosures_test,
        "inst_ownership": run_inst_ownership_test,
        "inst_holdings": run_inst_holdings_test,
        
        # Analysis & ratings
        "peers": run_peers_test,
        "dcf": run_dcf_test,
        "analyst": run_analyst_ratings_test,
        "esg": run_esg_test,
        
        # Calculated data
        "calculated": run_calculated_metrics_test,
    }
    
    # Determine which tasks to run
    tasks_to_run = []
    if args.tasks.lower() == 'all':
        tasks_to_run = list(all_tasks.items())
    else:
        selected_tasks = [t.strip() for t in args.tasks.split(',')]
        tasks_to_run = [(t, all_tasks[t]) for t in selected_tasks if t in all_tasks]
    
    if not tasks_to_run:
        logger.error(f"No valid tasks selected. Available tasks: {', '.join(all_tasks.keys())}")
        return 1
    
    logger.info(f"Will test {len(tasks_to_run)} tasks: {[t[0] for t in tasks_to_run]}")
    
    # Track results
    results = {}
    
    # Run each task
    for task_name, test_func in tasks_to_run:
        success = test_task(task_name, test_func, symbols, args.limit)
        results[task_name] = SUCCESS_MARK if success else FAILURE_MARK
        # Add small delay between tasks to avoid rate limiting
        time.sleep(1)
    
    # Print summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 50)
    
    for task_name, result in results.items():
        logger.info(f"{task_name.ljust(20)}: {result}")
    
    success_count = sum(1 for result in results.values() if SUCCESS_MARK in result)
    logger.info(f"\nTasks completed: {len(results)}")
    logger.info(f"Tasks successful: {success_count}")
    logger.info(f"Tasks failed: {len(results) - success_count}")
    
    return 0 if success_count == len(results) else 1

if __name__ == "__main__":
    sys.exit(main())
