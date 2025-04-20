# fmp_fetcher/tasks/owner_earnings_tasks.py
import logging
from typing import List

from ..clients import fmp_client, db_client
from ..utils import parsing
# from ..config import TARGET_SYMBOLS # Import if needed or pass symbols

logger = logging.getLogger(__name__)

# Suppress verbose logs from HTTP and FMP client when running in INFO mode
for _lib in ("urllib3", "httpcore", "httpx", "hpack"):
    logging.getLogger(_lib).setLevel(logging.WARNING)
# Only show INFO+ for FMP client to reduce low-level debug spam
logging.getLogger("fmp_fetcher.clients.fmp_client").setLevel(logging.INFO)


def fetch_and_store_owner_earnings_historical(
    symbols: List[str],
    limit: int = 40 # Fetch up to 40 years of annual data
):
    """Fetches historical owner earnings for the given symbols and limit,
    parses them, and upserts into the 'owner_earnings_historical' database table.

    Note: FMP endpoint seems to provide annual data only.

    Args:
        symbols: A list of stock symbols.
        limit: The number of past annual periods to fetch.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_owner_earnings_historical. Skipping.")
        return

    logger.info(f"Starting historical owner earnings fetch for {len(symbols)} symbols. Limit: {limit}.")

    all_parsed_records = []
    has_errors = False

    for symbol in symbols:
        logger.info(f"Fetching owner earnings for {symbol}, Limit: {limit}")
        try:
            data = fmp_client.make_fmp_request(
                endpoint_path="/stable/owner-earnings",
                params={'symbol': symbol, 'limit': limit},
                handle_csv=False
            )
        except Exception as e:
            logger.exception(f"Exception fetching owner earnings for {symbol}: {e}")
            has_errors = True
            continue
        if not isinstance(data, list) or not data:
            logger.warning(f"No owner earnings data returned for {symbol}")
            has_errors = True
            continue
        logger.info(f"Received {len(data)} owner earnings records for {symbol}")
        for record_data in data:
            parsed = parsing.parse_owner_earnings(record_data, symbol)
            if parsed:
                all_parsed_records.append(parsed)
            else:
                logger.warning(f"Failed to parse owner earnings record for {symbol}: {record_data}")

    # --- Store Data ---    
    if not all_parsed_records:
        logger.warning(f"No valid historical owner earnings records could be parsed for the target symbols.")
        return # Exit if nothing was parsed

    logger.info(f"Attempting to upsert a total of {len(all_parsed_records)} historical owner earnings records...")
    # Upsert using owner earnings wrapper
    success = db_client.update_owner_earnings_historical(all_parsed_records)

    if success:
        logger.info(f"Successfully upserted {len(all_parsed_records)} historical owner earnings records.")
    else:
        logger.error(f"Failed to upsert historical owner earnings records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished historical owner earnings fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
