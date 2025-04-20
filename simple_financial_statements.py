#!/usr/bin/env python
# simple_financial_statements.py — Dead simple financial statement fetching

import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from fmp_fetcher.clients import db_client
from fmp_fetcher.clients.fmp_client import make_fmp_request
from fmp_fetcher.config import TARGET_SYMBOLS

# — Load .env immediately so API key is available —
load_dotenv()

# — Configure logging so you always see INFO + DEBUG —
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)
logger = logging.getLogger(__name__)

# — Print a start banner so you know the script actually ran —
print("\n🔄 Starting simple_financial_statements.py\n", flush=True)

# — Which statements we fetch from FMP —
STATEMENT_TYPES = [
    "income-statement",
    "balance-sheet-statement",
    "cash-flow-statement",
]

# — How to map the FMP endpoint to your DB enum —
DB_ENUM_MAP = {
    "income-statement": "income",
    "balance-sheet-statement": "balance",
    "cash-flow-statement": "cashflow",
}


def ensure_profiles_exist(symbols):
    """Create minimal stock profiles if needed (for FK constraints)."""
    profiles = []
    for symbol in symbols:
        profiles.append({
            'symbol': symbol,
            'company_name': f'Test Company {symbol}',
            'exchange': 'TEST',
            'industry': 'Testing',
            'sector': 'Technology',
            'country': 'USA',
            'is_actively_trading': True
        })

    success = db_client.update_stocks(profiles)
    if success:
        logger.info("✅ Stock profiles ready for %d symbols", len(profiles))
        return True
    else:
        logger.error("❌ Failed to create stock profiles")
        return False


def map_period(api_period):
    """Convert FMP period values (FY, Q1–Q4) to your DB enum."""
    period_map = {
        "FY": "annual",
        "Q1": "quarter",
        "Q2": "quarter",
        "Q3": "quarter",
        "Q4": "quarter",
    }
    return period_map.get(api_period, "annual")


def fetch_financial_statements(symbols):
    """Fetch & insert all financial statements for the given symbols."""
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        logger.error("FMP_API_KEY not found in environment")
        return False

    # ensure stock profiles exist first
    if not ensure_profiles_exist(symbols):
        return False

    all_statements = []

    for symbol in symbols:
        logger.info("👉 Processing %s …", symbol)

        for stmt_type in STATEMENT_TYPES:
            db_type = DB_ENUM_MAP.get(stmt_type)
            if not db_type:
                logger.error("Unknown statement type mapping for %s", stmt_type)
                continue

            logger.info("Fetching %s for %s …", stmt_type, symbol)
            try:
                data = make_fmp_request(
                    f"/{stmt_type}",
                    {"symbol": symbol, "apikey": api_key}
                )

                # DEBUG: dump the raw JSON so you can inspect it
                logger.debug(
                    "RAW FMP RESPONSE for %s » %s:\n%s\n",
                    symbol, stmt_type,
                    json.dumps(data, indent=2) if data else data
                )

                if not data:
                    logger.warning("No %s data returned for %s", stmt_type, symbol)
                    continue

                logger.info("✅ Got %d %s records for %s", len(data), stmt_type, symbol)

                # Optional: save one sample to disk for offline debugging
                with open(f"sample_{symbol}_{stmt_type.replace('-', '_')}.json", "w") as f:
                    json.dump(data[0], f, indent=2)

                # Build DB records
                for item in data:
                    report_date   = item.get('date') or item.get('reportDate')
                    filing_date   = item.get('filingDate')
                    accepted_date = item.get('acceptedDate')

                    record = {
                        'symbol'            : symbol,
                        'report_date'       : report_date,
                        'filing_date'       : filing_date,
                        'accepted_date'     : accepted_date,
                        'calendar_year'     : int(item.get('fiscalYear', 0)),
                        'period'            : map_period(item.get('period')),
                        'statement_type'    : db_type,
                        'cik'               : item.get('cik'),
                        'link'              : None,
                        'source_filing_url' : None,
                        'data'              : item,
                        'last_fetched'      : datetime.now().isoformat(),
                    }
                    all_statements.append(record)

            except Exception as e:
                logger.error("Error fetching %s for %s: %s", stmt_type, symbol, e)

    if not all_statements:
        logger.warning("⚠️ No statements to insert")
        return False

    logger.info("Inserting %d financial statements into database …", len(all_statements))
    try:
        success = db_client.update_financial_statements(all_statements)
        if success:
            logger.info("✅ Successfully inserted %d statements", len(all_statements))
            return True
        else:
            logger.error("❌ Failed to insert statements")
            return False
    except Exception as e:
        logger.error("Error inserting statements: %s", e)
        return False


if __name__ == "__main__":
    ok = False
    try:
        symbols = sys.argv[1:] if len(sys.argv) > 1 else TARGET_SYMBOLS
        logger.info("Fetching financial statements for: %s", symbols)
        ok = fetch_financial_statements(symbols)
        logger.info("Finished fetching — success=%s", ok)
    except Exception as e:
        logger.exception("‼️ Uncaught exception in __main__: %s", e)
    finally:
        sys.exit(0 if ok else 1)
