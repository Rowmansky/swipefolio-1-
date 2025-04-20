"""
Direct test of the stock peers endpoint to verify correct URL format
"""
import requests
import json
import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("direct_test")

# Load environment variables 
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv("FMP_API_KEY")

# Test symbols
test_symbols = ["AAPL", "MSFT", "JPM", "JNJ", "AMZN"]

def direct_api_call(symbol):
    """Make a direct API call to the stock peers endpoint"""
    # Correct URL format (no duplicate 'stable')
    base_url = "https://financialmodelingprep.com/api/v3"
    endpoint = f"/stock-peers"
    
    # Try different endpoint formats
    endpoints_to_try = [
        # Format 1: v3 directly to stock-peers with symbol param
        f"{base_url}{endpoint}",
        # Format 2: stable version
        f"https://financialmodelingprep.com/stable/stock-peers", 
        # Format 3: v4 version
        f"https://financialmodelingprep.com/api/v4/stock-peers"
    ]
    
    results = {}
    
    for i, url in enumerate(endpoints_to_try):
        try:
            params = {'symbol': symbol, 'apikey': API_KEY}
            
            # Hide API key in logs
            log_params = {k: '***REDACTED***' if k == 'apikey' else v for k, v in params.items()}
            logger.info(f"Testing endpoint {i+1}: {url} with params: {log_params}")
            
            response = requests.get(url, params=params, timeout=30)
            
            # Check response status
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Response type: {type(data)}")
                print(f"Endpoint {i+1} SUCCESS - Response: {json.dumps(data, indent=2)}")
                results[f"endpoint_{i+1}"] = data
            else:
                logger.error(f"Endpoint {i+1} Failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Error with endpoint {i+1}: {str(e)}")
    
    return results

# Process each test symbol
print(f"Testing {len(test_symbols)} symbols for peer data...")

for symbol in test_symbols:
    print(f"\n{'=' * 60}")
    print(f"TESTING SYMBOL: {symbol}")
    print(f"{'=' * 60}")
    
    results = direct_api_call(symbol)
    
    # Process and format results for this symbol
    for endpoint_name, data in results.items():
        if isinstance(data, list):
            if data:
                print(f"\n✅ [{endpoint_name}] Got list with {len(data)} items")
                # If items are dictionaries, extract peer symbols
                if data and isinstance(data[0], dict) and 'symbol' in data[0]:
                    peer_symbols = [item['symbol'] for item in data]
                    print(f"Peer symbols: {', '.join(peer_symbols)}")
            else:
                print(f"\n❌ [{endpoint_name}] Empty list returned")
        elif isinstance(data, dict) and 'peersList' in data:
            peers = data['peersList']
            print(f"\n✅ [{endpoint_name}] Got dictionary with 'peersList' containing {len(peers)} items")
            print(f"Peer symbols: {', '.join(peers)}")
        else:
            print(f"\n❓ [{endpoint_name}] Unexpected format: {type(data)}")
    
    if not results:
        print(f"❌ No successful responses for {symbol}")

print("\nTest completed!")
