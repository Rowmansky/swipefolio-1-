#!/usr/bin/env python3
"""
Integration runner for insider trading data and statistics: fetches with live FMP API, upserts to Supabase, and prints payloads.
Usage: Set environment variables (SUPABASE_URL, SUPABASE_KEY, FMP_API_KEY) then:
    python runner_insider_trading.py AAPL MSFT
"""
import logging
import sys
from fmp_fetcher.tasks.insider_trading_tasks import (
    fetch_and_store_insider_trades,
    fetch_and_store_insider_trading_stats
)

# Configure root logger to DEBUG
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")

if __name__ == '__main__':
    symbols = sys.argv[1:]
    if not symbols:
        print("Usage: python runner_insider_trading.py <symbol1> [<symbol2> ...]")
        sys.exit(1)
    print(f"Running live insider trades fetch/upsert for: {symbols}")
    trades_payload = fetch_and_store_insider_trades(symbols)
    stats_payload = fetch_and_store_insider_trading_stats(symbols)

    import json as _json
    from fmp_fetcher.clients.db_client import convert_decimals_in_dict

    print("\nFinal insider trades payload:")
    trades_converted = [convert_decimals_in_dict(rec) for rec in trades_payload]
    print(_json.dumps(trades_converted, indent=2))

    print("\nFinal insider trading statistics payload:")
    stats_converted = [convert_decimals_in_dict(rec) for rec in stats_payload]
    print(_json.dumps(stats_converted, indent=2))

    print("Done.")
