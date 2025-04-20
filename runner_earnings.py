#!/usr/bin/env python3
"""
Integration runner for historical earnings reports: fetches with live FMP API, upserts to Supabase, and prints payload.
Usage: Set environment variables (SUPABASE_URL, SUPABASE_KEY, FMP_API_KEY) then:
    python runner_earnings.py AAPL MSFT
"""
import logging
import sys
from fmp_fetcher.tasks.earnings_tasks import fetch_and_store_earnings_reports

# Configure root logger to DEBUG
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")

if __name__ == '__main__':
    symbols = sys.argv[1:]
    if not symbols:
        print("Usage: python runner_earnings.py <symbol1> [<symbol2> ...]")
        sys.exit(1)
    print(f"Running live historical earnings fetch and upsert for: {symbols}")
    payload = fetch_and_store_earnings_reports(symbols)
    # Show payload for review
    import json as _json
    from fmp_fetcher.clients.db_client import convert_decimals_in_dict
    print("Final earnings payload (actual vs estimates):")
    converted = [convert_decimals_in_dict(rec) for rec in payload]
    print(_json.dumps(converted, indent=2))
    print("Done.")
