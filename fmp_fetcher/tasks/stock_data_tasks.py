import logging
from typing import List, Optional
from datetime import date # Added for date handling

from ..clients import fmp_client, db_client
from ..utils import parsing
from ..config import TARGET_SYMBOLS # Or get symbols dynamically later

logger = logging.getLogger(__name__)


def fetch_and_store_profiles(symbols: List[str]) -> Optional[bool]:
    """
    Fetches company profiles for the provided symbols and stores them in the database.
    Uses batch profile endpoint for efficiency.
    """
    if not symbols:
        logger.warning("Empty symbols list provided to fetch_and_store_profiles.")
        return False
    logger.info(f"Fetching profiles for symbols: {symbols}")
    try:
        # Use API v3 batch profile endpoint
        symbols_str = ",".join(symbols)
        endpoint = f"/api/v3/profile/{symbols_str}"
        api_data = fmp_client.make_fmp_request(endpoint_path=endpoint)
        if not api_data or not isinstance(api_data, list):
            logger.error(f"Profile fetch failed or returned unexpected format: {api_data}")
            return False
        # Parse profiles
        parsed = []
        for item in api_data:
            try:
                parsed_profile = parsing.parse_stock_profile(item)
                if parsed_profile:
                    parsed.append(parsed_profile)
            except Exception as err:
                logger.error(f"Error parsing profile for {item.get('symbol')}: {err}")
        if not parsed:
            logger.warning("No valid profiles parsed for symbols.")
            return False
        # Upsert profiles
        success = db_client.update_stocks(parsed)
        if success:
            logger.info(f"Upserted {len(parsed)} stock profiles.")
            return True
        else:
            logger.error("Failed to upsert stock profiles.")
            return False
    except Exception as e:
        logger.exception(f"Error in fetch_and_store_profiles: {e}")
        return None


def fetch_and_store_daily_prices(symbols: List[str], fetch_date: str) -> Optional[bool]:
    """Fetches End-of-Day (EOD) stock prices for the given symbols and date
    using the FMP bulk EOD API and upserts them into the 'stock_prices_daily' table.

    Args:
        symbols: A list of stock symbols to fetch prices for.
        fetch_date: The date to fetch EOD data for, in 'YYYY-MM-DD' format.
        
    Returns:
        True if successful, False if partial failure, None if critical error
    """
    if not symbols:
        logger.warning("No symbols provided to fetch_and_store_daily_prices. Skipping.")
        return False
    
    # Validate date format (basic check)
    try:
        fetch_date_obj = date.fromisoformat(fetch_date)
    except ValueError:
        logger.error(f"Invalid date format '{fetch_date}'. Please use YYYY-MM-DD. Skipping EOD fetch.")
        return False

    logger.info(f"Starting EOD price fetch for {len(symbols)} symbols for date {fetch_date}.")

    try:
        # Try multiple endpoint formats that FMP supports for historical price data
        endpoints_to_try = [
            # Format 1: Bulk EOD endpoint
            {"path": "/eod-bulk", "params": {"date": fetch_date}},
            # Format 2: API v3 bulk endpoint
            {"path": "/api/v3/eod-bulk", "params": {"date": fetch_date}},
            # Format 3: Historical batch
            {"path": "/api/v3/historical-price-full/batch", "params": {"from": fetch_date, "to": fetch_date}}
        ]
        
        # Try each endpoint until we get successful results
        api_data = None
        used_endpoint = None
        
        for endpoint_info in endpoints_to_try:
            logger.info(f"Trying price endpoint: {endpoint_info['path']}")
            
            try:
                endpoint_data = fmp_client.make_fmp_request(
                    endpoint_path=endpoint_info["path"],
                    params=endpoint_info["params"],
                    handle_csv=True  # Enable CSV handling
                )
                
                if endpoint_data is not None:
                    api_data = endpoint_data
                    used_endpoint = endpoint_info["path"]
                    logger.info(f"Successfully fetched prices using endpoint: {used_endpoint}")
                    break
            except Exception as e:
                logger.warning(f"Failed with endpoint {endpoint_info['path']}: {e}")
                continue
        
        # If all endpoints failed, try the individual symbol approach
        if api_data is None:
            logger.warning("All bulk endpoints failed. Falling back to individual symbol fetches...")
            return fetch_historical_prices_by_symbol(symbols, fetch_date)
            
        # Process the API data based on its format
        if isinstance(api_data, list):
            # Standard bulk EOD format - list of price objects
            logger.info(f"Received {len(api_data)} EOD records from bulk API for {fetch_date}. Parsing target symbols...")
            parsed_data = parsing.parse_bulk_daily_prices(api_data, symbols, date_override=fetch_date)
        elif isinstance(api_data, dict) and "historicalStockList" in api_data:
            # Batch historical format - nested structure
            historical_list = api_data.get("historicalStockList", [])
            logger.info(f"Received historical batch data with {len(historical_list)} stocks. Parsing target symbols...")
            
            # Extract data for our target date
            all_prices = []
            for stock_data in historical_list:
                symbol = stock_data.get("symbol")
                if not symbol or symbol not in symbols:
                    continue
                
                for price_data in stock_data.get("historical", []):
                    if price_data.get("date") == fetch_date:
                        price_data["symbol"] = symbol  # Add symbol to price data
                        all_prices.append(price_data)
            
            # Parse the extracted prices
            parsed_data = []
            for price_item in all_prices:
                parsed_price = parsing.parse_daily_price(price_item)
                if parsed_price:
                    parsed_data.append(parsed_price)
        else:
            logger.error(f"Unexpected data format from price endpoint {used_endpoint}: {type(api_data)}")
            return False

        if not parsed_data:
            logger.warning(f"No valid EOD price data could be parsed for the target symbols on {fetch_date}")
            # Last resort - try individual symbol fetching
            return fetch_historical_prices_by_symbol(symbols, fetch_date)

        logger.info(f"Successfully parsed {len(parsed_data)} EOD price records for target symbols.")

        # Store the data
        success = db_client.update_daily_prices(parsed_data)

        if success:
            logger.info(f"Successfully upserted {len(parsed_data)} EOD price records into the database for {fetch_date}.")
            return True
        else:
            logger.error(f"Failed to upsert EOD price records into the database for {fetch_date}.")
            return False

    except Exception as e:
        logger.error(f"Critical error in fetch_and_store_daily_prices: {e}", exc_info=True)
        return None

def fetch_historical_prices_by_symbol(symbols: List[str], fetch_date: str) -> bool:
    """Fallback method to fetch historical prices for each individual symbol.
    
    Args:
        symbols: List of stock symbols to fetch
        fetch_date: Date to fetch prices for in YYYY-MM-DD format
        
    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Attempting to fetch historical prices individually for {len(symbols)} symbols on {fetch_date}")
    
    all_prices = []
    
    # Process symbols in smaller chunks to avoid rate limiting
    for i in range(0, len(symbols), 5):
        symbols_chunk = symbols[i:i+5]
        chunk_str = ",".join(symbols_chunk)
        logger.info(f"Fetching historical daily prices for symbols chunk: {chunk_str}")
        
        # Try different endpoint formats
        endpoints_to_try = [
            # Format 1: Historical price endpoint with multiple symbols
            {"path": f"/historical-price-full/{chunk_str}", "params": {"from": fetch_date, "to": fetch_date}},
            # Format 2: API v3 endpoint
            {"path": f"/api/v3/historical-price-full/{chunk_str}", "params": {"from": fetch_date, "to": fetch_date}}
        ]
        
        chunk_data = None
        for endpoint_info in endpoints_to_try:
            try:
                endpoint_data = fmp_client.make_fmp_request(
                    endpoint_path=endpoint_info["path"],
                    params=endpoint_info["params"]
                )
                
                if endpoint_data is not None:
                    chunk_data = endpoint_data
                    logger.info(f"Successfully fetched historical prices using endpoint: {endpoint_info['path']}")
                    break
            except Exception as e:
                logger.warning(f"Failed with endpoint {endpoint_info['path']}: {e}")
                continue
        
        if not chunk_data or not isinstance(chunk_data, dict):
            logger.warning(f"Failed to fetch historical prices for chunk: {chunk_str}")
            continue
        
        # Process the response based on its structure
        if "historicalStockList" in chunk_data:
            # Multiple symbols format
            for stock_data in chunk_data.get("historicalStockList", []):
                symbol = stock_data.get("symbol")
                if not symbol:
                    continue
                
                # Extract the target date from historical data
                historical_data = stock_data.get("historical", [])
                for price_data in historical_data:
                    if price_data.get("date") == fetch_date:
                        # Add symbol to the price data
                        price_data["symbol"] = symbol
                        all_prices.append(price_data)
                        break
        elif "historical" in chunk_data and "symbol" in chunk_data:
            # Single symbol format
            symbol = chunk_data.get("symbol")
            historical_data = chunk_data.get("historical", [])
            
            for price_data in historical_data:
                if price_data.get("date") == fetch_date:
                    # Add symbol to the price data
                    price_data["symbol"] = symbol
                    all_prices.append(price_data)
                    break
    
    if not all_prices:
        logger.error(f"Failed to retrieve any price data for date {fetch_date}.")
        return False
    
    # Parse the data
    parsed_data = []
    for price_item in all_prices:
        try:
            parsed_price = parsing.parse_daily_price(price_item)
            if parsed_price:
                parsed_data.append(parsed_price)
        except Exception as e:
            logger.warning(f"Error parsing price for {price_item.get('symbol')}: {e}")
    
    if not parsed_data:
        logger.warning(f"No valid price data could be parsed for {fetch_date}")
        return False
    
    # Store the data
    success = db_client.update_daily_prices(parsed_data)
    
    if success:
        logger.info(f"Successfully upserted {len(parsed_data)} individual price records for {fetch_date}")
        return True
    else:
        logger.error(f"Failed to upsert individual price records for {fetch_date}")
        return False


# Example Usage (usually called from main.py scheduler):
# if __name__ == '__main__':
#     from ..utils.logging_config import setup_logging
#     setup_logging()
#     fetch_and_store_profiles(TARGET_SYMBOLS)

# Example Usage (called from main.py):
# from datetime import date, timedelta
# today_str = date.today().isoformat()
# yesterday_str = (date.today() - timedelta(days=1)).isoformat()
# fetch_and_store_daily_prices(TARGET_SYMBOLS, yesterday_str) # Fetch yesterday's data
