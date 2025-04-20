import logging
import sys

def setup_logging():
    """Configures basic logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout) # Log to console
            # TODO: Add FileHandler later if needed
            # logging.FileHandler("fmp_fetcher.log")
        ]
    )
    # Optional: Silence noisy libraries if necessary
    # logging.getLogger("requests").setLevel(logging.WARNING)
    # logging.getLogger("urllib3").setLevel(logging.WARNING)

    logging.info("Logging configured.")
