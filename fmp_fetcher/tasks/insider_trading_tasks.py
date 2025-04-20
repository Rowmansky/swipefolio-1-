# fmp_fetcher/tasks/insider_trading_tasks.py
import logging
import datetime
from typing import List

from ..clients import fmp_client, db_client
from ..utils import parsing
# from ..config import TARGET_SYMBOLS # Import if needed or pass symbols

logger = logging.getLogger(__name__)

# Define a reasonable limit for recent trades
DEFAULT_INSIDER_TRADE_LIMIT = 100

def fetch_and_store_insider_trades(symbols: List[str], limit: int = DEFAULT_INSIDER_TRADE_LIMIT):
    """Fetches recent insider trading data for the given symbols,
    parses them, and upserts into the 'insider_trades' database table.

    Args:
        symbols: A list of stock symbols.
        limit: The maximum number of recent trades to fetch per symbol.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_insider_trades. Skipping.")
        return

    logger.info(f"Starting insider trades fetch for {len(symbols)} symbols. Limit per symbol: {limit}.")

    all_parsed_trades = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching insider trades for symbol: {symbol}, Limit: {limit}")
        # CORRECTION: Use the correct endpoint with query parameters
        endpoint_path = "/stable/insider-trading/search"
        params = {'symbol': symbol, 'limit': limit}

        try:
            # --- Fetch Data ---
            # Assuming the response is a list of trade objects
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch insider trades for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for insider trades for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} insider trade records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for trade_data in api_data_list:
                parsed = parsing.parse_insider_trade(trade_data)
                if parsed:
                    all_parsed_trades.append(parsed)
                else:
                    logger.warning(f"Failed to parse insider trade record for {symbol} from data: {trade_data}")
                    # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing insider trades for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_trades:
        logger.warning(f"No valid insider trade records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_trades)} insider trade records...")
        # **** IMPORTANT: Assumes db_client has a function `update_insider_trades` ****
        success = db_client.update_insider_trades(all_parsed_trades)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_trades)} insider trade records.")
        else:
            logger.error(f"Failed to upsert insider trade records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished insider trades fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
    return all_parsed_trades

def fetch_and_store_insider_trading_stats(symbols: List[str]):
    """Fetches insider trading statistics data for the given symbols,
    parses them, and upserts into the 'insider_trading_stats' database table.

    Args:
        symbols: A list of stock symbols.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_insider_trading_stats. Skipping.")
        return

    logger.info(f"Starting insider trading statistics fetch for {len(symbols)} symbols.")
    # Only include statistics from the last 3 years
    cutoff_year = datetime.date.today().year - 3

    all_parsed_stats = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching insider trading statistics for symbol: {symbol}")
        endpoint_path = "/stable/insider-trading/statistics"
        params = {'symbol': symbol}

        try:
            # --- Fetch Data ---
            api_data = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data is None:
                logger.warning(f"Failed to fetch insider trading statistics for {symbol}. Skipping symbol.")
                has_errors = True
                continue

            # Normalize to list of stats records
            stats_list = api_data if isinstance(api_data, list) else [api_data]
            if not stats_list:
                logger.warning(f"No insider trading statistics returned for {symbol}. Skipping symbol.")
                continue

            # --- Parse Data ---
            for stat in stats_list:
                parsed = parsing.parse_insider_trading_stats(stat, symbol)
                if parsed:
                    if parsed.get('stats_year', 0) < cutoff_year:
                        continue
                    all_parsed_stats.append(parsed)
                else:
                    logger.warning(f"Failed to parse insider trading statistics for {symbol} from data: {stat}")

        except Exception as e:
            logger.exception(f"Error fetching/parsing insider trading statistics for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_stats:
        logger.warning("No valid insider trading statistics records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_stats)} insider trading statistics records...")
        success = db_client.update_insider_trading_stats(all_parsed_stats)

        if success:
            logger.info(f"Successfully upserted {len(all_parsed_stats)} insider trading statistics records.")
        else:
            logger.error("Failed to upsert insider trading statistics records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished insider trading statistics fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
    return all_parsed_stats
