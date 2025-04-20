"""
Temporary environment configuration for testing
"""
import os

# Replace these with your actual API keys for testing
os.environ["FMP_API_KEY"] = "69qQMNBueqOq5EQHCnlHHA6GGESc1LQy"
os.environ["SUPABASE_URL"] = "https://fzluwxuxvegdonfumsnz.supabase.co"
os.environ["SUPABASE_SERVICE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ6bHV3eHV4dmVnZG9uZnVtc256Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDY5NTcyNywiZXhwIjoyMDYwMjcxNzI3fQ.3TL-wDiT8qq0ODUnVwth3Dl9paUP3xjjZMhAwu1B488"

# Test with a diverse set of stocks across different sectors
TEST_SYMBOLS = [
    "AAPL",  # Technology - Apple
    "MSFT",  # Technology - Microsoft
    "GOOGL", # Technology - Alphabet (Google)
    "AMZN",  # Consumer Discretionary - Amazon
    "JPM",   # Financial - JPMorgan Chase
    "JNJ",   # Healthcare - Johnson & Johnson
    "PG",    # Consumer Staples - Procter & Gamble
    "XOM",   # Energy - Exxon Mobil
    "DIS",   # Communication Services - Disney
    "CAT"    # Industrials - Caterpillar
]
