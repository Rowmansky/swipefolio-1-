# fmp_fetcher/tasks/ownership_tasks.py
import logging
import datetime
from typing import List, Tuple

from ..clients import fmp_client, db_client
from ..utils import parsing

logger = logging.getLogger(__name__)


def _get_quarter_window(full_years: int = 2, partial_quarters: int = 2) -> List[Tuple[int, int]]:
    """Generate quarter slices: last `full_years` full years and first `partial_quarters` of current year."""
    now = datetime.datetime.now()
    current_year = now.year
    quarters: List[Tuple[int, int]] = []
    # Full past years
    for year in range(current_year - full_years, current_year):
        for q in range(1, 5):
            quarters.append((year, q))
    # Partial current year
    for q in range(1, partial_quarters + 1):
        quarters.append((current_year, q))
    return quarters


def fetch_and_store_inst_own_summary(symbols: List[str], full_years: int = 2, partial_quarters: int = 2):
    """Fetches institutional ownership summary data for the given symbols,
    parses them, and upserts into the 'institutional_ownership_summary' database table.
    
    Fetches data for the most recent quarters.

    Args:
        symbols: A list of stock symbols.
        full_years: Number of full years to fetch for each symbol.
        partial_quarters: Number of partial quarters to fetch for each symbol.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_inst_own_summary. Skipping.")
        return

    # Get the defined quarter window
    latest_quarters = _get_quarter_window(full_years, partial_quarters)
    
    logger.info(f"Starting institutional ownership summary fetch for {len(symbols)} symbols across {len(latest_quarters)} quarters.")

    all_parsed_summaries = []
    has_errors = False

    for symbol in symbols:
        for year, quarter in latest_quarters:
            logger.debug(f"Fetching institutional ownership summary for symbol: {symbol}, Year: {year}, Quarter: {quarter}")
            endpoint_path = "/stable/institutional-ownership/symbol-positions-summary"
            params = {'symbol': symbol, 'year': year, 'quarter': quarter}

            try:
                # --- Fetch Data ---
                api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

                if api_data_list is None:
                    logger.warning(f"Failed to fetch institutional ownership summary for {symbol} (Year: {year}, Quarter: {quarter}). Skipping this quarter.")
                    continue 
                if not isinstance(api_data_list, list):
                    logger.warning(f"Expected a list for Inst Ownership Summary for {symbol}, got {type(api_data_list)}. Skipping.")
                    has_errors = True
                    continue
                if not api_data_list:
                    # No data returned
                    continue
                # --- Parse Data ---
                for summary_data in api_data_list:
                    parsed = parsing.parse_inst_ownership_summary(summary_data, symbol)
                    if parsed:
                        all_parsed_summaries.append(parsed)
                    else:
                        logger.warning(f"Failed to parse institutional ownership summary for {symbol} data: {summary_data}")

            except Exception as e:
                logger.exception(f"Error fetching/parsing institutional ownership summary for {symbol} (Year: {year}, Quarter: {quarter}): {e}")
                has_errors = True
                # Continue with other quarters/symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_summaries:
        logger.warning(f"No valid institutional ownership summary records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_summaries)} institutional ownership summary records...")
        success = db_client.update_institutional_ownership_summary(all_parsed_summaries)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_summaries)} institutional ownership summary records.")
        else:
            logger.error(f"Failed to upsert institutional ownership summary records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished institutional ownership summary fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")


def fetch_and_store_inst_holdings(symbols: List[str], full_years: int = 2, partial_quarters: int = 2, top_holders_limit: int = 100):
    """Fetches institutional holdings detail data for the given symbols,
    parses them, and upserts into the 'institutional_holdings' database table.
    
    Fetches data for the most recent quarters, potentially limiting to top holders per symbol.

    Args:
        symbols: A list of stock symbols.
        full_years: Number of full years to fetch for each symbol.
        partial_quarters: Number of partial quarters to fetch for each symbol.
        top_holders_limit: Maximum number of holders to fetch per symbol per quarter.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_inst_holdings. Skipping.")
        return

    # Get the defined quarter window
    latest_quarters = _get_quarter_window(full_years, partial_quarters)
    
    logger.info(f"Starting institutional holdings detail fetch for {len(symbols)} symbols across {len(latest_quarters)} quarters.")

    all_parsed_holdings = []
    has_errors = False

    for symbol in symbols:
        for year, quarter in latest_quarters:
            logger.debug(f"Fetching institutional holdings detail for symbol: {symbol}, Year: {year}, Quarter: {quarter}")
            endpoint_path = "/stable/institutional-ownership/extract-analytics/holder"
            params = {'symbol': symbol, 'year': year, 'quarter': quarter, 'limit': top_holders_limit}

            try:
                # --- Fetch Data ---
                api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

                if api_data_list is None:
                    logger.warning(f"Failed to fetch institutional holdings detail for {symbol} (Year: {year}, Quarter: {quarter}). Skipping.")
                    continue
                if not isinstance(api_data_list, list):
                    logger.warning(f"Expected a list for Inst Holding Detail for {symbol}, got {type(api_data_list)}. Skipping.")
                    has_errors = True
                    continue
                if not api_data_list:
                    # No data returned
                    continue

                # --- Parse Data ---
                logger.info(f"Received {len(api_data_list)} institutional holder records for {symbol} (Year: {year}, Quarter: {quarter}). Parsing...")

                for holding_data in api_data_list:
                    parsed = parsing.parse_inst_holding_detail(holding_data, symbol)
                    if parsed:
                        all_parsed_holdings.append(parsed)
                    else:
                        logger.warning(f"Failed to parse institutional holding detail for {symbol} from data: {holding_data}")

            except Exception as e:
                logger.exception(f"Error fetching/parsing institutional holdings detail for {symbol} (Year: {year}, Quarter: {quarter}): {e}")
                has_errors = True
                # Continue with other quarters/symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_holdings:
        logger.warning(f"No valid institutional holdings detail records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_holdings)} institutional holdings detail records...")
        success = db_client.update_institutional_holdings(all_parsed_holdings)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_holdings)} institutional holdings detail records.")
        else:
            logger.error(f"Failed to upsert institutional holdings detail records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished institutional holdings detail fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
