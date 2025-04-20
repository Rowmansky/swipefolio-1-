"""
Quick test script to verify stock peers API is working correctly
"""
import os
import sys
import requests
import json

# Get API key from environment or use the one provided
api_key = os.environ.get('FMP_API_KEY', '69qQMNBueqOq5EQHCnlHHA6GGESc1LQy')
symbol = "AAPL"  # Test with Apple

# Use the exact URL format provided
url = f"https://financialmodelingprep.com/stable/stock-peers?symbol={symbol}&apikey={api_key}"

print(f"Testing stock peers API with URL: {url}")
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    print(f"\nAPI response type: {type(data)}")
    print(f"API response content: {json.dumps(data, indent=2)}")
    
    # Check the structure of the response
    if isinstance(data, list):
        print(f"\nReceived list of {len(data)} items")
        for i, item in enumerate(data[:5]):  # Show first 5 peers
            print(f"  Peer {i+1}: {item}")
    elif isinstance(data, dict) and 'peersList' in data:
        peers = data['peersList']
        print(f"\nReceived dict with peersList containing {len(peers)} peers")
        for i, peer in enumerate(peers[:5]):  # Show first 5 peers
            print(f"  Peer {i+1}: {peer}")
    else:
        print("Unexpected response format")
else:
    print(f"Error: {response.status_code}, {response.text}")

# Now let's examine the clear_stock_peers and update_stock_peers functions in db_client
try:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from fmp_fetcher.clients.db_client import clear_stock_peers, update_stock_peers
    print("\nSuccessfully imported clear_stock_peers and update_stock_peers from db_client")
except ImportError as e:
    print(f"\nError importing functions from db_client: {e}")
    
    # Check if just one function is missing
    try:
        from fmp_fetcher.clients.db_client import update_stock_peers
        print("Successfully imported update_stock_peers, but clear_stock_peers is missing")
    except ImportError:
        print("Both update_stock_peers and clear_stock_peers are missing")
