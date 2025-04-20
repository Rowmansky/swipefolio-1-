from fmp_fetcher.clients.fmp_client import make_fmp_request
from dotenv import load_dotenv
import os

# —– INJECT YOUR KEY —–
os.environ["FMP_API_KEY"] = "69qQMNBueqOq5EQHCnlHHA6GGESc1LQy"
print("🔑 FMP_API_KEY:", os.environ.get("FMP_API_KEY"))

from dotenv import load_dotenv
load_dotenv()    # fallback if you later get your .env working

from fmp_fetcher.clients.fmp_client import make_fmp_request
for stmt in ("income-statement", "balance-sheet-statement", "cash-flow-statement"):
    print("\n---", stmt, "---")
    try:
        data = make_fmp_request(f"/{stmt}", {"symbol": "AAPL"})
        print("raw response ->", repr(data)[:200], "…")    # first 200 chars
        if isinstance(data, list):
            print("▶ type:", type(data), "len:", len(data))
            print("▶ sample item keys:", list(data[0].keys()) if data else "[]")
        else:
            print("⚠️ not a list:", data)
    except Exception as e:
        print("❌ Exception:", e)
