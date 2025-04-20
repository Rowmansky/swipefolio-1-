# run_dcf.py
import os
from dotenv import load_dotenv

# load .env into os.environ
load_dotenv()

from fmp_fetcher.tasks.dcf_tasks import fetch_and_store_dcf_valuations

if __name__ == "__main__":
    # list the symbols you want to fetch
    symbols = ["AAPL", "MSFT", "JPM"]
    fetch_and_store_dcf_valuations(symbols)


FMP_API_KEY='69qQMNBueqOq5EQHCnlHHA6GGESc1LQy'
SUPABASE_URL=https://fzluwxuxvegdonfumsnz.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6…
