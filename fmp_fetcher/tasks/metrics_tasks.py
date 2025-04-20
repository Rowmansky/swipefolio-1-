# Replace the existing fetch_and_store_key_metrics_ttm function in
# fmp_fetcher/tasks/metrics_tasks.py with this corrected version:

import logging
from typing import List, Dict, Any, Optional
from typing_extensions import Literal

from ..clients import fmp_client, db_client
from ..utils import parsing
# from ..config import TARGET_SYMBOLS # Import if needed, or pass symbols as arg

logger = logging.getLogger(__name__)

def fetch_and_store_key_metrics_ttm(symbols: List[str]) -> Optional[bool]:
    """
    Fetches key metrics TTM (Trailing Twelve Months) for the given symbols and stores them in the database.
    
    Args:
        symbols: List of stock symbols to filter the bulk data
        
    Returns:
        True if operation was successful, False if some part failed, None if critical error
    """
    if not symbols:
        logger.warning("fetch_and_store_key_metrics_ttm called with empty symbols list.")
        return False
    
    logger.info(f"Starting Bulk TTM key metrics/ratios fetch for {len(symbols)} symbols.")
    
    try:
        # FIRST CHECK: Verify which symbols exist in the stocks table
        # to avoid foreign key constraint violations
        from ..config import get_supabase_client
        supabase = get_supabase_client()
        
        # Get the list of valid symbols from the stocks table
        logger.info("Checking which symbols exist in the stocks table...")
        try:
            response = supabase.table('stocks').select('symbol').execute()
            valid_symbols_records = response.data if hasattr(response, 'data') else []
            valid_symbols = set(record['symbol'] for record in valid_symbols_records if 'symbol' in record)
            
            # Filter our input symbols to only those that exist in the database
            filtered_symbols = [s for s in symbols if s in valid_symbols]
            
            if not filtered_symbols:
                logger.warning(f"None of the {len(symbols)} requested symbols exist in the stocks table. "
                              f"Need to fetch stock profiles first before metrics can be added.")
                return False
                
            if len(filtered_symbols) < len(symbols):
                missing_count = len(symbols) - len(filtered_symbols)
                logger.warning(f"Skipping {missing_count} symbols that don't exist in the stocks table. "
                              f"Filtered from {len(symbols)} to {len(filtered_symbols)} symbols.")
                symbols = filtered_symbols
        except Exception as e:
            logger.error(f"Error checking symbols in stocks table: {e}")
            # Continue with all symbols and let the database handle constraints
        
        # Attempt to fetch metrics from both TTM bulk endpoints
        metrics_data = {}
        ratios_data = {}
        
        # First try the bulk metrics endpoint (this gets ALL stocks at once)
        logger.info("Fetching data from /key-metrics-ttm-bulk...")
        try:
            bulk_metrics = fmp_client.make_fmp_request(
                "/key-metrics-ttm-bulk", 
                handle_csv=True  # Enable CSV response handling
            )
            if bulk_metrics and isinstance(bulk_metrics, list):
                # Filter to just the symbols we care about
                metrics_data = {item.get('symbol'): item for item in bulk_metrics if item.get('symbol') in symbols}
                logger.info(f"Successfully fetched TTM metrics via bulk endpoint. Found data for {len(metrics_data)} of {len(symbols)} requested symbols.")
            else:
                logger.warning("Bulk metrics endpoint returned invalid data format.")
        except Exception as e:
            logger.error(f"Failed to fetch bulk key metrics TTM from FMP API: {e}")
            metrics_data = {}  # Ensure empty if failed
            
        # Then try the bulk ratios endpoint (also gets ALL stocks at once)
        logger.info("Fetching data from /ratios-ttm-bulk...")
        try:
            bulk_ratios = fmp_client.make_fmp_request(
                "/ratios-ttm-bulk",
                handle_csv=True  # Enable CSV response handling
            )
            if bulk_ratios and isinstance(bulk_ratios, list):
                # Filter to just the symbols we care about
                ratios_data = {item.get('symbol'): item for item in bulk_ratios if item.get('symbol') in symbols}
                logger.info(f"Successfully fetched TTM ratios via bulk endpoint. Found data for {len(ratios_data)} of {len(symbols)} requested symbols.")
            else:
                logger.warning("Bulk ratios endpoint returned invalid data format.")
        except Exception as e:
            logger.error(f"Failed to fetch bulk ratios TTM from FMP API: {e}")
            ratios_data = {}  # Ensure empty if failed
            
        # Check if we got enough data
        all_symbols_with_data = set(metrics_data.keys()) | set(ratios_data.keys())
        if not all_symbols_with_data:
            logger.error("Failed to fetch any data from either bulk endpoint.")
            return False
            
        missing_symbols = set(symbols) - all_symbols_with_data
        if missing_symbols:
            logger.warning(f"No data found for {len(missing_symbols)} symbols: {', '.join(list(missing_symbols)[:10])}...")
        
        # Combined parsing and upsert of metrics/ratios data
        parsed_metrics = []
        
        # Process all symbols we found data for
        for symbol in all_symbols_with_data:
            # Get data from both sources if available
            metrics = metrics_data.get(symbol)
            ratios = ratios_data.get(symbol)
            
            # If we only have ratios data but no metrics data, use ratios as primary
            if not metrics and ratios:
                logger.info(f"Using ratios as primary data for {symbol}")
                metrics = ratios
                ratios = None
                
            # Parse combined data - our new parser function can handle both sources
            try:
                parsed = parsing.parse_key_metrics_ttm(metrics, symbol, ratios)
                if parsed:
                    parsed_metrics.append(parsed)
                else:
                    logger.warning(f"Failed to parse TTM data for {symbol}")
            except Exception as e:
                logger.error(f"Error parsing TTM data for {symbol}: {e}")
                
        # Upsert to database
        if not parsed_metrics:
            logger.warning("No valid TTM metrics parsed. Nothing to upsert.")
            return False
            
        logger.info(f"Upserting {len(parsed_metrics)} parsed TTM metrics records.")
        success = db_client.update_key_metrics_ttm(parsed_metrics)
        
        if success:
            logger.info(f"Successfully upserted {len(parsed_metrics)} TTM metrics records.")
        else:
            logger.error("Failed to upsert TTM metrics.")
            return False
            
        return True
        
    except Exception as e:
        logger.exception(f"Critical error in fetch_and_store_key_metrics_ttm: {e}")
        return None


# --- Historical Key Metrics Task ---

def fetch_and_store_key_metrics_historical(
    symbols: List[str],
    period: Literal['quarter', 'annual'] = 'quarter',
    limit: int = 40 # Fetch ~10 years of quarterly data or 40 annual
):
    """Fetches historical key metrics for the given symbols, period, and limit,
    parses them, and upserts into the 'key_metrics_historical' database table.

    Args:
        symbols: A list of stock symbols.
        period: The reporting period ('quarter' or 'annual').
        limit: The number of past periods to fetch.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_key_metrics_historical. Skipping.")
        return

    logger.info(f"Starting historical key metrics fetch for {len(symbols)} symbols. Period: {period}, Limit: {limit}.")

    all_parsed_metrics = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching historical key metrics for symbol: {symbol}, Period: {period}, Limit: {limit}")
        endpoint_path = f"/key-metrics/{symbol}"
        params = {'period': period, 'limit': limit}

        try:
            # --- Fetch Data ---
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch historical key metrics for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for historical key metrics for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} historical metric records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for metrics_data in api_data_list:
                parsed = parsing.parse_key_metrics_historical(metrics_data, symbol)
                if parsed:
                    all_parsed_metrics.append(parsed)
                else:
                    logger.warning(f"Failed to parse historical key metric record for {symbol} from data: {metrics_data}")
                    # Don't set has_errors for parsing failure, only fetch failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing historical key metrics for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_metrics:
        logger.warning(f"No valid historical key metrics could be parsed for the target symbols.")
        return # Exit if nothing was parsed

    logger.info(f"Attempting to upsert a total of {len(all_parsed_metrics)} historical key metrics records...")
    success = db_client.update_key_metrics_historical(all_parsed_metrics) # Assumes this DB function exists

    if success:
        logger.info(f"Successfully upserted {len(all_parsed_metrics)} historical key metrics records.")
    else:
        logger.error(f"Failed to upsert historical key metrics records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished historical key metrics fetch for {len(symbols)} requested symbols. Period: {period}. Encountered fetch errors: {has_errors}")


# --- Historical Financial Ratios Task ---

def fetch_and_store_financial_ratios_historical(
    symbols: List[str],
    period: Literal['quarter', 'annual'] = 'quarter',
    limit: int = 40 # Fetch ~10 years of quarterly data or 40 annual
):
    """Fetches historical financial ratios for the given symbols, period, and limit,
    parses them, and upserts into the 'financial_ratios_historical' database table.

    Args:
        symbols: A list of stock symbols.
        period: The reporting period ('quarter' or 'annual').
        limit: The number of past periods to fetch.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_financial_ratios_historical. Skipping.")
        return

    logger.info(f"Starting historical financial ratios fetch for {len(symbols)} symbols. Period: {period}, Limit: {limit}.")

    all_parsed_ratios = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching historical financial ratios for symbol: {symbol}, Period: {period}, Limit: {limit}")
        endpoint_path = f"/ratios/{symbol}"
        params = {'period': period, 'limit': limit}

        try:
            # --- Fetch Data ---
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch historical financial ratios for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for historical financial ratios for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} historical ratio records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for ratio_data in api_data_list:
                parsed = parsing.parse_financial_ratios_historical(ratio_data, symbol)
                if parsed:
                    all_parsed_ratios.append(parsed)
                else:
                    logger.warning(f"Failed to parse historical ratio record for {symbol} from data: {ratio_data}")
                    # Don't set has_errors for parsing failure, only fetch failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing historical financial ratios for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_ratios:
        logger.warning(f"No valid historical financial ratios could be parsed for the target symbols.")
        return # Exit if nothing was parsed

    logger.info(f"Attempting to upsert a total of {len(all_parsed_ratios)} historical financial ratios records...")
    # **** IMPORTANT: Assumes db_client has a function `update_financial_ratios_historical` ****
    success = db_client.update_financial_ratios_historical(all_parsed_ratios) 

    if success:
        logger.info(f"Successfully upserted {len(all_parsed_ratios)} historical financial ratios records.")
    else:
        logger.error(f"Failed to upsert historical financial ratios records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished historical financial ratios fetch for {len(symbols)} requested symbols. Period: {period}. Encountered fetch errors: {has_errors}")


# --- Historical Enterprise Values Task ---

def fetch_and_store_enterprise_values_historical(
    symbols: List[str],
    period: Literal['quarter', 'annual'] = 'quarter',
    limit: int = 40 # Fetch ~10 years of quarterly data or 40 annual
):
    """Fetches historical enterprise values for the given symbols, period, and limit,
    parses them, and upserts into the 'enterprise_values_historical' database table.

    Args:
        symbols: A list of stock symbols.
        period: The reporting period ('quarter' or 'annual').
        limit: The number of past periods to fetch.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_enterprise_values_historical. Skipping.")
        return

    logger.info(f"Starting historical enterprise values fetch for {len(symbols)} symbols. Period: {period}, Limit: {limit}.")

    all_parsed_evs = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching historical enterprise values for symbol: {symbol}, Period: {period}, Limit: {limit}")
        endpoint_path = f"/enterprise-values/{symbol}"
        params = {'period': period, 'limit': limit}

        try:
            # --- Fetch Data ---
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch historical enterprise values for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for historical enterprise values for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} historical EV records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for ev_data in api_data_list:
                parsed = parsing.parse_enterprise_value(ev_data, symbol)
                if parsed:
                    all_parsed_evs.append(parsed)
                else:
                    logger.warning(f"Failed to parse historical EV record for {symbol} from data: {ev_data}")
                    # Don't set has_errors for parsing failure, only fetch failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing historical enterprise values for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_evs:
        logger.warning(f"No valid historical enterprise values could be parsed for the target symbols.")
        return # Exit if nothing was parsed

    logger.info(f"Attempting to upsert a total of {len(all_parsed_evs)} historical enterprise values records...")
    # **** IMPORTANT: Assumes db_client has a function `update_enterprise_values_historical` ****
    success = db_client.update_enterprise_values_historical(all_parsed_evs) 

    if success:
        logger.info(f"Successfully upserted {len(all_parsed_evs)} historical enterprise values records.")
    else:
        logger.error(f"Failed to upsert historical enterprise values records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished historical enterprise values fetch for {len(symbols)} requested symbols. Period: {period}. Encountered fetch errors: {has_errors}")


# --- FMP Financial Scores Task ---

def fetch_and_store_fmp_scores(symbols: List[str], limit: int = 40):
    """Fetches historical FMP financial scores data for the given symbols,
    parses them, and upserts into the 'fmp_financial_scores_historical' database table.

    Args:
        symbols: A list of stock symbols.
        limit: The maximum number of historical data points to fetch per symbol.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_fmp_scores. Skipping.")
        return

    logger.info(f"Starting FMP financial scores fetch for {len(symbols)} symbols. Limit: {limit}.")

    all_parsed_scores = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching FMP financial scores for symbol: {symbol}, Limit: {limit}")
        endpoint_path = "/stable/financial-scores"
        params = {'symbol': symbol, 'limit': limit}

        try:
            # --- Fetch Data ---
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch FMP financial scores for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for FMP financial scores for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} FMP financial score records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for score_data in api_data_list:
                parsed = parsing.parse_fmp_financial_score(score_data, symbol)
                if parsed:
                    all_parsed_scores.append(parsed)
                else:
                    logger.warning(f"Failed to parse FMP financial score for {symbol} from data: {score_data}")
                    # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing FMP financial scores for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_scores:
        logger.warning(f"No valid FMP financial score records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_scores)} FMP financial score records...")
        success = db_client.update_fmp_financial_scores_historical(all_parsed_scores)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_scores)} FMP financial score records.")
        else:
            logger.error(f"Failed to upsert FMP financial score records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished FMP financial scores fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")