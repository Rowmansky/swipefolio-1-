import json
import pytest
from pathlib import Path

import fmp_fetcher.tasks.esg_tasks as esg_tasks
from fmp_fetcher.clients import fmp_client, db_client

FIXTURE_DIR = Path(__file__).parent.parent / 'fixtures'

@ pytest.fixture(autouse=True)
def clear_monkeypatch(monkeypatch):
    # Ensure stubbed calls don't leak
    yield


def test_fetch_and_store_esg_scores_success(monkeypatch, caplog):
    caplog.set_level('INFO')
    # Load fixtures
    discl = json.loads((FIXTURE_DIR / 'esg_disclosures.json').read_text())
    ratings = json.loads((FIXTURE_DIR / 'esg_ratings.json').read_text())

    # Stub FMP client
    def fake_make_request(endpoint_path, params):
        if 'disclosures' in endpoint_path:
            return discl
        elif 'ratings' in endpoint_path:
            return ratings
        return []

    monkeypatch.setattr(fmp_client, 'make_fmp_request', fake_make_request)

    # Capture DB upsert
    captured = {}
    def fake_update(data):
        captured['data'] = data
        return True

    monkeypatch.setattr(db_client, 'update_esg_scores_historical', fake_update)

    # Run task
    esg_tasks.fetch_and_store_esg_scores(['AAPL'])

    # Verify upsert called with two records
    assert 'data' in captured
    upserted = captured['data']
    assert isinstance(upserted, list)
    # One from disclosures, one from ratings
    assert len(upserted) == 2

    # Validate fields
    data_sources = {rec['data_source'] for rec in upserted}
    assert data_sources == {'FMP ESG Disclosures', 'FMP ESG Ratings'}
    for rec in upserted:
        assert rec['symbol'] == 'AAPL'
        assert rec['report_date'] is not None
        assert 'esg_score' in rec


def test_fetch_and_store_esg_scores_no_data(monkeypatch, caplog):
    caplog.set_level('WARNING')
    # Both endpoints return empty
    monkeypatch.setattr(fmp_client, 'make_fmp_request', lambda *args, **kwargs: [])
    called = False
    def fake_update(data):
        nonlocal called
        called = True
        return True
    monkeypatch.setattr(db_client, 'update_esg_scores_historical', fake_update)

    esg_tasks.fetch_and_store_esg_scores(['AAPL'])
    # Should warn and not call update
    assert not called
    assert "No valid ESG score records" in caplog.text
