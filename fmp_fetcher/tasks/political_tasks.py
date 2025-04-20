import logging
from typing import List, Dict, Any

from ..clients import fmp_client, db_client
from ..utils.parsing import parse_political_disclosure

logger = logging.getLogger(__name__)

def fetch_and_store_political_disclosures(symbols: List[str]) -> List[Dict[str, Any]]:
    """Fetches Senate and House trading disclosures for given symbols, parses, and upserts."""
    if not symbols:
        logger.warning("No symbols provided to fetch political disclosures. Skipping.")
        return []
    logger.info(f"Starting political disclosures fetch for {len(symbols)} symbols.")

    all_records: List[Dict[str, Any]] = []
    has_errors = False

    for symbol in symbols:
        for source, endpoint in [('Senate', '/stable/senate-trades'), ('House', '/stable/house-trades')]:
            logger.debug(f"Fetching {source} trades for symbol: {symbol}")
            try:
                api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint, params={'symbol': symbol})
                if not api_data_list or not isinstance(api_data_list, list):
                    logger.info(f"No {source} data or invalid format for {symbol}. Skipping.")
                    continue
                logger.info(f"Received {len(api_data_list)} {source} records for {symbol}. Parsing...")
                for item in api_data_list:
                    rec = parse_political_disclosure(item, source)
                    if rec:
                        all_records.append(rec)
            except Exception as e:
                logger.exception(f"Error fetching/parsing {source} trades for {symbol}: {e}")
                has_errors = True

    if not all_records:
        logger.warning("No valid political disclosure records parsed for target symbols.")
    else:
        # --- Filter to last 3 years of transaction_date ---
        from datetime import datetime, date
        total = len(all_records)
        min_year = date.today().year - 2
        filtered = []
        for rec in all_records:
            try:
                tx = datetime.fromisoformat(rec['transaction_date']).date()
                if tx.year >= min_year:
                    filtered.append(rec)
            except Exception:
                filtered.append(rec)
        logger.info(f"Filtered political disclosures from {total} to {len(filtered)} for last 3 years (>= {min_year})")
        all_records = filtered
        # Deduplicate records by ptr_link to avoid batch conflicts
        seen = {}
        for rec in all_records:
            seen[rec['ptr_link']] = rec
        unique_records = list(seen.values())
        logger.info(f"Deduplicated records: {len(all_records)} -> {len(unique_records)} unique ptr_links")
        all_records = unique_records
        # Print and log upsert action
        count = len(all_records)
        print(f"Upserting {count} political disclosure records...")
        success = db_client.update_political_disclosures(all_records)
        print(f"Update function returned: {success}")
        if success:
            logger.info(f"Successfully upserted {count} political disclosure records.")
        else:
            logger.error("Failed to upsert political disclosure records.")
    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished political disclosures fetch. Symbols: {symbols}. Errors: {has_errors}")
    logger.debug("Final political disclosures payload: %s", all_records)
    return all_records
