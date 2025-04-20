#!/usr/bin/env python3
"""
Integration runner for Political Disclosures tasks: fetches live Senate/House trades and upserts to Supabase.
Usage: Set environment variables (SUPABASE_URL, SUPABASE_KEY, FMP_API_KEY) then:
    python runner_integration_political.py AAPL [MSFT ...]
"""
import logging
import sys
import json
from fmp_fetcher.clients.db_client import convert_decimals_in_dict, get_supabase_client
from fmp_fetcher.tasks.political_tasks import fetch_and_store_political_disclosures

# Configure root logger to DEBUG
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")

if __name__ == '__main__':
    symbols = sys.argv[1:]
    if not symbols:
        print("Usage: python runner_integration_political.py <symbol1> [<symbol2> ...]")
        sys.exit(1)
    print(f"Running live political disclosures fetch and upsert for: {symbols}")
    payload = fetch_and_store_political_disclosures(symbols)
    # Show merged payload for review
    print("Final political disclosures payload:")
    converted = [convert_decimals_in_dict(rec) for rec in payload]
    print(json.dumps(converted, indent=2))
    # Verify insertion by querying the table
    supabase = get_supabase_client()
    # Sample rows by ticker filter
    resp = supabase.table('political_disclosures').select('*', count='exact').eq('ticker', symbols[0]).limit(5).execute()
    print(f"Sample rows for {symbols[0]} (count={resp.count}):")
    import json as _j
    print(_j.dumps(resp.data, indent=2))
    # Overall table count
    all_resp = supabase.table('political_disclosures').select('*', count='exact').execute()
    print(f"Total rows in 'political_disclosures' table: {all_resp.count}")
    print("Done.")
