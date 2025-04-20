# fmp_fetcher/tasks/estimates_tasks.py
import logging
from typing import List

from ..clients import fmp_client, db_client
from ..utils import parsing

logger = logging.getLogger(__name__)


def fetch_and_store_financial_estimates(symbols: List[str], quarterly_limit: int = 8, annual_limit: int = 5):
    """Fetches financial estimates (analyst estimates) for the given symbols,
    parses them, and upserts into the 'financial_estimates' database table.
    Gets both quarterly (2 years) and annual (5 years) estimates.

    Args:
        symbols: A list of stock symbols.
        quarterly_limit: The number of quarters to fetch (default 8 = 2 years).
        annual_limit: The number of years to fetch (default 5 years).
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_financial_estimates. Skipping.")
        return

    logger.info(f"Starting financial estimates fetch for {len(symbols)} symbols.")

    all_parsed_estimates = []
    has_errors = False

    # Define the periods to fetch
    periods = [
        {"period": "quarter", "limit": quarterly_limit},
        {"period": "annual", "limit": annual_limit}
    ]

    for symbol in symbols:
        for period_config in periods:
            period = period_config["period"]
            limit = period_config["limit"]
            
            logger.debug(f"Fetching {period} financial estimates for symbol: {symbol}, Limit: {limit}")
            endpoint_path = "/stable/analyst-estimates"
            params = {'symbol': symbol, 'period': period, 'limit': limit}

            try:
                # --- Fetch Data ---
                api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

                if api_data_list is None:
                    logger.warning(f"Failed to fetch {period} financial estimates for {symbol}. Skipping.")
                    has_errors = True
                    continue # Skip to next period/symbol

                if not isinstance(api_data_list, list):
                    logger.warning(f"Expected a list for {period} financial estimates for {symbol}, got {type(api_data_list)}. Skipping.")
                    has_errors = True
                    continue

                logger.info(f"Received {len(api_data_list)} {period} financial estimate records for {symbol}. Parsing...")

                # --- Parse Data ---            
                for estimate_data in api_data_list:
                    # Add symbol and period if not in response
                    if 'symbol' not in estimate_data:
                        estimate_data['symbol'] = symbol
                    if 'period' not in estimate_data:
                        estimate_data['period'] = period
                        
                    parsed = parsing.parse_financial_estimate(estimate_data)
                    if parsed:
                        all_parsed_estimates.append(parsed)
                    else:
                        logger.warning(f"Failed to parse {period} financial estimate for {symbol} from data: {estimate_data}")
                        # Don't set has_errors for parsing failure

            except Exception as e:
                logger.exception(f"Error fetching/parsing {period} financial estimates for {symbol}: {e}")
                has_errors = True
                # Continue with other periods/symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_estimates:
        logger.warning(f"No valid financial estimate records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_estimates)} financial estimate records...")
        success = db_client.update_financial_estimates(all_parsed_estimates)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_estimates)} financial estimate records.")
        else:
            logger.error(f"Failed to upsert financial estimate records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished financial estimates fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
