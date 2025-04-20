"""
Detailed test for stock peers data fetching workflow
This simulates what happens when we process multiple stocks
"""
import sys
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Import required modules
from fmp_fetcher.clients import fmp_client
logger = logging.getLogger("test_stock_peers")

def test_stock_peers_workflow(symbols: List[str]):
    """Test the stock peers workflow with real API calls"""
    print(f"\n{'=' * 80}")
    print(f"TESTING STOCK PEERS WORKFLOW FOR {len(symbols)} STOCKS")
    print(f"{'=' * 80}")
    
    all_parsed_peers = []
    
    for symbol in symbols:
        print(f"\n{'=' * 40}")
        print(f"Processing {symbol}")
        print(f"{'=' * 40}")
        
        # Make the API request
        endpoint_path = "/stable/stock-peers"
        params = {'symbol': symbol}
        
        print(f"Calling API: {endpoint_path} with params: {params}")
        api_data = fmp_client.make_fmp_request(endpoint_path=endpoint_path, params=params)
        
        # Show the raw API response
        print(f"\nRaw API response type: {type(api_data)}")
        print(f"Raw API response: {api_data}")
        
        if api_data is None:
            print(f"❌ Failed to fetch data for {symbol}")
            continue
            
        # Process the response
        if isinstance(api_data, dict) and 'peersList' in api_data:
            print(f"\n✅ Received response with 'peersList' key")
            peer_list = api_data.get('peersList', [])
            print(f"Peers list type: {type(peer_list)}")
            print(f"Peers list content: {peer_list}")
            
            for peer_symbol in peer_list:
                if peer_symbol != symbol:
                    print(f"  Adding peer: {symbol} -> {peer_symbol}")
                    parsed = {'symbol': symbol, 'peer_symbol': peer_symbol}
                    all_parsed_peers.append(parsed)
                else:
                    print(f"  Skipping self as peer: {symbol} -> {symbol}")
            
        elif isinstance(api_data, list):
            print(f"\n✅ Received response as list with {len(api_data)} items")
            
            for item in api_data:
                print(f"  Processing list item: {item}")
                
                if isinstance(item, dict) and 'symbol' in item:
                    peer_symbol = item['symbol']
                    print(f"  Extracted peer symbol from dict: {peer_symbol}")
                elif isinstance(item, str):
                    peer_symbol = item
                    print(f"  Using direct string as peer symbol: {peer_symbol}")
                else:
                    print(f"  ❌ Unexpected item format: {type(item)}")
                    continue
                
                if peer_symbol != symbol:
                    print(f"  Adding peer: {symbol} -> {peer_symbol}")
                    parsed = {'symbol': symbol, 'peer_symbol': peer_symbol}
                    all_parsed_peers.append(parsed)
                else:
                    print(f"  Skipping self as peer: {symbol} -> {symbol}")
        else:
            print(f"❌ Unexpected response format: {type(api_data)}")
    
    # Print the final results
    print(f"\n{'=' * 80}")
    print(f"FINAL RESULTS: {len(all_parsed_peers)} PEER RELATIONSHIPS")
    print(f"{'=' * 80}")
    
    for i, peer in enumerate(all_parsed_peers):
        print(f"{i+1}. {peer['symbol']} -> {peer['peer_symbol']}")
    
    return all_parsed_peers

if __name__ == "__main__":
    # Test with 5 diverse stocks
    test_symbols = ["AAPL", "MSFT", "JPM", "JNJ", "AMZN"]
    results = test_stock_peers_workflow(test_symbols)
    
    print(f"\nTotal peer relationships found: {len(results)}")
