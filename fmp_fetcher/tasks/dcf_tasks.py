# fmp_fetcher/tasks/dcf_tasks.py
import logging
from typing import List

from ..clients import fmp_client, db_client
from ..utils import parsing
# from ..config import TARGET_SYMBOLS # Import if needed or pass symbols

logger = logging.getLogger(__name__)


def fetch_and_store_dcf_valuations(symbols: List[str]):
    """Fetches both standard and levered DCF valuations for the given symbols,
    parses them, and upserts into the 'dcf_valuations' database table.

    Args:
        symbols: A list of stock symbols.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_dcf_valuations. Skipping.")
        return

    logger.info(f"Starting DCF valuations fetch for {len(symbols)} symbols.")

    all_parsed_dcfs = []
    has_errors = False

    # Define the DCF types to fetch
    dcf_types = [
        {"path": "/discounted-cash-flow", "type": "Standard"},
        {"path": "/levered-discounted-cash-flow", "type": "Levered"}
    ]

    for symbol in symbols:
        logger.debug(f"Fetching DCF valuations for symbol: {symbol}")
        
        # Fetch both standard and levered DCF for each symbol
        for dcf_config in dcf_types:
            endpoint_path = dcf_config["path"]
            dcf_type = dcf_config["type"]
            params = {'symbol': symbol}
            
            try:
                # --- Fetch Data ---
                api_data = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

                if api_data is None:
                    logger.warning(f"Failed to fetch {dcf_type} DCF valuation for {symbol}. Skipping.")
                    has_errors = True
                    continue # Skip to next DCF type

                # --- Parse Data ---            
                parsed = parsing.parse_dcf_valuation(api_data, dcf_type)
                if parsed:
                    all_parsed_dcfs.append(parsed)
                    logger.debug(f"Successfully parsed {dcf_type} DCF valuation for {symbol}")
                else:
                    logger.warning(f"Failed to parse {dcf_type} DCF valuation for {symbol}")
                    # Don't set has_errors for parsing failure

            except Exception as e:
                logger.exception(f"Error fetching/parsing {dcf_type} DCF valuation for {symbol}: {e}")
                has_errors = True
                # Continue with other DCF types and symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_dcfs:
        logger.warning(f"No valid DCF valuation records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_dcfs)} DCF valuation records...")
        # **** IMPORTANT: Assumes db_client has a function `update_dcf_valuations` ****
        success = db_client.update_dcf_valuations(all_parsed_dcfs)


        if success:
            logger.info(f"Successfully upserted {len(all_parsed_dcfs)} DCF valuation records.")
        else:
            logger.error(f"Failed to upsert DCF valuation records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished DCF valuations fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
