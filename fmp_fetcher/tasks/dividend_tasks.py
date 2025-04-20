# fmp_fetcher/tasks/dividend_tasks.py
import logging
from typing import List
import datetime

from ..clients import fmp_client, db_client
from ..utils import parsing
# from ..config import TARGET_SYMBOLS # Import if needed or pass symbols

logger = logging.getLogger(__name__)


def fetch_and_store_dividends_historical(symbols: List[str]):
    """Fetches the full historical dividend data for the given symbols,
    parses them, and upserts into the 'dividends_historical' database table.

    Args:
        symbols: A list of stock symbols.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_dividends_historical. Skipping.")
        return

    logger.info(f"Starting historical dividends fetch for {len(symbols)} symbols.")
    # Only include dividends from the last 5 years
    cutoff_date = datetime.date.today() - datetime.timedelta(days=5*365)
     
    all_parsed_dividends = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching historical dividends for symbol: {symbol}")
        # CORRECTION: Use the correct endpoint with query parameters
        endpoint_path = "/stable/dividends"
        params = {'symbol': symbol}

        try:
            # --- Fetch Data ---
            # Assuming the response is a list of dividend objects
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch historical dividends for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol
                
            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for dividends of {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} historical dividend records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for dividend_data in api_data_list:
                parsed = parsing.parse_dividend(dividend_data, symbol)
                if parsed:
                    # filter by date
                    try:
                        d = datetime.datetime.strptime(parsed['date'], '%Y-%m-%d').date()
                    except Exception:
                        logger.warning(f"Invalid date format for dividend: {parsed['date']}")
                        continue
                    if d < cutoff_date:
                        continue
                    all_parsed_dividends.append(parsed)
                else:
                    logger.warning(f"Failed to parse historical dividend record for {symbol} from data: {dividend_data}")
                    # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing historical dividends for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_dividends:
        logger.warning(f"No valid historical dividend records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_dividends)} historical dividend records...")
        # **** IMPORTANT: Assumes db_client has a function `update_dividends_historical` ****
        success = db_client.update_dividends_historical(all_parsed_dividends)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_dividends)} historical dividend records.")
        else:
            logger.error(f"Failed to upsert historical dividend records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished historical dividends fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
    return all_parsed_dividends
