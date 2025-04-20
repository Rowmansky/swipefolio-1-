#!/usr/bin/env python3
"""
Standalone test runner for Political Disclosures tasks without pytest.
Usage: python runner_political_test.py
"""
import logging
import sys
import json
from pathlib import Path

from fmp_fetcher.tasks.political_tasks import fetch_and_store_political_disclosures
from fmp_fetcher.clients import fmp_client, db_client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

FIXTURE_DIR = Path(__file__).parent / 'tests' / 'fixtures'

def load_fixture(name):
    path = FIXTURE_DIR / name
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"❌ Failed to load fixture {name}: {e}")
        sys.exit(1)

# Load fixtures
senate = load_fixture('senate_trades.json')
house = load_fixture('house_trades.json')

# Stub FMP client
original_make = fmp_client.make_fmp_request
captured = []

def fake_make_request(endpoint_path, params):
    if 'senate-trades' in endpoint_path:
        return senate
    if 'house-trades' in endpoint_path:
        return house
    return []

fmp_client.make_fmp_request = fake_make_request

# Stub DB upsert
original_update = db_client.update_political_disclosures
def fake_update(data):
    global captured
    captured = data
    return True

# Override
setattr(db_client, 'update_political_disclosures', fake_update)

# Run task
result = fetch_and_store_political_disclosures(['AAPL'])
expected_count = len(senate) + len(house)
if len(captured) != expected_count:
    print(f"❌ Test failed: expected {expected_count} records upserted, got {len(captured)}")
    sys.exit(1)
print(f"✅ Correct number of records upserted: {len(captured)}")

# Validate fields
for rec in captured:
    assert rec['ptr_link'] in (senate[0]['link'], house[0]['link']), f"Unexpected ptr_link: {rec['ptr_link']}"
    assert rec['ticker'] == 'AAPL', f"Unexpected ticker: {rec['ticker']}"
    assert rec['source'] in ('Senate', 'House'), f"Unexpected source: {rec['source']}"

print("✅ Field presence validated.")

# Validate return
if result != captured:
    print("❌ Return payload mismatch.")
    sys.exit(1)
print("✅ fetch_and_store_political_disclosures returned correct payload.")

# Test no-data scenario
print("Running no-data scenario...")
fmp_client.make_fmp_request = lambda *args, **kwargs: []
captured = []
result2 = fetch_and_store_political_disclosures(['AAPL'])
if captured:
    print(f"❌ Expected no upserts, but got {len(captured)}")
    sys.exit(1)
print("✅ No data scenario passed.")

# Cleanup
fmp_client.make_fmp_request = original_make
setattr(db_client, 'update_political_disclosures', original_update)

print("All Political Disclosures tests passed successfully.")
sys.exit(0)
