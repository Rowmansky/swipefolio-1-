# fmp_fetcher/tasks/earnings_tasks.py
import logging
import datetime
from typing import List

from ..clients import fmp_client, db_client
from ..utils import parsing
# from ..config import TARGET_SYMBOLS # Import if needed or pass symbols

logger = logging.getLogger(__name__)


def fetch_and_store_earnings_reports(symbols: List[str]):
    """Fetches historical earnings report data for the given symbols,
    parses them, and upserts into the 'earnings_reports' database table.

    Args:
        symbols: A list of stock symbols.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_earnings_reports. Skipping.")
        return

    logger.info(f"Starting earnings reports fetch for {len(symbols)} symbols.")
    # Only include earnings from the last 5 years
    cutoff_date = datetime.date.today() - datetime.timedelta(days=5*365)

    all_parsed_reports = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching earnings reports for symbol: {symbol}")
        # CORRECTION: Use the correct endpoint with query parameters
        endpoint_path = "/stable/earnings"
        params = {'symbol': symbol}

        try:
            # --- Fetch Data ---
            # Assuming the response is a list of earnings report objects
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch earnings reports for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for earnings reports for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} earnings report records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for report_data in api_data_list:
                # parse with symbol
                parsed = parsing.parse_earnings_report(report_data, symbol)
                if parsed:
                    # filter by date
                    try:
                        d = datetime.datetime.strptime(parsed['date'], '%Y-%m-%d').date()
                    except Exception:
                        logger.warning(f"Invalid date format for earnings: {parsed['date']}")
                        continue
                    if d < cutoff_date:
                        continue
                    all_parsed_reports.append(parsed)
                else:
                    logger.warning(f"Failed to parse earnings report record for {symbol} from data: {report_data}")
                    # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing earnings reports for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_reports:
        logger.warning(f"No valid earnings report records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_reports)} earnings report records...")
        # **** IMPORTANT: Assumes db_client has a function `update_earnings_reports` ****
        success = db_client.update_earnings_reports(all_parsed_reports)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_reports)} earnings report records.")
        else:
            logger.error(f"Failed to upsert earnings report records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished earnings reports fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
    return all_parsed_reports
