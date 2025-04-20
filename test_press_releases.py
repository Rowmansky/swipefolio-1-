import logging
import sys
from fmp_fetcher.tasks.news_releases_tasks import fetch_and_store_press_releases

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger("press_releases_test")

def main():
    logger.info("=== Testing press releases ===")
    
    # Test with default limit
    success = fetch_and_store_press_releases()
    
    logger.info(f"Press releases test completed: {success}")
    
    if success:
        logger.info("✅ Press releases successfully fetched and stored!")
    else:
        logger.info("❌ Press releases fetch failed!")
    
    return success

if __name__ == "__main__":
    result = main()
    # Exit with appropriate code for automation
    sys.exit(0 if result else 1)
