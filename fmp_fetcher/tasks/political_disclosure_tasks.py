# fmp_fetcher/tasks/political_disclosure_tasks.py
import logging
from typing import List

from ..clients import fmp_client, db_client
from ..utils import parsing
# from ..config import TARGET_SYMBOLS # Import if needed or pass symbols

logger = logging.getLogger(__name__)

# Define a reasonable limit for recent disclosures
DEFAULT_DISCLOSURE_LIMIT = 100

def fetch_and_store_political_disclosures(symbols: List[str], limit: int = DEFAULT_DISCLOSURE_LIMIT):
    """Fetches recent political disclosure data for the given symbols from both Senate and House trades,
    parses them, and upserts into the 'political_disclosures' database table.

    Args:
        symbols: A list of stock symbols.
        limit: The maximum number of recent disclosures to fetch per symbol per source.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_political_disclosures. Skipping.")
        return

    logger.info(f"Starting political disclosures fetch for {len(symbols)} symbols. Limit per symbol per source: {limit}.")

    all_parsed_disclosures = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching political disclosures for symbol: {symbol}, Limit: {limit}")
        
        # CORRECTION: Use separate endpoints for Senate and House trades
        # Define the two endpoints to fetch from
        endpoints = [
            {"path": "/stable/senate-trades", "source": "Senate"},
            {"path": "/stable/house-trades", "source": "House"}
        ]
        
        for endpoint in endpoints:
            endpoint_path = endpoint["path"]
            source = endpoint["source"]
            params = {'symbol': symbol, 'limit': limit}
            
            try:
                # --- Fetch Data ---
                # Fetch from each source separately
                api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

                if api_data_list is None:
                    logger.warning(f"Failed to fetch {source} political disclosures for {symbol}. Skipping this source.")
                    has_errors = True
                    continue # Skip to next endpoint

                if not isinstance(api_data_list, list):
                    logger.warning(f"Expected a list for {source} political disclosures for {symbol}, got {type(api_data_list)}. Skipping this source.")
                    has_errors = True
                    continue

                logger.info(f"Received {len(api_data_list)} {source} political disclosure records for {symbol}. Parsing...")

                # --- Parse Data ---            
                for disclosure_data in api_data_list:
                    # Pass the source (Senate/House) to the parser
                    parsed = parsing.parse_political_disclosure(disclosure_data, source)
                    if parsed:
                        all_parsed_disclosures.append(parsed)
                    else:
                        logger.warning(f"Failed to parse {source} political disclosure record for {symbol} from data: {disclosure_data}")
                        # Don't set has_errors for parsing failure

            except Exception as e:
                logger.exception(f"Error fetching/parsing {source} political disclosures for {symbol}: {e}")
                has_errors = True
                # Continue with other sources/symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_disclosures:
        logger.warning(f"No valid political disclosure records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_disclosures)} political disclosure records...")
        # **** IMPORTANT: Assumes db_client has a function `update_political_disclosures` ****
        success = db_client.update_political_disclosures(all_parsed_disclosures)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_disclosures)} political disclosure records.")
        else:
            logger.error(f"Failed to upsert political disclosure records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished political disclosures fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
