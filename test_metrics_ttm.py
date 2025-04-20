import os
import json
import logging
from dotenv import load_dotenv
from fmp_fetcher.clients.fmp_client import get_single_symbol_data
from fmp_fetcher.utils.parsing import parse_key_metrics_ttm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
api_key = os.getenv("FMP_API_KEY")

if not api_key:
    raise ValueError("FMP_API_KEY environment variable is not set")

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

def test_key_metrics_ttm():
    """Test fetching and parsing of key metrics TTM data for multiple symbols."""
    results = {}
    null_metrics_by_symbol = {}
    
    for symbol in test_symbols:
        logger.info(f"Testing key metrics TTM for {symbol}")
        
        # Fetch TTM data from FMP
        try:
            # Use the get_single_symbol_data function with key metrics TTM endpoint
            ttm_data = get_single_symbol_data(symbol, "/key-metrics-ttm/{symbol}")
            if not ttm_data:
                logger.error(f"No TTM data received for {symbol}")
                results[symbol] = "ERROR: No data received"
                continue
                
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
                
        except Exception as e:
            logger.error(f"Error processing {symbol}: {str(e)}")
            results[symbol] = f"ERROR: {str(e)}"
    
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
