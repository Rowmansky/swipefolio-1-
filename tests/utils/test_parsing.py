import json
import pytest
from pathlib import Path
from fmp_fetcher.utils.parsing import parse_esg_historical

FIXTURE_DIR = Path(__file__).parent.parent / 'fixtures'

@pytest.mark.parametrize(
    "fixture_file, source, expected_year, expected_report_date, expected_grade",
    [
        ('esg_disclosures.json', 'FMP ESG Disclosures', 2024, '2024-12-28', None),
        ('esg_ratings.json', 'FMP ESG Ratings', 2024, '2024-12-31', 'B'),
    ]
)
def test_parse_esg_historical(fixture_file, source, expected_year, expected_report_date, expected_grade):
    # Load fixture
    fixture_path = FIXTURE_DIR / fixture_file
    data_list = json.loads(fixture_path.read_text())
    api_data = data_list[0]
    # Invoke parser
    parsed = parse_esg_historical(api_data, symbol='AAPL', source=source)
    assert parsed is not None
    assert parsed['symbol'] == 'AAPL'
    assert parsed['calendar_year'] == expected_year
    assert parsed['report_date'] == expected_report_date
    assert parsed['esg_score'] is not None
    # Check rating grade for ratings fixture, None for disclosures
    assert parsed['esg_rating_grade'] == expected_grade
