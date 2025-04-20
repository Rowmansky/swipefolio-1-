import os
import logging
import sys
from postgrest import APIError
from fmp_fetcher.config import get_supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("debug_db_schema")

def main():
    """Debug script to validate database schema and column names"""
    try:
        supabase = get_supabase_client()
        
        # Try to get column information for the stock_news table
        logger.info("Testing stock_news table...")
        # First get a single record to check column names
        try:
            stock_news_result = supabase.table("stock_news").select("*").limit(1).execute()
            print(f"Stock News columns: {list(stock_news_result.data[0].keys()) if stock_news_result.data else 'No data'}")
        except APIError as e:
            logger.error(f"Error with stock_news: {e}")
            # Try to get the definition via SQL if we have permission
            try:
                sql_result = supabase.rpc(
                    "debugging_table_columns", 
                    {"table_name": "stock_news"}
                ).execute()
                print(f"Stock News SQL info: {sql_result.data}")
            except Exception as e2:
                logger.error(f"SQL error: {e2}")
        
        # Try to get column information for the press_releases table
        logger.info("Testing press_releases table...")
        try:
            press_releases_result = supabase.table("press_releases").select("*").limit(1).execute()
            print(f"Press Releases columns: {list(press_releases_result.data[0].keys()) if press_releases_result.data else 'No data'}")
        except APIError as e:
            logger.error(f"Error with press_releases: {e}")
            # Try to get the definition via SQL if we have permission
            try:
                sql_result = supabase.rpc(
                    "debugging_table_columns", 
                    {"table_name": "press_releases"}
                ).execute()
                print(f"Press Releases SQL info: {sql_result.data}")
            except Exception as e2:
                logger.error(f"SQL error: {e2}")
        
        # Try another approach - try inserting with a minimal set of fields
        logger.info("Testing minimal insert to press_releases...")
        try:
            # Try with just the required fields for a test record
            test_record = {
                'title': 'DEBUG TEST - PLEASE DELETE',
                'source_url': 'https://test-debug-delete-me.example.com/test',
                'published_date': '2025-04-16T00:00:00Z'
            }
            insert_result = supabase.table("press_releases").insert(test_record).execute()
            logger.info(f"Insert succeeded with minimal fields: {test_record.keys()}")
            # Clean up test record
            delete_result = supabase.table("press_releases").delete().eq('source_url', test_record['source_url']).execute()
            logger.info(f"Test record deleted")
        except APIError as e:
            logger.error(f"Minimal insert error: {str(e)}")
            # Parse the error to see what fields are mentioned
            error_msg = str(e)
            if "column" in error_msg.lower() and "does not exist" in error_msg.lower():
                problem_field = error_msg.split("column")[1].split("does not exist")[0].strip()
                logger.error(f"Problem field appears to be: {problem_field}")
            elif "not-null" in error_msg.lower():
                problem_field = error_msg.split("not-null")[1].split("violat")[0].strip()
                logger.error(f"Missing required field: {problem_field}")
    
    except Exception as e:
        logger.exception(f"Overall debug error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
