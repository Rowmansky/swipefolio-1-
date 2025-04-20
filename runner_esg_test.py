#!/usr/bin/env python3
"""
Standalone test runner for ESG tasks without pytest.
Usage: python runner_esg_test.py
"""
import logging
import sys
import json
from pathlib import Path

from fmp_fetcher.tasks.esg_tasks import fetch_and_store_esg_scores
from fmp_fetcher.clients import fmp_client, db_client

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

# Fixture directory
FIXTURE_DIR = Path(__file__).parent / 'tests' / 'fixtures'

def load_fixture(name):
    path = FIXTURE_DIR / name
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"❌ Failed to load fixture {name}: {e}")
        sys.exit(1)

# Test 1: Valid data
print("Running ESG task tests with valid fixture data...")
disclosures = load_fixture('esg_disclosures.json')
ratings = load_fixture('esg_ratings.json')

# Stub FMP client
original_make = fmp_client.make_fmp_request
captured = []

def fake_make_request(endpoint_path, params):
    if 'disclosures' in endpoint_path:
        return disclosures
    if 'ratings' in endpoint_path:
        return ratings
    return []

fmp_client.make_fmp_request = fake_make_request

# Stub DB client
original_update = db_client.update_esg_scores_historical
def fake_update(data):
    captured.extend(data)
    return True

db_client.update_esg_scores_historical = fake_update

# Run
fetch_and_store_esg_scores(['AAPL'])
expected_count = len(disclosures)
if len(captured) != expected_count:
    print(f"❌ Test failed: expected {expected_count} records, got {len(captured)}")
    sys.exit(1)
print(f"✅ Valid data test passed: {len(captured)} records upserted.")
for rec in captured:
    # Ensure numeric scores present and rating grade merged
    assert rec['esg_score'] is not None, "Missing esg_score"
    assert rec['environmental_score'] is not None, "Missing environmental_score"
    assert rec['social_score'] is not None, "Missing social_score"
    assert rec['governance_score'] is not None, "Missing governance_score"
    assert rec.get('esg_rating_grade') == 'B', f"Expected rating 'B', got {rec.get('esg_rating_grade')}"
    assert rec.get('data_source') == 'FMP ESG Disclosures', f"Unexpected data_source {rec.get('data_source')}"

# Test 2: No data
print("Running ESG task tests with empty data...")
captured.clear()
# Stub FMP client to accept any args/kwargs
fmp_client.make_fmp_request = lambda *args, **kwargs: []

fetch_and_store_esg_scores(['AAPL'])
if captured:
    print(f"❌ Test failed: expected 0 records, got {len(captured)}")
    sys.exit(1)
print("✅ No data test passed: no records upserted.")

# Cleanup stubs
fmp_client.make_fmp_request = original_make
db_client.update_esg_scores_historical = original_update

print("All ESG tests passed successfully.")
sys.exit(0)
