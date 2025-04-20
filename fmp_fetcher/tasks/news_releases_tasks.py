# fmp_fetcher/tasks/news_releases_tasks.py
import logging
import time
import datetime
from typing import List, Dict, Any, Optional

from ..clients import fmp_client, db_client
from ..utils import parsing

logger = logging.getLogger(__name__)


def fetch_and_store_press_releases(symbols: List[str], limit: int = 30) -> bool:
    """Fetches the latest press releases for the given symbols,
    parses them, and upserts into the 'press_releases' database table.

    Args:
        symbols: List of stock symbols to fetch press releases for
        limit: The maximum number of recent press releases to fetch per request
        
    Returns:
        True if the operation was successful, False otherwise
    """
    if not symbols:
        logger.warning("No symbols provided for press releases. Skipping.")
        return False
        
    logger.info(f"Starting press releases fetch for {len(symbols)} symbols. Limit: {limit} per request.")

    all_parsed_releases = []
    has_errors = False
    attempted_endpoints = []
    
    # Process in chunks to avoid URL length limits and rate limiting
    chunk_size = 10  # Max 10 symbols per request
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i:i+chunk_size]
        symbols_str = ','.join(chunk)
        logger.info(f"Processing press releases for symbols chunk: {symbols_str}")
        
        # Use the documented endpoint for press releases
        try:
            # First try the documented endpoint with symbols parameter
            endpoint_path = "/news/press-releases"
            params = {
                'symbols': symbols_str,
                'limit': limit
            }
            
            logger.info(f"Fetching press releases from {endpoint_path} with symbols: {symbols_str}")
            attempted_endpoints.append(f"{endpoint_path}?symbols={symbols_str}")
            
            api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
            
            if not api_data_list:
                logger.warning(f"No press releases found for symbols: {symbols_str}")
                continue
                
            if not isinstance(api_data_list, list):
                logger.warning(f"Expected a list of press releases, got {type(api_data_list)}")
                continue
                
            if len(api_data_list) == 0:
                logger.warning(f"Empty list of press releases for symbols: {symbols_str}")
                continue
                
            logger.info(f"Received {len(api_data_list)} press releases for symbols chunk: {symbols_str}")
            
            # Log a sample to understand structure
            if api_data_list and len(api_data_list) > 0:
                sample = api_data_list[0]
                logger.info(f"Sample press release fields: {list(sample.keys())}")
                logger.info(f"Sample press release data: {str(sample)[:300]}...")
            
            # Parse press releases with mapping to our DB schema
            for release_data in api_data_list:
                try:
                    # Validate that we have required fields
                    symbol = release_data.get('symbol')
                    if not symbol:
                        logger.warning(f"Skipping press release with missing symbol")
                        continue
                    
                    # Map response fields to our database columns
                    parsed_release = {
                        'symbol': symbol,
                        'published_date': release_data.get('publishedDate'),
                        'title': release_data.get('title'),
                        'text': release_data.get('text'),
                        'source_url': release_data.get('url')  # This is the key field name in the API response
                    }
                    
                    # Validate required fields
                    if not parsed_release['source_url']:
                        logger.warning(f"Skipping press release with missing source_url: {parsed_release.get('title')}")
                        continue
                        
                    if not parsed_release['published_date']:
                        logger.warning(f"Skipping press release with missing published_date: {parsed_release.get('title')}")
                        continue
                        
                    if not parsed_release['title']:
                        logger.warning(f"Skipping press release with missing title for {symbol}")
                        continue
                    
                    # Add to list for database insertion
                    all_parsed_releases.append(parsed_release)
                    
                except Exception as e:
                    logger.warning(f"Error parsing press release: {e}")
                    has_errors = True
                    
        except Exception as e:
            logger.error(f"Error fetching press releases for symbols {symbols_str}: {e}")
            has_errors = True
    
    # Check if we successfully parsed any releases
    if not all_parsed_releases:
        logger.error(f"No valid press release records could be parsed!")
        logger.error(f"Attempted endpoints: {', '.join(attempted_endpoints)}")
        return False
    
    # Insert into database 
    logger.info(f"Preparing to upsert {len(all_parsed_releases)} press releases to database")
    
    try:
        # Filter to expected database columns
        valid_columns = ['symbol', 'published_date', 'title', 'text', 'source_url']
        filtered_data = []
        for record in all_parsed_releases:
            # Skip records missing required fields (source_url is NOT NULL in the DB)
            if not record.get('source_url'):
                logger.warning(f"Skipping press release record missing source_url")
                continue
                
            # Only keep the columns that exist in the DB table
            filtered_record = {k: v for k, v in record.items() if k in valid_columns}
            filtered_data.append(filtered_record)
            
        if not filtered_data:
            logger.error("No valid press release records after filtering")
            return False
            
        # Insert into database
        success = db_client.update_press_releases(filtered_data)
        if success:
            logger.info(f"Successfully upserted {len(filtered_data)} press releases")
            return True
        else:
            logger.error("Failed to upsert press releases")
            return False
    except Exception as e:
        logger.exception(f"Error upserting press releases: {e}")
        return False


def fetch_and_store_stock_news(symbols: List[str], limit: int = 50, chunk_size: int = 10) -> bool:
    """Fetches recent stock news for the given symbols,
    parses them, and upserts into the 'stock_news' database table.
    
    Symbols are processed in chunks to avoid URL length limits.

    Args:
        symbols: A list of stock symbols.
        limit: The maximum number of news items to fetch per chunk.
        chunk_size: Number of symbols to include in each request.
        
    Returns:
        True if operation was successful (even partially), False otherwise
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_stock_news. Skipping.")
        return False

    logger.info(f"Starting stock news fetch for {len(symbols)} symbols.")

    all_parsed_news = []
    has_errors = False
    attempted_endpoints = []
    
    # Process symbols in smaller chunks to avoid URI Too Long errors and rate limiting
    for i in range(0, len(symbols), chunk_size):
        symbols_chunk = symbols[i:i+chunk_size]
        symbols_str = ','.join(symbols_chunk)
        
        logger.info(f"Fetching stock news for symbols chunk: {symbols_str}, Limit: {limit}")
        
        # Try multiple endpoints to find news data
        endpoints_to_try = [
            {"path": "/news/stock", "param_name": "symbols"},
            {"path": "/stock-news", "param_name": "tickers"},  
            {"path": "/api/v3/stock_news", "param_name": "tickers"},
            {"path": "/api/v4/stock_news", "param_name": "symbol"}
        ]
        
        chunk_success = False
        
        for endpoint_info in endpoints_to_try:
            try:
                # --- Fetch Data ---
                endpoint_path = endpoint_info["path"]
                param_name = endpoint_info["param_name"]
                params = {param_name: symbols_str, 'limit': limit}
                
                logger.info(f"Trying news endpoint: {endpoint_path} with {param_name} parameter")
                attempted_endpoints.append(f"{endpoint_path} with {param_name}")
                
                api_data_list = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)

                if api_data_list is None:
                    logger.warning(f"No data returned from {endpoint_path}. Trying next endpoint...")
                    continue

                if not isinstance(api_data_list, list):
                    logger.warning(f"Expected a list from {endpoint_path}, got {type(api_data_list)}. Trying next endpoint...")
                    continue

                if len(api_data_list) == 0:
                    logger.warning(f"Empty list returned from {endpoint_path}. Trying next endpoint...")
                    continue

                logger.info(f"Received {len(api_data_list)} stock news items from {endpoint_path}. Parsing...")

                # --- Parse Data ---
                # Parse each item individually to handle errors per item
                chunk_parsed_news = []
                for news_item in api_data_list:
                    try:
                        # Make sure the news item has required fields
                        if not news_item or not isinstance(news_item, dict):
                            continue
                            
                        # Handle different API response formats
                        if "symbol" not in news_item and "ticker" in news_item:
                            news_item["symbol"] = news_item["ticker"]
                            
                        if "publishedDate" not in news_item and "published_date" in news_item:
                            news_item["publishedDate"] = news_item["published_date"]
                        
                        parsed = parsing.parse_stock_news(news_item)
                        if parsed:
                            # Log first few records for debugging
                            if len(chunk_parsed_news) < 2:
                                logger.info(f"Parsed news record: {parsed}")
                            chunk_parsed_news.append(parsed)
                    except Exception as e:
                        logger.warning(f"Error parsing individual news item: {e}")
                        # Continue with the next item

                logger.info(f"Successfully parsed {len(chunk_parsed_news)} news items from this chunk")
                if chunk_parsed_news:
                    all_parsed_news.extend(chunk_parsed_news)
                    chunk_success = True
                    break  # We found a working endpoint with data!
                
            except Exception as e:
                logger.exception(f"Error with endpoint {endpoint_path}: {e}")
                continue
        
        if not chunk_success:
            logger.error(f"All endpoints failed for symbols chunk: {symbols_str}")
            has_errors = True

    # --- Store Data ---    
    if not all_parsed_news:
        logger.error("No valid stock news records could be parsed. No news is NOT a valid state!")
        logger.error(f"Attempted endpoints: {', '.join(attempted_endpoints)}")
        return False 
    else:
        logger.info(f"Attempting to upsert a total of {len(all_parsed_news)} stock news records...")
        
        try:
            from ..config import get_supabase_client
            supabase = get_supabase_client()
            
            # Make sure we're only supplying columns that are actually in the table
            # Based on the SQL schema we know the table has these columns:
            valid_columns = [
                'symbol', 'published_date', 'title', 'image_url', 'site', 'text', 'source_url'
            ]
            
            # Filter each record to only include valid columns
            filtered_data = []
            for record in all_parsed_news:
                filtered_record = {k: v for k, v in record.items() if k in valid_columns}
                filtered_data.append(filtered_record)
            
            # Log what we're about to insert
            logger.info(f"Upserting news with columns: {valid_columns}")
                
            # Perform the upsert properly with conflict handling
            response = supabase.table('stock_news').upsert(
                filtered_data,
                on_conflict="source_url",  # Handle conflicts on source_url column
                ignore_duplicates=False    # Update existing records with new data
            ).execute()
            
            logger.info(f"Successfully upserted {len(filtered_data)} stock news records.")
            return True
        except Exception as e:
            logger.exception(f"Error during stock news upsert: {e}")
            return False

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished stock news fetch for {len(symbols)} requested symbols. Encountered fetch errors: {has_errors}")
    
    # Only return true if we actually found and parsed some news
    return len(all_parsed_news) > 0
