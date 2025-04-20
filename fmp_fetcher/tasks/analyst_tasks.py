# fmp_fetcher/tasks/analyst_tasks.py
import logging
from typing import List, Dict, Any

from ..clients import fmp_client, db_client
from ..utils import parsing
from fmp_fetcher.tasks.stock_data_tasks import fetch_and_store_profiles
from fmp_fetcher.config import get_supabase_client

logger = logging.getLogger(__name__)


def fetch_and_store_price_target_news(symbols: List[str], limit: int = 100):
    """Fetches recent price target news for the given symbols,
    parses them, and upserts into the 'analyst_ratings' database table.

    Args:
        symbols: A list of stock symbols.
        limit: The maximum number of news items to fetch per symbol.
    """
    
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_price_target_news. Skipping.")
        return

    logger.info(f"Starting price target news fetch for {len(symbols)} symbols. Limit per symbol: {limit}.")

    all_parsed_ratings = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching price target news for symbol: {symbol}, Limit: {limit}")
        endpoint_path = "/stable/price-target-news"
        params = {'symbol': symbol, 'limit': limit}

        try:
            # --- Fetch Data ---
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch price target news for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for price target news for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} price target news records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for news_data in api_data_list:
                parsed = parsing.parse_analyst_rating(news_data, source='FMP Price Target News')
                if parsed:
                    all_parsed_ratings.append(parsed)
                else:
                    logger.warning(f"Failed to parse price target news for {symbol} from data: {news_data}")
                    # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing price target news for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_ratings:
        logger.warning(f"No valid price target news records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_ratings)} price target news records...")
        # Deduplicate before upsert
        unique_map: Dict[tuple, Dict[str, Any]] = {}
        for rec in all_parsed_ratings:
            key = (rec.get("symbol"), rec.get("date"), rec.get("source"), rec.get("rating_analyst_firm"))
            unique_map[key] = rec
        deduped = list(unique_map.values())
        success = db_client.update_analyst_ratings(deduped)

        if success:
            logger.info(f"Successfully upserted {len(deduped)} price target news records.")
        else:
            logger.error(f"Failed to upsert price target news records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished price target news fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")


def fetch_and_store_grade_news(symbols: List[str], limit: int = 15):
    """Fetches recent grade news for the given symbols,
    parses them, and upserts into the 'analyst_ratings' database table.

    Args:
        symbols: A list of stock symbols.
        limit: The maximum number of grade news items to fetch per symbol.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_grade_news. Skipping.")
        return

    logger.info(f"Starting grade news fetch for {len(symbols)} symbols. Limit per symbol: {limit}.")

    all_parsed_ratings = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching grade news for symbol: {symbol}, Limit: {limit}")
        endpoint_path = "/stable/grades-news"
        params = {'symbol': symbol, 'limit': limit}

        try:
            # --- Fetch Data ---
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch grade news for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for grade news for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} grade news records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for news_data in api_data_list:
                parsed = parsing.parse_analyst_rating(news_data, source='FMP Grade News')
                if parsed:
                    all_parsed_ratings.append(parsed)
                else:
                    logger.warning(f"Failed to parse grade news for {symbol} from data: {news_data}")
                    # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing grade news for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_ratings:
        logger.warning(f"No valid grade news records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_ratings)} grade news records...")
        # Deduplicate before upsert
        unique_map: Dict[tuple, Dict[str, Any]] = {}
        for rec in all_parsed_ratings:
            key = (rec.get("symbol"), rec.get("date"), rec.get("source"), rec.get("rating_analyst_firm"))
            unique_map[key] = rec
        deduped = list(unique_map.values())
        success = db_client.update_analyst_ratings(deduped)

        if success:
            logger.info(f"Successfully upserted {len(deduped)} grade news records.")
        else:
            logger.error(f"Failed to upsert grade news records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished grade news fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")


def fetch_and_store_current_grades(symbols: List[str], limit: int = 5):
    """Fetches current grades for the given symbols,
    parses them, and upserts into the 'analyst_ratings' database table.

    Args:
        symbols: A list of stock symbols.
        limit: The maximum number of current grades to fetch per symbol.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_current_grades. Skipping.")
        return

    logger.info(f"Starting current grades fetch for {len(symbols)} symbols. Limit per symbol: {limit}.")

    all_parsed_ratings = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching current grades for symbol: {symbol}, Limit: {limit}")
        endpoint_path = "/stable/grades"
        params = {'symbol': symbol, 'limit': limit}

        try:
            # --- Fetch Data ---
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
            # DEBUG: log raw API payload for current grades
            logger.debug("RAW current grades API data for %s: %s", symbol, api_data_list)

            if api_data_list is None:
                logger.warning(f"Failed to fetch current grades for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for current grades for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} current grade records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for grade_data in api_data_list:
                parsed = parsing.parse_analyst_rating(grade_data, source='FMP Grade Current')
                if parsed:
                    all_parsed_ratings.append(parsed)
                else:
                    logger.warning(f"Failed to parse current grade for {symbol} from data: {grade_data}")
                    # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing current grades for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_ratings:
        logger.warning(f"No valid current grade records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_ratings)} current grade records...")
        # Deduplicate before upsert
        unique_map: Dict[tuple, Dict[str, Any]] = {}
        for rec in all_parsed_ratings:
            key = (rec.get("symbol"), rec.get("date"), rec.get("source"), rec.get("rating_analyst_firm"))
            unique_map[key] = rec
        deduped = list(unique_map.values())
        success = db_client.update_analyst_ratings(deduped)

        if success:
            logger.info(f"Successfully upserted {len(deduped)} current grade records.")
        else:
            logger.error(f"Failed to upsert current grade records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished current grades fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")


def fetch_and_store_ratings_snapshot(symbols: List[str]):
    """Fetches ratings snapshots for the given symbols,
    parses them, and upserts into the 'analyst_ratings' database table.

    Args:
        symbols: A list of stock symbols.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_ratings_snapshot. Skipping.")
        return

    logger.info(f"Starting ratings snapshot fetch for {len(symbols)} symbols.")

    all_parsed_ratings = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching ratings snapshot for symbol: {symbol}")
        endpoint_path = "/stable/ratings-snapshot"
        params = {'symbol': symbol}

        try:
            # --- Fetch Data ---
            api_data = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
            # DEBUG: log raw API payload for ratings snapshot
            logger.debug("RAW ratings snapshot API data for %s: %s", symbol, api_data)

            if api_data is None:
                logger.warning(f"Failed to fetch ratings snapshot for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            # Handle both list and single object formats
            if isinstance(api_data, list):
                if not api_data:  # Empty list
                    logger.warning(f"No ratings snapshot returned for {symbol}. Skipping symbol.")
                    continue
                # If list, use the first item
                api_data = api_data[0]
                logger.info(f"Received a list for ratings snapshot for {symbol}, using first item.")

            # --- Parse Data ---
            parsed = parsing.parse_analyst_rating(api_data, source='FMP Rating Snapshot')
            if parsed:
                all_parsed_ratings.append(parsed)
            else:
                logger.warning(f"Failed to parse ratings snapshot for {symbol} from data: {api_data}")
                # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing ratings snapshot for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_ratings:
        logger.warning(f"No valid ratings snapshot records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_ratings)} ratings snapshot records...")
        # Deduplicate before upsert
        unique_map: Dict[tuple, Dict[str, Any]] = {}
        for rec in all_parsed_ratings:
            key = (rec.get("symbol"), rec.get("date"), rec.get("source"), rec.get("rating_analyst_firm"))
            unique_map[key] = rec
        deduped = list(unique_map.values())
        success = db_client.update_analyst_ratings(deduped)

        if success:
            logger.info(f"Successfully upserted {len(deduped)} ratings snapshot records.")
        else:
            logger.error(f"Failed to upsert ratings snapshot records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished ratings snapshot fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")


def fetch_and_store_price_target_consensus(symbols: List[str]):
    """Fetches price target consensuses for the given symbols,
    parses them, and upserts into the 'analyst_ratings' database table.

    Args:
        symbols: A list of stock symbols.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_price_target_consensus. Skipping.")
        return

    logger.info(f"Starting price target consensus fetch for {len(symbols)} symbols.")

    all_parsed_ratings = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching price target consensus for symbol: {symbol}")
        endpoint_path = "/stable/price-target-consensus"
        params = {'symbol': symbol}

        try:
            # --- Fetch Data ---
            api_data = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
            # DEBUG: log raw API payload for consensus
            logger.debug("RAW consensus API data for %s: %s", symbol, api_data)

            if api_data is None:
                logger.warning(f"Failed to fetch price target consensus for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            # Handle both list and single object formats
            if isinstance(api_data, list):
                if not api_data:  # Empty list
                    logger.warning(f"No price target consensus returned for {symbol}. Skipping symbol.")
                    continue
                # If list, use the first item
                api_data = api_data[0]
                logger.info(f"Received a list for price target consensus for {symbol}, using first item.")

            # --- Parse Data ---
            parsed = parsing.parse_analyst_rating(api_data, source='FMP Price Target Consensus')
            if parsed:
                all_parsed_ratings.append(parsed)
            else:
                logger.warning(f"Failed to parse price target consensus for {symbol} from data: {api_data}")
                # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing price target consensus for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_ratings:
        logger.warning(f"No valid price target consensus records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_ratings)} price target consensus records...")
        # Deduplicate before upsert
        unique_map: Dict[tuple, Dict[str, Any]] = {}
        for rec in all_parsed_ratings:
            key = (rec.get("symbol"), rec.get("date"), rec.get("source"), rec.get("rating_analyst_firm"))
            unique_map[key] = rec
        deduped = list(unique_map.values())
        success = db_client.update_analyst_ratings(deduped)

        if success:
            logger.info(f"Successfully upserted {len(deduped)} price target consensus records.")
        else:
            logger.error(f"Failed to upsert price target consensus records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished price target consensus fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")


def fetch_and_store_historical_grades(symbols: List[str], limit: int = 100):
    """Fetches historical grades for the given symbols,
    parses them, and upserts into the 'analyst_ratings' database table.

    Args:
        symbols: A list of stock symbols.
        limit: The maximum number of historical grades to fetch per symbol.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_historical_grades. Skipping.")
        return

    logger.info(f"Starting historical grades fetch for {len(symbols)} symbols. Limit per symbol: {limit}.")

    all_parsed_ratings = []
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching historical grades for symbol: {symbol}, Limit: {limit}")
        endpoint_path = "/stable/grades-historical"
        params = {'symbol': symbol, 'limit': limit}

        try:
            # --- Fetch Data ---
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

            if api_data_list is None:
                logger.warning(f"Failed to fetch historical grades for {symbol}. Skipping symbol.")
                has_errors = True
                continue # Skip to next symbol

            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list for historical grades for {symbol}, got {type(api_data_list)}. Skipping symbol.")
                has_errors = True
                continue

            logger.info(f"Received {len(api_data_list)} historical grade records for {symbol}. Parsing...")

            # --- Parse Data ---            
            for grade_data in api_data_list:
                parsed = parsing.parse_analyst_rating(grade_data, source='FMP Grade Historical')
                if parsed:
                    all_parsed_ratings.append(parsed)
                else:
                    logger.warning(f"Failed to parse historical grade for {symbol} from data: {grade_data}")
                    # Don't set has_errors for parsing failure

        except Exception as e:
            logger.exception(f"Error fetching/parsing historical grades for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_parsed_ratings:
        logger.warning(f"No valid historical grade records could be parsed for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_ratings)} historical grade records...")
        # Deduplicate before upsert
        unique_map: Dict[tuple, Dict[str, Any]] = {}
        for rec in all_parsed_ratings:
            key = (rec.get("symbol"), rec.get("date"), rec.get("source"), rec.get("rating_analyst_firm"))
            unique_map[key] = rec
        deduped = list(unique_map.values())
        success = db_client.update_analyst_ratings(deduped)

        if success:
            logger.info(f"Successfully upserted {len(deduped)} historical grade records.")
        else:
            logger.error(f"Failed to upsert historical grade records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished historical grades fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")


def fetch_and_store_financial_estimates(symbols: List[str], period: str = 'annual', page: int = 0, limit: int = 10):
    """Fetches analyst financial estimates for the given symbols,
    parses them, and upserts into the 'financial_estimates' database table.

    Args:
        symbols: A list of stock symbols.
        period: 'annual' or 'quarter'.
        page: Pagination page index.
        limit: Number of records per symbol.
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_financial_estimates. Skipping.")
        return

    logger.info(f"Starting financial estimates fetch for {len(symbols)} symbols (period={period}).")
    all_records: List[Dict[str, Any]] = []
    symbol_counts: Dict[str,int] = {}
    has_errors = False

    for symbol in symbols:
        logger.debug(f"Fetching financial estimates for symbol: {symbol}, period={period}, page={page}, limit={limit}")
        endpoint = "/stable/analyst-estimates"
        params = {'symbol': symbol, 'period': period, 'page': page, 'limit': limit}
        parsed_count = 0
        try:
            data = fmp_client.make_fmp_request(endpoint_path=endpoint, params=params)
            if data is None:
                logger.warning(f"No financial estimates data returned for {symbol}. Skipping.")
                has_errors = True
                continue
            if not isinstance(data, list):
                logger.warning(f"Expected list for financial estimates for {symbol}, got {type(data)}. Skipping.")
                has_errors = True
                continue
            logger.info(f"Received {len(data)} financial estimates records for {symbol}. Parsing...")
            for item in data:
                parsed = parsing.parse_financial_estimate(item)
                if parsed:
                    all_records.append(parsed)
                    parsed_count += 1
            symbol_counts[symbol] = parsed_count
            if parsed_count:
                logger.info(f"Parsed {parsed_count} financial estimates for {symbol}.")
            else:
                logger.warning(f"No financial estimates parsed for {symbol}.")
        except Exception as e:
            logger.exception(f"Error fetching/parsing financial estimates for {symbol}: {e}")
            has_errors = True

    # Upsert
    if not all_records:
        logger.warning("No valid financial estimate records parsed; nothing to upsert.")
    else:
        # Ensure stocks exist: seed missing symbols before upsert
        client = get_supabase_client()
        resp = client.table('stocks').select('symbol').execute()
        existing = {row['symbol'] for row in resp.data or []}
        # Seed any missing stock profiles
        missing = {r['symbol'] for r in all_records} - existing
        if missing:
            logger.info(f"Seeding stock profiles for missing symbols: {missing}")
            fetch_and_store_profiles(list(missing))
            # refresh existing symbols
            resp = client.table('stocks').select('symbol').execute()
            existing = {row['symbol'] for row in resp.data or []}
        # Filter records to symbols present in stocks table
        valid_records = [r for r in all_records if r['symbol'] in existing]
        skipped = len(all_records) - len(valid_records)
        if skipped:
            logger.warning(f"Skipping {skipped} estimate records still missing in stocks table.")
        logger.info(f"Attempting to upsert {len(valid_records)} financial estimates records.")
        success = False
        if valid_records:
            success = db_client.update_financial_estimates(valid_records)
        if success:
            logger.info(f"Successfully upserted {len(valid_records)} financial estimate records.")
        else:
            logger.error("Failed to upsert financial estimate records.")
    # Summary of per-symbol parsing
    logger.info(f"Financial estimates parsing summary: {symbol_counts}")

    logger.log(logging.WARNING if has_errors else logging.INFO,
               f"Finished financial estimates fetch. Errors: {has_errors}")


# CLI entrypoint to run all analyst tasks
if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description='Run FMP analyst tasks')
    parser.add_argument('--symbols', nargs='+', required=True, help='List of stock symbols')
    parser.add_argument('--period', choices=['annual', 'quarter'], default='annual', help='Estimate period')
    parser.add_argument('--page', type=int, default=0, help='Pagination page for estimates')
    parser.add_argument('--limit', type=int, default=10, help='Limit per symbol for news/grades/estimates')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug(f"DEBUG mode enabled. Symbols: {args.symbols}, period: {args.period}, page: {args.page}, limit: {args.limit}")

    # Sequentially fetch and store all data types
    fetch_and_store_price_target_news(args.symbols, limit=args.limit)
    fetch_and_store_grade_news(args.symbols, limit=args.limit)
    fetch_and_store_current_grades(args.symbols, limit=args.limit)
    fetch_and_store_ratings_snapshot(args.symbols)
    fetch_and_store_price_target_consensus(args.symbols)
    fetch_and_store_historical_grades(args.symbols, limit=args.limit)
    fetch_and_store_financial_estimates(args.symbols, period=args.period, page=args.page, limit=args.limit)
