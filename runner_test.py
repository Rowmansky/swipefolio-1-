#!/usr/bin/env python3
"""
Smoke-test runner for all new FMP fetch tasks: ownership, ESG, earnings, dividends.
Usage: python runner_test.py
"""
import logging
import sys

from fmp_fetcher.tasks.ownership_tasks import (
    fetch_and_store_inst_own_summary,
    fetch_and_store_inst_holdings
)
from fmp_fetcher.tasks.esg_tasks import fetch_and_store_esg_scores
from fmp_fetcher.tasks.earnings_tasks import fetch_and_store_earnings_reports
from fmp_fetcher.tasks.dividend_tasks import fetch_and_store_dividends_historical

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

# Symbols to test against; ensure stocks exist in DB or provide via upstream profile load
SYMBOLS = ["AAPL", "MSFT"]

# List of (name, function) pairs to run
TASKS = [
    ("Ownership Summary", lambda: fetch_and_store_inst_own_summary(SYMBOLS, full_years=2, partial_quarters=2)),
    ("Ownership Holdings", lambda: fetch_and_store_inst_holdings(SYMBOLS, full_years=2, partial_quarters=2, top_holders_limit=10)),
    ("ESG Scores", lambda: fetch_and_store_esg_scores(SYMBOLS)),
    ("Earnings Reports", lambda: fetch_and_store_earnings_reports(SYMBOLS)),
    ("Dividends Historical", lambda: fetch_and_store_dividends_historical(SYMBOLS)),
]


def run_task(name, func):
    logging.info(f"Running: {name}")
    try:
        result = func()
        logging.info(f"✅ {name} completed")
        return True
    except Exception:
        logging.exception(f"❌ {name} failed")
        return False


def main():
    errors = False
    for name, func in TASKS:
        ok = run_task(name, func)
        if not ok:
            errors = True
    if errors:
        logging.error("One or more tasks failed. See logs above.")
        sys.exit(1)
    logging.info("All new tasks passed smoke tests.")


if __name__ == '__main__':
    main()
