#!/usr/bin/env python
# test_financial_statements_fix.py
import logging
import sys
import csv
import io
import requests
import json
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_direct_financial_statement_api():
    """Test direct API call to financial statements endpoint using the correct format."""
    # Load API key
    load_dotenv()
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        logger.error("FMP_API_KEY not found. Please check .env file.")
        return False
    
    # Test symbol and parameters - using a previous year that's more likely to have data
    symbol = "AAPL"
    year = 2022
    period = "FY"
    
    # Test income statement bulk endpoint directly with the stable prefix
    url = f"https://financialmodelingprep.com/stable/income-statement-bulk"
    params = {
        "year": year,
        "period": period,
        "apikey": api_key
    }
    
    logger.info(f"Making direct API call to: {url} for {year} {period}")
    
    try:
        response = requests.get(url, params=params)
        
        # Log response status
        logger.info(f"Response status code: {response.status_code}")
        
        # Check if it's a successful response
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"Response Content-Type: {content_type}")
            
            # Try parsing as JSON first
            try:
                data = response.json()
                if isinstance(data, list):
                    logger.info(f"JSON response with {len(data)} items")
                    if data:
                        # Print first item keys and sample values
                        sample = data[0]
                        logger.info(f"Sample keys: {list(sample.keys())[:10]}...")  # Show first 10 keys
                        logger.info(f"Symbol: {sample.get('symbol', 'N/A')}")
                        logger.info(f"Date: {sample.get('date', 'N/A')}")
                        
                        # Save sample data to a file for review
                        with open('sample_financial_data.json', 'w') as f:
                            json.dump(sample, f, indent=2)
                        logger.info("Saved sample data to sample_financial_data.json")
                        
                        return True
                else:
                    logger.warning(f"Unexpected JSON format: {type(data)}")
            except ValueError:
                # Not JSON, try parsing as CSV
                csv_text = response.text
                logger.info(f"Attempting to parse as CSV. First 100 chars: {csv_text[:100]}")
                
                try:
                    reader = csv.DictReader(io.StringIO(csv_text))
                    rows = list(reader)
                    
                    if rows:
                        logger.info(f"Successfully parsed CSV with {len(rows)} rows")
                        logger.info(f"First row keys: {list(rows[0].keys())}")
                        
                        # Save sample data to a file for review
                        with open('sample_financial_data.csv', 'w') as f:
                            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                            writer.writeheader()
                            writer.writerows(rows[:5])  # Write first 5 rows
                        logger.info("Saved sample data to sample_financial_data.csv")
                        
                        return True
                except Exception as csv_error:
                    logger.error(f"Error parsing as CSV: {csv_error}")
                    logger.info(f"Response raw content (first 500 chars): {response.text[:500]}")
        else:
            logger.error(f"Error response: {response.text}")
        
    except Exception as e:
        logger.error(f"Error making API call: {e}")
    
    return False

if __name__ == "__main__":
    logger.info("Testing financial statements API with corrected URL format...")
    success = test_direct_financial_statement_api()
    
    if success:
        logger.info("✅ Financial statements API test passed!")
    else:
        logger.error("❌ Financial statements API test failed!")
