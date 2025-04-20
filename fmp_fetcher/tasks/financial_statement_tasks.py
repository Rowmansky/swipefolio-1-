# fmp_fetcher/tasks/financial_statement_tasks.py

import logging
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

from fmp_fetcher.clients import fmp_client, db_client
from fmp_fetcher.utils import parsing

logger = logging.getLogger(__name__)

# Statement types supported by the FMP API
SUPPORTED_STATEMENT_TYPES = [
    "income-statement",
    "balance-sheet-statement",
    "cash-flow-statement",
]

SUPPORTED_PERIODS = ["Q1", "Q2", "Q3", "Q4", "FY"]

def fetch_and_store_statements(
    symbols: List[str],
    year: int,
    period: Literal["Q1", "Q2", "Q3", "Q4", "FY"],
) -> bool:
    """
    Fetch financial statements for each symbol individually and store in database.
    
    This implementation uses individual API calls per symbol rather than bulk endpoints,
    which is more reliable across different API subscription levels.
    
    Args:
        symbols: List of stock symbols to fetch data for
        year: The calendar year to fetch statements for
        period: The period type (Q1, Q2, Q3, Q4, FY)
        
    Returns:
        True if operation was successful, False otherwise
    """
    if not symbols:
        logger.warning("No symbols provided for financial statements fetching")
        return False
    
    if period not in SUPPORTED_PERIODS:
        logger.error(f"Invalid period '{period}'. Must be one of {SUPPORTED_PERIODS}")
        return False
        
    logger.info(f"Fetching financial statements for {len(symbols)} symbols, "
               f"year={year}, period={period}")
    
    # Collect all parsed statements here
    all_statements = []
    has_errors = False

    # Process each symbol and statement type individually
    for symbol in symbols:
        logger.info(f"Processing statements for {symbol}...")
        
        for stmt_name in SUPPORTED_STATEMENT_TYPES:
            # Convert to database format: income-statement -> income
            db_type = stmt_name.replace("-statement", "").replace("-", "")
            
            # Use individual endpoint format: /api/v3/income-statement/AAPL
            endpoint = f"api/v3/{stmt_name}/{symbol}"
            
            # Request parameters - limit is the number of statements to return
            # Use higher limit to make sure we find the specific year/period
            params = {
                "limit": 10  
            }
            
            # If period is specified, add it to the parameters
            if period != "FY":  # FY is default, no need to specify
                params["period"] = period
                
            logger.info(f"Fetching {stmt_name} for {symbol}...")
            
            try:
                # Make the API request
                statements = fmp_client.make_fmp_request(
                    endpoint_path=endpoint,
                    params=params
                )
                
                if statements and isinstance(statements, list) and statements:
                    # Filter statements for the requested year
                    matching_statements = []
                    
                    for stmt in statements:
                        # Match both year and period
                        if (str(stmt.get('calendarYear', '')) == str(year) and 
                            stmt.get('period', '').upper() == period.upper()):
                            matching_statements.append(stmt)
                    
                    if matching_statements:
                        logger.info(f"Found {len(matching_statements)} matching {stmt_name} for {symbol} ({year} {period})")
                        
                        # Process each statement for database storage
                        for stmt_data in matching_statements:
                            # Create a record for database storage
                            record = {
                                'symbol': symbol,
                                'report_date': stmt_data.get('date'),
                                'filing_date': stmt_data.get('fillingDate'),  # Note FMP typo 'fillingDate'
                                'accepted_date': stmt_data.get('acceptedDate'),
                                'calendar_year': int(stmt_data.get('calendarYear')),
                                'period': stmt_data.get('period'),  # Keep original case for the enum (FY, Q1, etc.)
                                'statement_type': db_type.lower(),
                                'cik': stmt_data.get('cik'),
                                'link': stmt_data.get('link'),
                                'source_filing_url': stmt_data.get('finalLink'),
                                'data': stmt_data
                            }
                            all_statements.append(record)
                    else:
                        logger.warning(f"No {stmt_name} data found for {symbol} matching {year} {period}")
                else:
                    logger.warning(f"No {stmt_name} data returned for {symbol}")
                    
            except Exception as e:
                logger.exception(f"Error fetching {stmt_name} for {symbol}: {e}")
                has_errors = True
    
    # Insert all statements into the database
    if all_statements:
        logger.info(f"Inserting {len(all_statements)} financial statements into database")
        try:
            success = db_client.update_financial_statements(all_statements)
            if success:
                logger.info(f"✅ Successfully inserted {len(all_statements)} financial statements")
            else:
                logger.error("❌ Failed to insert financial statements")
                has_errors = True
        except Exception as e:
            logger.exception(f"Error inserting financial statements: {e}")
            has_errors = True
    else:
        logger.warning(f"No financial statements found for any symbols for {year} {period}")
    
    return not has_errors

def fetch_and_store_statement_growth(
    symbols: List[str],
    year: int,
    period: Literal["Q1", "Q2", "Q3", "Q4", "FY"],
) -> bool:
    """
    Fetches bulk statement growth data for given symbols, year, and period,
    parses them, and upserts into 'financial_statement_growth' table.
    """
    if not symbols:
        logger.warning("No symbols provided for statement growth fetching")
        return False
    if period not in SUPPORTED_PERIODS:
        logger.error(f"Invalid period '{period}'. Must be one of {SUPPORTED_PERIODS}")
        return False
    logger.info(f"Fetching growth data for {len(symbols)} symbols, year={year}, period={period}")
    all_growth = []
    has_errors = False
    for stmt_name in SUPPORTED_STATEMENT_TYPES:
        db_type = stmt_name.replace("-statement", "").replace("-", "").lower()
        endpoint = f"/stable/{stmt_name}-growth-bulk"
        params = {"year": year, "period": period}
        try:
            bulk_data = fmp_client.make_fmp_request(endpoint_path=endpoint, params=params)
            if not bulk_data or not isinstance(bulk_data, list):
                logger.warning(f"No bulk growth data for {stmt_name} ({year} {period})")
                continue
            for item in bulk_data:
                sym = item.get('symbol')
                if not sym or sym not in symbols:
                    continue
                rec = parsing.parse_statement_growth(item, sym, db_type)
                if rec:
                    all_growth.append(rec)
                else:
                    logger.warning(f"Failed to parse growth for {sym}, type {db_type}: {item}")
        except Exception as e:
            logger.exception(f"Error fetching bulk growth for {stmt_name}: {e}")
            has_errors = True
    if all_growth:
        logger.info(f"Upserting {len(all_growth)} growth records into database")
        ok = db_client.update_financial_statement_growth(all_growth)
        if not ok:
            logger.error("Failed to upsert statement growth records")
            has_errors = True
    else:
        logger.warning(f"No growth records parsed for {year} {period}")
    return not has_errors
