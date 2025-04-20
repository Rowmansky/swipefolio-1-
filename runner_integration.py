#!/usr/bin/env python3
"""
Integration runner for ESG tasks: fetches with live FMP API and upserts to Supabase.
Usage: Set environment variables (SUPABASE_URL, SUPABASE_KEY, FMP_API_KEY) then:
    python runner_integration.py AAPL MSFT
"""
import logging
import sys
from fmp_fetcher.tasks.esg_tasks import fetch_and_store_esg_scores

# Configure root logger to DEBUG
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")

if __name__ == '__main__':
    symbols = sys.argv[1:]
    if not symbols:
        print("Usage: python runner_integration.py <symbol1> [<symbol2> ...]")
        sys.exit(1)
    print(f"Running live ESG fetch and upsert for: {symbols}")
    payload = fetch_and_store_esg_scores(symbols)
    # Show merged payload for review
    import json as _json
    from fmp_fetcher.clients.db_client import convert_decimals_in_dict
    print("Final merged ESG payload:")
    # Convert Decimal values to floats for JSON serialization
    converted = [convert_decimals_in_dict(rec) for rec in payload]
    print(_json.dumps(converted, indent=2))
    # Then confirm upsert
    print("Done.")
