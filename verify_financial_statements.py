#!/usr/bin/env python
# verify_financial_statements.py - Check what's actually in the database
import os
import sys
import logging
from dotenv import load_dotenv
from fmp_fetcher.config import get_supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def verify_database():
    """Check what financial statements are actually in the database"""
    # Load environment variables
    load_dotenv()
    
    # Symbols to verify
    symbols = ["AAPL", "MSFT", "GOOG", "PLD"]
    statement_types = ["income", "balance", "cashflow"]
    
    # Connect to Supabase
    try:
        supabase = get_supabase_client()
        
        # First, count total statements in the database
        result = supabase.table("financial_statements").select("*", count="exact").execute()
        total_count = 0
        if hasattr(result, 'count'):
            total_count = result.count
        
        logger.info(f"Total statements in database: {total_count}")
        
        # Check each symbol
        for symbol in symbols:
            logger.info(f"\n=== CHECKING {symbol} STATEMENTS ===")
            
            # First get all statements for this symbol
            all_stmts = supabase.table("financial_statements").select("*").eq("symbol", symbol).execute()
            
            if hasattr(all_stmts, 'data') and all_stmts.data:
                logger.info(f"Found {len(all_stmts.data)} total statements for {symbol}")
                
                # Group by statement type
                by_type = {}
                for stmt in all_stmts.data:
                    stmt_type = stmt.get('statement_type')
                    if stmt_type not in by_type:
                        by_type[stmt_type] = []
                    by_type[stmt_type].append(stmt)
                
                # Show counts by type
                for stmt_type, stmts in by_type.items():
                    logger.info(f"  - {len(stmts)} {stmt_type} statements")
                    # Show the first record of each type
                    if stmts:
                        sample = stmts[0]
                        logger.info(f"    Sample: {sample.get('report_date')} | ID: {sample.get('id')}")
            else:
                logger.warning(f"No statements found for {symbol}")
        
        # Check specifically for statement types that might be missing
        logger.info("\n=== CHECKING FOR MISSING STATEMENT TYPES ===")
        for symbol in symbols:
            for stmt_type in statement_types:
                result = supabase.table("financial_statements").select("id").eq("symbol", symbol).eq("statement_type", stmt_type).execute()
                
                if not (hasattr(result, 'data') and result.data):
                    logger.warning(f"⚠️ MISSING: No {stmt_type} statements found for {symbol}")
                    
                    # Let's try inserting a test statement of this type
                    logger.info(f"Attempting to create a test {stmt_type} statement for {symbol}...")
                    
                    # Create a minimal test statement
                    test_stmt = {
                        'symbol': symbol,
                        'report_date': '2023-12-31',
                        'statement_type': stmt_type,
                        'period': 'annual',
                        'calendar_year': 2023,
                        'data': {'test': True}
                    }
                    
                    # Try to insert it
                    try:
                        insert_result = supabase.table("financial_statements").insert(test_stmt).execute()
                        if hasattr(insert_result, 'data') and insert_result.data:
                            logger.info(f"✅ Successfully inserted test {stmt_type} statement for {symbol}")
                        else:
                            logger.error(f"❌ Failed to insert test {stmt_type} statement for {symbol}")
                    except Exception as e:
                        logger.error(f"❌ Error inserting test statement: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    logger.info("🔍 Starting financial statement verification...")
    success = verify_database()
    
    if success:
        logger.info("✅ Verification completed")
    else:
        logger.error("❌ Verification failed")
