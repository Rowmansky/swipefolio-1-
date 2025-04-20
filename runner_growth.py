#!/usr/bin/env python3
"""
Runner for financial statement growth bulk endpoint.
Usage: python runner_growth.py <year> <period> <symbol1> [<symbol2> ...]
"""
import sys
from dotenv import load_dotenv
load_dotenv()
from fmp_fetcher.tasks.financial_statement_tasks import fetch_and_store_statement_growth

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python runner_growth.py <year> <period> <symbol1> [<symbol2> ...]")
        sys.exit(1)
    year = int(sys.argv[1])
    period = sys.argv[2]
    symbols = sys.argv[3:]
    print(f"Fetching growth for year={year}, period={period}, symbols={symbols}")
    success = fetch_and_store_statement_growth(symbols, year, period)
    print(f"Success: {success}")
