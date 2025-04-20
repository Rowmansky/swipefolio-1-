# quick_debug.py
import argparse
from fmp_fetcher.clients.fmp_client import make_fmp_request
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Quick debug FMP endpoints')
    parser.add_argument('--symbols', nargs='+', default=['AAPL','PLD','O','PGN'], help='Stock symbols to test')
    parser.add_argument('--period', choices=['annual','quarter'], default='annual', help='Estimate period')
    parser.add_argument('--page', type=int, default=0, help='Estimate page')
    parser.add_argument('--limit', type=int, default=1, help='Limit per request')
    args = parser.parse_args()
    endpoints = [
        '/stable/price-target-news',
        '/stable/grades-news',
        '/stable/ratings-snapshot',
        '/stable/grades',
        '/stable/price-target-consensus',
        '/stable/grades-consensus',
        '/stable/analyst-estimates',
    ]
    for ep in endpoints:
        for sym in args.symbols:
            params = {'symbol': sym, 'limit': args.limit}
            if ep == '/stable/analyst-estimates':
                params.update({'period': args.period, 'page': args.page})
            data = make_fmp_request(ep, params)
            if data is None:
                count = 0
            elif isinstance(data, list):
                count = len(data)
            else:
                count = 1
            print(f"{ep} [{sym}] → {count} records → {data[:1] if isinstance(data, list) and data else data}")
