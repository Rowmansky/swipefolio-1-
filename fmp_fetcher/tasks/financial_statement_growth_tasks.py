# fmp_fetcher/tasks/financial_statement_growth_tasks.py
import logging
from typing import List
from typing_extensions import Literal

from ..clients import fmp_client, db_client
from ..utils import parsing
# from ..config import TARGET_SYMBOLS # Import if needed or pass symbols

logger = logging.getLogger(__name__)

# Map DB enum to FMP endpoint parts if necessary (though parser handles DB type)
STATEMENT_TYPES = ['income', 'balance', 'cashflow'] # Corresponds to DB enum


def fetch_and_store_statement_growth(
    symbols: List[str],
    period: Literal['quarter', 'annual'] = 'quarter',
    limit: int = 40 # Fetch ~10 years of quarterly data or 40 annual
):
    """Fetches financial statement growth metrics for given symbols, period, and limit,
    parses them, and upserts into the 'financial_statement_growth' database table.

    Args:
        symbols: A list of stock symbols.
        period: The reporting period ('quarter' or 'annual').
        limit: The number of past periods to fetch.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_statement_growth. Skipping.")
        return

    logger.info(f"Starting financial statement growth fetch for {len(symbols)} symbols. Period: {period}, Limit: {limit}.")

    all_parsed_growth_records = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching statement growth for symbol: {symbol}, Period: {period}, Limit: {limit}")
        # FMP endpoint requires statement type in the path
        # Need to map db type back to FMP path component if needed
        # Example: '/income-statement-growth/', '/balance-sheet-statement-growth/', '/cash-flow-statement-growth/'
        # We iterate through the 3 types per symbol.

        for statement_type in STATEMENT_TYPES: # Use 'income', 'balance', 'cashflow'
            # Construct FMP endpoint path (adjust if FMP uses different names)
            fmp_statement_segment = statement_type
            if statement_type == 'balance':
                fmp_statement_segment = 'balance-sheet-statement'
            elif statement_type == 'cashflow':
                fmp_statement_segment = 'cash-flow-statement'
            else: # income
                fmp_statement_segment = 'income-statement'

            endpoint_path = f"/{fmp_statement_segment}-growth/{symbol}"
            params = {'period': period, 'limit': limit}
            
            logger.debug(f"Fetching {statement_type} growth from {endpoint_path}")

            try:
                # --- Fetch Data ---
                api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

                if api_data_list is None:
                    logger.warning(f"Failed to fetch {statement_type} growth for {symbol}. Skipping type for this symbol.")
                    has_errors = True
                    continue # Skip to next statement type for this symbol

                if not isinstance(api_data_list, list):
                    logger.warning(f"Expected a list for {statement_type} growth for {symbol}, got {type(api_data_list)}. Skipping type for this symbol.")
                    has_errors = True
                    continue

                logger.info(f"Received {len(api_data_list)} {statement_type} growth records for {symbol}. Parsing...")

                # --- Parse Data ---            
                for growth_data in api_data_list:
                    # Pass the db_statement_type ('income', 'balance', 'cashflow') to the parser
                    parsed = parsing.parse_statement_growth(growth_data, symbol, statement_type)
                    if parsed:
                        all_parsed_growth_records.append(parsed)
                    else:
                        logger.warning(f"Failed to parse {statement_type} growth record for {symbol} from data: {growth_data}")
                        # Don't set has_errors for parsing failure

            except Exception as e:
                logger.exception(f"Error fetching/parsing {statement_type} growth for {symbol}: {e}")
                has_errors = True
                # Continue with other statement types/symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_growth_records:
        logger.warning(f"No valid financial statement growth records could be parsed for the target symbols.")
        return # Exit if nothing was parsed

    logger.info(f"Attempting to upsert a total of {len(all_parsed_growth_records)} financial statement growth records...")
    # **** IMPORTANT: Assumes db_client has a function `update_financial_statement_growth` ****
    success = db_client.update_financial_statement_growth(all_parsed_growth_records)

    if success:
        logger.info(f"Successfully upserted {len(all_parsed_growth_records)} financial statement growth records.")
    else:
        logger.error(f"Failed to upsert financial statement growth records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished financial statement growth fetch for {len(symbols)} requested symbols. Period: {period}. Encountered fetch errors: {has_errors}")
