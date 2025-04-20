# fmp_fetcher/tasks/esg_tasks.py
import logging
from typing import List, Dict, Any
from datetime import datetime

from ..clients import fmp_client, db_client
from ..utils import parsing
# from ..config import TARGET_SYMBOLS # Import if needed or pass symbols

logger = logging.getLogger(__name__)


def fetch_and_store_esg_scores(symbols: List[str]):
    """Fetches the latest ESG scores for the given symbols,
    parses them, and upserts into the 'esg_scores_historical' database table.

    Args:
        symbols: A list of stock symbols.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_esg_scores. Skipping.")
        return

    logger.info(f"Starting ESG scores fetch for {len(symbols)} symbols.")

    all_parsed_scores = []
    has_errors = False

    for symbol in symbols:
        # Prepare per-symbol mappings
        disc_map: Dict[int, Dict[str, Any]] = {}  # year -> record with parsed date
        rating_map: Dict[int, str] = {}           # year -> rating grade

        # 1) ESG Disclosures (only 10-K forms)
        logger.debug(f"Fetching ESG disclosures for symbol: {symbol}")
        endpoint_path = "/stable/esg-disclosures"
        params = {'symbol': symbol}
        try:
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
            if api_data_list is None:
                logger.warning(f"Failed to fetch ESG disclosures for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for ESG disclosures for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue
            
            if not api_data_list: # Check if list is empty
                logger.info(f"No ESG disclosures data returned for {symbol}. Skipping symbol.")
                continue # Skip to next symbol
                
            logger.info(f"Received {len(api_data_list)} ESG disclosures records for {symbol}. Parsing...")

            for data in api_data_list:
                if data.get('formType') != '10-K':
                    continue
                parsed = parsing.parse_esg_historical(data, symbol, 'FMP ESG Disclosures')
                if not parsed:
                    logger.warning(f"Failed to parse disclosure for {symbol} from data: {data}")
                    continue
                # Keep latest 10-K per year
                dt = datetime.fromisoformat(parsed['report_date'])
                yr = parsed['calendar_year']
                existing = disc_map.get(yr)
                if not existing or dt > existing['_parsed_dt']:
                    rec = parsed.copy()
                    rec['_parsed_dt'] = dt
                    disc_map[yr] = rec

        except Exception as e:
            logger.exception(f"Error fetching/parsing ESG disclosures for {symbol}: {e}")
            has_errors = True

        # 2) ESG Ratings
        logger.debug(f"Fetching ESG ratings for symbol: {symbol}")
        endpoint_path = "/stable/esg-ratings"
        params = {'symbol': symbol}
        try:
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
            if api_data_list is None:
                logger.warning(f"Failed to fetch ESG ratings for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for ESG ratings for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue
            
            if not api_data_list: # Check if list is empty
                logger.info(f"No ESG ratings data returned for {symbol}. Skipping symbol.")
                continue # Skip to next symbol
                
            logger.info(f"Received {len(api_data_list)} ESG ratings records for {symbol}. Parsing...")

            for data in api_data_list:
                parsed = parsing.parse_esg_historical(data, symbol, 'FMP ESG Ratings')
                if not parsed:
                    logger.warning(f"Failed to parse rating for {symbol} from data: {data}")
                    continue
                rating_map[parsed['calendar_year']] = parsed.get('esg_rating_grade')

        except Exception as e:
            logger.exception(f"Error fetching/parsing ESG ratings for {symbol}: {e}")
            has_errors = True

        # --- Merge disclosures with ratings per year ---
        for yr, rec in disc_map.items():
            rec.pop('_parsed_dt', None)
            rec['esg_rating_grade'] = rating_map.get(yr)
            all_parsed_scores.append(rec)

    # --- Filter to last 3 calendar years ---
    current_year = datetime.now().year
    min_year = current_year - 2
    total = len(all_parsed_scores)
    all_parsed_scores = [r for r in all_parsed_scores if r.get('calendar_year') and r['calendar_year'] >= min_year]
    logger.info(f"Filtered ESG records from {total} to {len(all_parsed_scores)} for last 3 years (>= {min_year})")
    logger.debug("Final ESG payload before upsert: %s", all_parsed_scores)
    # --- Store Data ---    
    if not all_parsed_scores:
        logger.warning(f"No valid ESG score records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_scores)} ESG score records...")
        # **** IMPORTANT: Assumes db_client has a function `update_esg_scores_historical` ****
        success = db_client.update_esg_scores_historical(all_parsed_scores)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_scores)} ESG score records.")
        else:
            logger.error(f"Failed to upsert ESG score records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished ESG scores fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
    # Return the processed payload for inspection
    return all_parsed_scores
