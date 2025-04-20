import schedule
import time
import logging
import argparse
import sys
import os
from datetime import date, timedelta, datetime

# Ensure the parent directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fmp_fetcher.utils.logging_config import setup_logging
from fmp_fetcher.config import TARGET_SYMBOLS
from fmp_fetcher.tasks.stock_data_tasks import (
    fetch_and_store_profiles,
    fetch_and_store_daily_prices
)
from fmp_fetcher.tasks.financial_statement_tasks import fetch_and_store_statements
from fmp_fetcher.tasks.metrics_tasks import (
    fetch_and_store_key_metrics_ttm,
    fetch_and_store_key_metrics_historical,
    fetch_and_store_financial_ratios_historical,
    fetch_and_store_enterprise_values_historical,
    fetch_and_store_fmp_scores
)
from fmp_fetcher.tasks.financial_statement_growth_tasks import fetch_and_store_statement_growth
from fmp_fetcher.tasks.owner_earnings_tasks import fetch_and_store_owner_earnings_historical
from fmp_fetcher.tasks.dividend_tasks import fetch_and_store_dividends_historical
from fmp_fetcher.tasks.earnings_tasks import fetch_and_store_earnings_reports
from fmp_fetcher.tasks.esg_tasks import fetch_and_store_esg_scores
from fmp_fetcher.tasks.insider_trading_tasks import (
    fetch_and_store_insider_trades,
    fetch_and_store_insider_trading_stats
)
from fmp_fetcher.tasks.political_disclosure_tasks import fetch_and_store_political_disclosures
from fmp_fetcher.tasks.estimates_tasks import fetch_and_store_financial_estimates
from fmp_fetcher.tasks.news_releases_tasks import (
    fetch_and_store_press_releases,
    fetch_and_store_stock_news
)
from fmp_fetcher.tasks.misc_data_tasks import fetch_and_store_peers
from fmp_fetcher.tasks.ownership_tasks import (
    fetch_and_store_inst_own_summary,
    fetch_and_store_inst_holdings
)
from fmp_fetcher.tasks.dcf_tasks import fetch_and_store_dcf_valuations
from fmp_fetcher.tasks.calculator_tasks import calculate_and_store_derived_metrics
from fmp_fetcher.tasks.analyst_tasks import (
    fetch_and_store_price_target_news,
    fetch_and_store_grade_news,
    fetch_and_store_current_grades,
    fetch_and_store_ratings_snapshot,
    fetch_and_store_price_target_consensus,
    fetch_and_store_historical_grades
)

# Setup logging AS EARLY AS POSSIBLE
setup_logging()
logger = logging.getLogger(__name__)

# --- Hourly Jobs --- 

def run_hourly_jobs():
    logger.info("--- Running Hourly Jobs --- ")
    
    # Fetch latest stock news
    logger.info("--- Running Hourly Stock News Fetch ---")
    fetch_and_store_stock_news(TARGET_SYMBOLS, limit=50, chunk_size=20)
    
    logger.info("--- Hourly Jobs Complete --- ")

# --- Daily Jobs ---

def run_daily_jobs():
    logger.info("--- Running Daily Jobs --- ")
    
    # Determine date for EOD prices (usually previous business day)
    # Simple approach: fetch yesterday's data. Robust approach would check market holidays.
    yesterday = date.today() - timedelta(days=1)
    fetch_date_str = yesterday.isoformat()
    logger.info(f"Target date for daily data fetch: {fetch_date_str}")

    try:
        fetch_and_store_daily_prices(TARGET_SYMBOLS, fetch_date_str)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_daily_prices: {e}")

    # Fetch full historical dividends (daily check seems reasonable)
    logger.info("--- Running Daily Historical Dividend Fetch ---")
    fetch_and_store_dividends_historical(TARGET_SYMBOLS)

    # Fetch recent insider trades (daily check)
    logger.info("--- Running Daily Insider Trades Fetch ---")
    fetch_and_store_insider_trades(TARGET_SYMBOLS) # Fetches default limit (e.g., 100)

    # Fetch recent political disclosures (daily check)
    logger.info("--- Running Daily Political Disclosures Fetch ---")
    fetch_and_store_political_disclosures(TARGET_SYMBOLS) # Fetches default limit (e.g., 100)
    
    # Fetch latest press releases
    logger.info("--- Running Daily Press Releases Fetch ---")
    fetch_and_store_press_releases(limit=200)

    # Fetch analyst price target news
    logger.info("--- Running Daily Price Target News Fetch ---")
    fetch_and_store_price_target_news(TARGET_SYMBOLS, limit=100)
    
    # Fetch analyst grade news
    logger.info("--- Running Daily Grade News Fetch ---")
    fetch_and_store_grade_news(TARGET_SYMBOLS, limit=15)
    
    # Fetch current analyst grades
    logger.info("--- Running Daily Current Grades Fetch ---")
    fetch_and_store_current_grades(TARGET_SYMBOLS, limit=5)

    # Fetch TTM Metrics
    try:
        logger.info("--- Running Daily TTM Metrics Fetch ---")
        fetch_and_store_key_metrics_ttm(TARGET_SYMBOLS)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_key_metrics_ttm: {e}")

    logger.info("--- Daily Jobs Complete --- ")

# --- Weekly Jobs ---

def run_weekly_jobs():
    logger.info("--- Running Weekly Jobs --- ")

    try:
        logger.info("--- Running Weekly Company Profiles Fetch ---")
        fetch_and_store_profiles(TARGET_SYMBOLS)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_profiles: {e}")
    
    # Fetch financial estimates (quarterly and annual)
    logger.info("--- Running Weekly Financial Estimates Fetch ---")
    fetch_and_store_financial_estimates(TARGET_SYMBOLS, quarterly_limit=8, annual_limit=5)
    
    # Fetch FMP financial scores (historical)
    logger.info("--- Running Weekly FMP Financial Scores Fetch ---")
    fetch_and_store_fmp_scores(TARGET_SYMBOLS, limit=40)
    
    # Fetch ratings snapshots
    logger.info("--- Running Weekly Ratings Snapshot Fetch ---")
    fetch_and_store_ratings_snapshot(TARGET_SYMBOLS)
    
    # Fetch price target consensus
    logger.info("--- Running Weekly Price Target Consensus Fetch ---")
    fetch_and_store_price_target_consensus(TARGET_SYMBOLS)

    logger.info("--- Weekly Jobs Complete --- ")

# --- Monthly Jobs ---

def run_monthly_jobs():
    logger.info("--- Running Monthly Jobs --- ")
    
    # Fetch stock peers
    logger.info("--- Running Monthly Stock Peers Fetch ---")
    fetch_and_store_peers(TARGET_SYMBOLS)
    
    # Fetch DCF valuations (both standard and levered)
    logger.info("--- Running Monthly DCF Valuations Fetch ---")
    fetch_and_store_dcf_valuations(TARGET_SYMBOLS)
    
    # Fetch insider trading statistics
    logger.info("--- Running Monthly Insider Trading Statistics Fetch ---")
    fetch_and_store_insider_trading_stats(TARGET_SYMBOLS)
    
    # Fetch historical grades
    logger.info("--- Running Monthly Historical Grades Fetch ---")
    fetch_and_store_historical_grades(TARGET_SYMBOLS, limit=100)

    logger.info("--- Monthly Jobs Complete --- ")

# --- Quarterly Jobs ---

def run_quarterly_jobs(year: int, period: str):
    logger.info(f"--- Running Quarterly Jobs for {year} {period} --- ")
    # Note: The fetch_and_store_statements task uses 'limit' rather than specific year/period.
    # We'll fetch recent quarterly and annual data when this job runs.
    # Adapt this if specific year/period fetching is strictly required and supported differently.

    try:
        logger.info("--- Running Quarterly Financial Statements Fetch ---")
        fetch_and_store_statements(TARGET_SYMBOLS, quarter_limit=8, annual_limit=5)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_statements: {e}")

    # Historical Key Metrics
    try:
        logger.info("--- Running Quarterly Historical Key Metrics Fetch ---")
        fetch_and_store_key_metrics_historical(TARGET_SYMBOLS, period='quarter', limit=20)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_key_metrics_historical: {e}")

    # Historical Financial Ratios 
    try:
        logger.info("--- Running Quarterly Historical Financial Ratios Fetch ---")
        fetch_and_store_financial_ratios_historical(TARGET_SYMBOLS, period='quarter', limit=20)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_financial_ratios_historical: {e}")

    # Historical Enterprise Values
    try:
        logger.info("--- Running Quarterly Historical Enterprise Values Fetch ---")
        fetch_and_store_enterprise_values_historical(TARGET_SYMBOLS, period='quarter', limit=20)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_enterprise_values_historical: {e}")

    # Financial Statement Growth data
    try:
        logger.info("--- Running Quarterly Financial Statement Growth Fetch ---")
        fetch_and_store_statement_growth(TARGET_SYMBOLS, period='quarter', limit=20)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_statement_growth: {e}")

    # Earnings Reports
    try:
        logger.info("--- Running Quarterly Earnings Reports Fetch ---")
        fetch_and_store_earnings_reports(TARGET_SYMBOLS)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_earnings_reports: {e}")

    # ESG Scores
    try:
        logger.info("--- Running Quarterly ESG Scores Fetch ---")
        fetch_and_store_esg_scores(TARGET_SYMBOLS)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_esg_scores: {e}")
    
    # Institutional Ownership Summary
    try:
        logger.info("--- Running Quarterly Institutional Ownership Summary Fetch ---")
        fetch_and_store_inst_own_summary(TARGET_SYMBOLS, num_quarters=4)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_inst_own_summary: {e}")
    
    # Institutional Holdings Detail
    try:
        logger.info("--- Running Quarterly Institutional Holdings Detail Fetch ---")
        fetch_and_store_inst_holdings(TARGET_SYMBOLS, num_quarters=4, top_holders_limit=100)
    except Exception as e:
        logger.exception(f"Error running fetch_and_store_inst_holdings: {e}")

    # Calculate derived metrics
    try:
        logger.info("--- Running Quarterly Calculated Metrics ---")
        calculate_and_store_derived_metrics(TARGET_SYMBOLS)
    except Exception as e:
        logger.exception(f"Error running calculate_and_store_derived_metrics: {e}")

    logger.info(f"--- Quarterly Jobs for {year} {period} Complete --- ")

# --- Annual Jobs ---

def run_annual_jobs(year: int):
    logger.info(f"--- Running Annual Jobs for {year} --- ")

    logger.info(f"--- Running Annual Owner Earnings Historical Fetch ---")
    fetch_and_store_owner_earnings_historical(TARGET_SYMBOLS, limit=15)  # Fetch 15 years of data

    logger.info(f"--- Annual Jobs for {year} Complete --- ")

def main():
    parser = argparse.ArgumentParser(description="FMP Data Fetcher Service")
    parser.add_argument(
        '--run-quarterly',
        action='store_true',
        help='Run the quarterly data fetching and calculation tasks immediately.'
    )
    parser.add_argument(
        '--year', 
        type=int, 
        help='Specify the year for quarterly tasks (required if --run-quarterly is set).'
    )
    parser.add_argument(
        '--period', 
        type=str, 
        choices=['Q1', 'Q2', 'Q3', 'Q4', 'FY'], 
        help='Specify the period (Q1-Q4, FY) for quarterly tasks (required if --run-quarterly is set).'
    )
    parser.add_argument(
        '--run-task', 
        type=str, 
        help='Run a specific task immediately (e.g., "hourly", "daily", "weekly", "monthly", "annual"). For testing.'
    )

    args = parser.parse_args()

    if args.run_quarterly:
        if not args.year or not args.period:
            parser.error("--year and --period are required when using --run-quarterly")
        logger.info(f"Manual trigger: Running quarterly tasks for {args.year} {args.period}")
        run_quarterly_jobs(args.year, args.period)
        logger.info("Manual quarterly run finished. Exiting scheduler mode.")
        return
    
    if args.run_task:
        task_name = args.run_task.lower()
        logger.info(f"Manual trigger: Running task '{task_name}'")
        if task_name == 'hourly':
            run_hourly_jobs()
        elif task_name == 'daily':
            run_daily_jobs()
        elif task_name == 'weekly':
            run_weekly_jobs()
        elif task_name == 'monthly':
            run_monthly_jobs()
        elif task_name == 'annual':
            run_annual_jobs(2022) # default year
        else:
            logger.error(f"Unknown task name for --run-task: {task_name}. Choose 'hourly', 'daily', 'weekly', 'monthly', or 'annual'.")
        logger.info(f"Manual task '{task_name}' finished. Exiting scheduler mode.")
        return

    # --- Setup Schedules (if not running manually) ---
    logger.info("Setting up schedules...")

    # High Frequency (Example: News every hour at :05) - Adjust as needed
    # schedule.every().hour.at(":05").do(run_hourly_jobs)
    logger.info("TODO: Schedule hourly jobs (news, press releases?).")

    # Medium Frequency (Example: Daily after market close - 6 PM ET = 22:00 UTC approx)
    # Ensure the server running this script uses UTC or handle timezones appropriately.
    schedule.every().day.at("22:00").do(run_daily_jobs) 
    logger.info("Daily jobs scheduled for 22:00 UTC.")

    # Low Frequency (Example: Weekly on Sunday at 3 AM UTC)
    schedule.every().sunday.at("03:00").do(run_weekly_jobs)
    logger.info("Weekly jobs scheduled for Sunday 03:00 UTC.")

    # Monthly Jobs
    schedule.every().day.at("02:00").do(run_monthly_jobs) # Run monthly jobs on the 1st of each month
    logger.info("Monthly jobs scheduled for the 1st of each month at 02:00 UTC.")

    # Very Low Frequency (Example: Annually on January 1st at 3 AM UTC)
    schedule.every().year.at("01:01:03").do(run_annual_jobs, 2022) # default year
    logger.info("Annual jobs scheduled for January 1st 03:00 UTC.")

    logger.info("Scheduler setup complete. Starting main loop.")
    
    # Run once immediately? Optional
    # logger.info("Running initial daily jobs...")
    # run_daily_jobs()
    # logger.info("Initial daily jobs complete.")

    # --- Run Scheduler Loop ---
    while True:
        try:
            schedule.run_pending()
            time.sleep(60) # Check every 60 seconds
        except KeyboardInterrupt:
            logger.info("Scheduler stopped manually.")
            break
        except Exception as e:
            logger.exception(f"An error occurred in the scheduler loop: {e}")
            time.sleep(300) # Wait 5 minutes before trying again

if __name__ == "__main__":
    main()
