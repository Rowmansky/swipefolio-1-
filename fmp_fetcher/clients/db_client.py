import logging
import json
from typing import List, Dict, Any, Optional
from decimal import Decimal
from postgrest.exceptions import APIError

from ..config import get_supabase_client

logger = logging.getLogger(__name__) # Use module-specific logger

# Custom JSON encoder to handle Decimal types
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float for JSON serialization
        return super(DecimalEncoder, self).default(obj)

def convert_decimals_in_dict(data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively converts all Decimal values in a dictionary to float.
    This ensures the dictionary can be JSON serialized for Supabase.
    
    Args:
        data_dict: Dictionary potentially containing Decimal values
        
    Returns:
        Dictionary with all Decimal values converted to float
    """
    result = {}
    for key, value in data_dict.items():
        if isinstance(value, Decimal):
            result[key] = float(value)
        elif isinstance(value, dict):
            result[key] = convert_decimals_in_dict(value)
        elif isinstance(value, list):
            result[key] = [
                convert_decimals_in_dict(item) if isinstance(item, dict) else 
                float(item) if isinstance(item, Decimal) else item 
                for item in value
            ]
        else:
            result[key] = value
    return result

# fmp_fetcher/clients/db_client.py

def upsert_data(table_name: str, data: List[Dict[str, Any]]) -> bool:

    # Convert Decimal objects to floats for JSON serialization
    processed_data = [convert_decimals_in_dict(item) for item in data]
    logger.debug(f"Upsert payload for table '{table_name}': %s", processed_data)
    supabase = get_supabase_client()
    try:
        # Custom conflict handling per table
        if table_name == 'stock_prices_daily':
            response = supabase.table(table_name).upsert(
                processed_data,
                on_conflict="symbol,date",
                ignore_duplicates=False
            ).execute()

        elif table_name == 'press_releases':
            response = supabase.table(table_name).upsert(
                processed_data,
                on_conflict="source_url",
                ignore_duplicates=False
            ).execute()

        elif table_name == 'dcf_valuations':
            # NEW: handle conflicts on symbol+date+dcf_type
            response = supabase.table(table_name).upsert(
                processed_data,
                on_conflict="symbol,date,dcf_type",
                ignore_duplicates=False
            ).execute()

        elif table_name == 'financial_statements':
            # Use on_conflict to allow insert or update without 409 errors
            logger.info(
                "Performing upsert on financial_statements with conflict keys: symbol,report_date,period,statement_type"
            )
            response = supabase.table(table_name).upsert(
                processed_data,
                on_conflict="symbol,report_date,period,statement_type",
                ignore_duplicates=False
            ).execute()

        elif table_name == 'analyst_ratings':
            # Skip duplicate rows in batch to avoid conflict errors
            response = supabase.table(table_name).upsert(
                processed_data,
                on_conflict="symbol,date,source,rating_analyst_firm",
                ignore_duplicates=True
            ).execute()

        elif table_name == 'political_disclosures':
            # Use ptr_link unique key for political disclosures
            logger.debug("Political upsert payload: %s", processed_data)
            response = supabase.table(table_name).upsert(
                processed_data,
                on_conflict="ptr_link",
                ignore_duplicates=False
            ).execute()
            logger.debug("Political upsert response: %s", response)

        else:
            # For other tables, use standard upsert behavior
            response = supabase.table(table_name).upsert(processed_data).execute()

        logger.debug(f"Supabase upsert response for '{table_name}': %s", response)
        # Log success count
        logger.info(f"Successfully upserted {len(data)} record(s) into '{table_name}'.")
        return True

    except APIError as e:
        # Special handling for duplicate key violations - treat as success
        if "duplicate key value violates unique constraint" in str(e):
            logger.info(f"Data already exists in {table_name}. Treating as success.")
            return True
        
        logger.exception(f"Supabase APIError during upsert to '{table_name}': {e.message} (Code: {e.code}, Details: {e.details}, Hint: {e.hint})")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during upsert to '{table_name}': {e}")
        return False

# ==================================================
# Specific Table Upsert Functions (v3.1 Schema)
# ==================================================
# These functions act as wrappers around upsert_data, providing a clear API
# for the data fetching tasks. They will be called with data parsed/mapped
# from the FMP API responses.

def update_stocks(data: List[Dict[str, Any]]) -> bool:
    """Upserts stock profile data into the 'stocks' table."""
    return upsert_data('stocks', data)

def update_daily_prices(data: List[Dict[str, Any]]) -> bool:
    """Upserts daily stock price data into the 'stock_prices_daily' table."""
    return upsert_data('stock_prices_daily', data)

def update_financial_statements(data: List[Dict[str, Any]]) -> bool:
    """Upserts financial statement JSON data into the 'financial_statements' table."""
    return upsert_data('financial_statements', data)

def update_key_metrics_ttm(data: List[Dict[str, Any]]) -> bool:
    """Upserts TTM key metrics data into the 'key_metrics_ttm' table."""
    # Note: TTM data is usually one record per symbol, ensure input 'data' reflects this.
    return upsert_data('key_metrics_ttm', data)

def update_calculated_metrics(data: List[Dict[str, Any]]) -> bool:
    """Upserts calculated metrics data into the 'calculated_metrics' table."""
    return upsert_data('calculated_metrics', data)

def update_analyst_ratings(data: List[Dict[str, Any]]) -> bool:
    """Upserts analyst ratings data into the 'analyst_ratings' table."""
    return upsert_data('analyst_ratings', data)

def update_stock_news(data: List[Dict[str, Any]]) -> bool:
    """Upserts stock news data into the 'stock_news' table."""
    return upsert_data('stock_news', data)

def update_esg_scores_historical(data: List[Dict[str, Any]]) -> bool:
    """Upserts historical ESG scores into the 'esg_scores_historical' table."""
    return upsert_data('esg_scores_historical', data)

def update_dividends(data: List[Dict[str, Any]]) -> bool:
    """Upserts historical dividend data into the 'dividends' table."""
    return upsert_data('dividends', data)

def update_financial_estimates(data: List[Dict[str, Any]]) -> bool:
    """Upserts financial estimate data into the 'financial_estimates' table."""
    return upsert_data('financial_estimates', data)

def update_earnings_reports(data: List[Dict[str, Any]]) -> bool:
    """Upserts earnings report data into the 'earnings_reports' table."""
    return upsert_data('earnings_reports', data)

def update_press_releases(data: List[Dict[str, Any]]) -> bool:
    """Upserts press release data into the 'press_releases' table.
    
    This is a specialized function that handles press releases with proper
    conflict resolution on the source_url column.
    """
    if not data:
        logger.info("No press release data provided. Skipping.")
        return True
    
    # Log how many press releases we're processing
    logger.info(f"Processing {len(data)} press releases for database update")
    
    # Process data to ensure all Decimal values are converted to float
    processed_data = [convert_decimals_in_dict(item) for item in data]
    
    # Log exactly what we're trying to insert for debugging purposes
    for i, record in enumerate(processed_data[:3]):  # Log first 3 records at most
        logger.info(f"Press release record {i} keys: {list(record.keys())}")
        if 'source_url' in record:
            logger.info(f"Press release {i} has source_url: {record['source_url']}")
        else:
            logger.warning(f"Press release {i} is missing source_url field!")
        
    supabase = get_supabase_client()
    try:
        # Use proper upsert with source_url as the conflict resolution field
        response = supabase.table('press_releases').upsert(
            processed_data,
            on_conflict="source_url",  # Handle conflicts on source_url column
            ignore_duplicates=False    # Update existing records with new data
        ).execute()
        
        # Log success
        logger.info(f"Successfully upserted {len(data)} press release record(s).")
        return True
        
    except APIError as e:
        # Special handling for duplicate key violations - treat as success
        if "duplicate key value violates unique constraint" in str(e):
            logger.info("Press release data already exists. Treating as success.")
            return True
            
        logger.exception(f"Supabase APIError during press release upsert: {e.message if hasattr(e, 'message') else str(e)}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during press release upsert: {e}")
        return False

def update_political_disclosures(data: List[Dict[str, Any]]) -> bool:
    """Upserts political disclosures into the 'political_disclosures' table."""
    # Convert and insert directly to avoid Upsert conflicts
    processed_data = [convert_decimals_in_dict(item) for item in data]
    logger.debug("Political upsert payload: %s", processed_data)
    supabase = get_supabase_client()
    try:
        # Use upsert to insert new and skip existing based on ptr_link
        response = supabase.table('political_disclosures').upsert(
            processed_data,
            on_conflict="ptr_link",
            ignore_duplicates=True
        ).execute()
        logger.debug("Political upsert response: %s", response)
        logger.info(f"Upserted {len(data)} political disclosure records.")
        return True
    except APIError as e:
        logger.exception(f"Supabase APIError during upsert to 'political_disclosures': {e}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error during upsert to 'political_disclosures': {e}")
        return False

def update_financial_statement_growth(data: List[Dict[str, Any]]) -> bool:
    """Upserts financial statement growth data into the 'financial_statement_growth' table."""
    return upsert_data('financial_statement_growth', data)

def update_key_metrics_historical(data: List[Dict[str, Any]]) -> bool:
    """Upserts historical key metrics data into the 'key_metrics_historical' table."""
    return upsert_data('key_metrics_historical', data)

def update_financial_ratios_historical(data: List[Dict[str, Any]]) -> bool:
    """Upserts historical financial ratios data into the 'financial_ratios_historical' table."""
    return upsert_data('financial_ratios_historical', data)

def update_fmp_financial_scores_historical(data: List[Dict[str, Any]]) -> bool:
    """Upserts FMP financial scores data into the 'fmp_financial_scores_historical' table."""
    return upsert_data('fmp_financial_scores_historical', data)

def update_owner_earnings_historical(data: List[Dict[str, Any]]) -> bool:
    """Upserts historical owner earnings into the 'owner_earnings_historical' table."""
    return upsert_data('owner_earnings_historical', data)

def update_enterprise_values_historical(data: List[Dict[str, Any]]) -> bool:
    """Upserts historical enterprise value data into the 'enterprise_values_historical' table."""
    return upsert_data('enterprise_values_historical', data)

def update_insider_trades(data: List[Dict[str, Any]]) -> bool:
    """Upserts insider trading data into the 'insider_trades' table."""
    return upsert_data('insider_trades', data)

def update_insider_trading_stats(data: List[Dict[str, Any]]) -> bool:
    """Upserts insider trading statistics data into the 'insider_trades' table."""
    return upsert_data('insider_trades', data)

def update_stock_peers(data: List[Dict[str, Any]]) -> bool:
    """Upserts stock peer data into the 'stock_peers' table."""
    return upsert_data('stock_peers', data)

def update_dcf_valuations(data: List[Dict[str, Any]]) -> bool:
    """Upserts DCF valuation data into the 'dcf_valuations' table."""
    return upsert_data('dcf_valuations', data)

def update_institutional_ownership_summary(data: List[Dict[str, Any]]) -> bool:
    """Upserts institutional ownership summary data into the 'institutional_ownership_summary' table."""
    return upsert_data('institutional_ownership_summary', data)

def update_institutional_holdings(data: List[Dict[str, Any]]) -> bool:
    """Upserts institutional holdings detail data into the 'institutional_holdings' database table."""
    return upsert_data('institutional_holdings', data)

def update_esg_scores_historical(data: List[Dict[str, Any]]) -> bool:
    """Upserts historical ESG scores into the 'esg_scores_historical' table."""
    return upsert_data('esg_scores_historical', data)

def update_earnings_reports(data: List[Dict[str, Any]]) -> bool:
    """Upserts earnings report records into the 'earnings_reports' table."""
    return upsert_data('earnings_reports', data)

def update_dividends_historical(data: List[Dict[str, Any]]) -> bool:
    """Upserts historical dividend records into the 'dividends' table."""
    return upsert_data('dividends', data)

def clear_stock_peers(symbols: set) -> bool:
    """
    Clears existing stock peer relationships for the given symbols.
    
    Args:
        symbols: Set of stock symbols to clear peer relationships for
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert set to list for SQL query
        symbol_list = list(symbols)
        
        if not symbol_list:
            logger.warning("No symbols provided to clear_stock_peers")
            return False
            
        # Delete peer relationships where the symbol is in our list
        logger.info(f"Clearing existing peer relationships for {len(symbol_list)} symbols")
        response = supabase.table('stock_peers').delete().in_('symbol', symbol_list).execute()
        
        # Log the operation success
        logger.info(f"Successfully cleared peer relationships")
        return True
    except Exception as e:
        logger.error(f"Error clearing stock peer relationships: {e}")
        return False

# TODO: Add functions to FETCH data FROM Supabase if needed for calculations
# e.g., def get_latest_statements(symbol: str, period: str, statement_type: str, count: int = 1)
