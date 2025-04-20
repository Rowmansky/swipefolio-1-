import os
from dotenv import load_dotenv
from supabase import create_client, Client
import logging

# Load environment variables from .env file located in the parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=dotenv_path)

FMP_API_KEY = os.getenv("FMP_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") # Using Service Role Key for backend

# FMP Base URL
# --- Ensure this line is in your config.py ---
FMP_BASE_URL = "https://financialmodelingprep.com"  # Base URL; endpoints include '/stable/...'

# Target symbols (Example - move to config file or DB later?)
TARGET_SYMBOLS = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA']

# --- Initialize Supabase Client ---
supabase_client: Client | None = None
try:
    if not all([FMP_API_KEY, SUPABASE_URL, SUPABASE_KEY]):
        raise ValueError("Missing required environment variables (FMP_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY) in .env file")
    
    supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logging.info("Supabase client initialized successfully.")

except ValueError as ve:
    logging.error(f"Configuration error: {ve}")
    # Decide if the application should exit or try to continue without DB/API
    # For this service, it likely needs to exit if basics are missing.
    raise # Re-raise the exception to stop execution if critical config is missing
except Exception as e:
    logging.error(f"Failed to initialize Supabase client: {e}")
    supabase_client = None # Ensure client is None if initialization fails
    raise # Re-raise to indicate critical failure

# --- API Settings ---
DEFAULT_TIMEOUT = 30 # Default timeout for API requests in seconds
RETRY_ATTEMPTS = 3 # Max number of retries for failed API calls
RETRY_DELAY_SECONDS = 5 # Initial delay between retries (will use backoff)


def get_supabase_client() -> Client:
    """Returns the initialized Supabase client."""
    if supabase_client is None:
        # This should ideally not happen if checks are done at startup,
        # but provides a safeguard.
        logging.error("Attempted to get Supabase client, but it was not initialized.")
        raise RuntimeError("Supabase client is not available.")
    return supabase_client

def get_fmp_api_key() -> str:
    """Returns the FMP API Key."""
    if not FMP_API_KEY:
        logging.error("Attempted to get FMP API Key, but it was not loaded.")
        raise RuntimeError("FMP API Key is not available.")
    return FMP_API_KEY
