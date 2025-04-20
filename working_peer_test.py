"""
Ultra-simple test that uses the exact same approach that worked in our screenshot
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load API key
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
API_KEY = os.getenv("FMP_API_KEY")

# Use AAPL which we know returned peers in the screenshot
symbol = "AAPL"
print(f"Testing with symbol: {symbol}")

# The exact URL that worked in our direct test that showed "BABA, ETSY, etc."
url = f"https://financialmodelingprep.com/api/v3/stock-peers"
params = {'symbol': symbol, 'apikey': API_KEY}

print(f"Making API call to: {url}")
response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"API response type: {type(data)}")
    
    if data:
        print(f"Got {len(data)} peer items")
        for i, item in enumerate(data):
            print(f"  Peer {i+1}: {json.dumps(item)}")
            
            # Extract the actual peer relationship
            if isinstance(item, dict) and 'symbol' in item:
                peer_symbol = item['symbol']
                print(f"    Symbol: {peer_symbol}")
                
                # This is the exact data we'd store
                peer_record = {
                    'symbol': symbol,
                    'peer_symbol': peer_symbol
                }
                print(f"    Record: {peer_record}")
    else:
        print("Empty response data")
else:
    print(f"Error: {response.status_code}, {response.text}")
