import os
import json
import logging
import requests
from dotenv import load_dotenv
from fmp_fetcher.utils.parsing import parse_key_metrics_ttm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("FMP_API_KEY")

if not api_key:
    raise ValueError("FMP_API_KEY environment variable is not set")

# FMP API base URL
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# Test symbols (diverse set across different sectors)
test_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "JPM", "JNJ", "PG", "XOM", "DIS", "CAT"]

# Previously problematic metrics to verify
problem_metrics = [
    "pe_ratio_ttm", "pocfratio_ttm", "pfcf_ratio_ttm", "pb_ratio_ttm", "ptb_ratio_ttm",
    "enterprise_value_over_ebitdat_tm", "roe_ttm", "roic_ttm", "debt_to_equity_ttm",
    "debt_to_assets_ttm", "interest_coverage_ttm", "long_term_debt_to_capitalization_ttm",
    "total_debt_to_capitalization_ttm", "debt_ratio_ttm", "cash_flow_to_debt_ratio_ttm",
    "company_equity_multiplier_ttm", "cash_flow_coverage_ratios_ttm", "short_term_coverage_ratios_ttm",
    "payout_ratio_ttm", "days_sales_outstanding_ttm", "days_payables_outstanding_ttm",
    "days_of_inventory_on_hand_ttm"
]

def get_key_metrics_ttm(symbol):
    """Direct fetch of key metrics TTM data from FMP API."""
    url = f"{FMP_BASE_URL}/key-metrics-ttm/{symbol}"
    params = {"apikey": api_key}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            return data[0]  # FMP returns a list even for single items
        return None
    except Exception as e:
        logger.error(f"Error fetching TTM data for {symbol}: {str(e)}")
        return None

def test_key_metrics_ttm():
    """Test fetching and parsing of key metrics TTM data for multiple symbols."""
    results = {}
    null_metrics_by_symbol = {}
    
    for symbol in test_symbols:
        logger.info(f"Testing key metrics TTM for {symbol}")
        
        # Fetch TTM data directly from FMP
        ttm_data = get_key_metrics_ttm(symbol)
        if not ttm_data:
            logger.error(f"No TTM data received for {symbol}")
            results[symbol] = "ERROR: No data received"
            continue
            
        # Log raw data for debugging
        logger.info(f"Raw data for {symbol}: {json.dumps(ttm_data)[:500]}...")
            
        # Parse the TTM data
        parsed_data = parse_key_metrics_ttm(ttm_data, symbol)
        if not parsed_data:
            logger.error(f"Failed to parse TTM data for {symbol}")
            results[symbol] = "ERROR: Parsing failed"
            continue
            
        # Check for NULL values in problem metrics
        null_metrics = []
        for metric in problem_metrics:
            if parsed_data.get(metric) is None:
                null_metrics.append(metric)
        
        # Record results
        results[symbol] = "OK" if not null_metrics else f"MISSING: {len(null_metrics)} metrics"
        null_metrics_by_symbol[symbol] = null_metrics
        
        # Output the actual values for verification
        logger.info(f"Key metrics for {symbol}:")
        for metric in problem_metrics:
            value = parsed_data.get(metric)
            logger.info(f"  - {metric}: {value}")
                
    # Print summary
    logger.info("\n=== SUMMARY ===")
    for symbol, status in results.items():
        logger.info(f"{symbol}: {status}")
        if null_metrics_by_symbol.get(symbol):
            logger.info(f"  NULL metrics: {', '.join(null_metrics_by_symbol[symbol])}")
    
    # Output overall success rate
    success_count = sum(1 for status in results.values() if "ERROR" not in status and "MISSING" not in status)
    logger.info(f"\nSuccess rate: {success_count}/{len(test_symbols)} symbols processed without errors or missing metrics")

if __name__ == "__main__":
    test_key_metrics_ttm()
