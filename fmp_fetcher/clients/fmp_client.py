# fmp_fetcher/clients/fmp_client.py
"""
Simple, resilient helper for talking to the FMP REST API.

* Automatic retries with back‑off
* Optional CSV handling (for the “‑bulk” endpoints)
* Centralised logging

Environment / config values are imported from fmp_fetcher.config
"""
from __future__ import annotations

import io
import csv
import time
import logging
from typing import Any, Dict, List, Optional, Union

import requests

from ..config import (
    FMP_BASE_URL,
    get_fmp_api_key,
    DEFAULT_TIMEOUT,
    RETRY_ATTEMPTS,
    RETRY_DELAY_SECONDS,
)

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Main helper
# --------------------------------------------------------------------------- #
def make_fmp_request(
    endpoint_path: str,
    params: Optional[Dict[str, Any]] = None,
    *,
    handle_csv: bool = False,
) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
    """
    Call an FMP endpoint and return a python object.

    If *handle_csv* is True the function will treat the payload as CSV and
    return `List[Dict[str, str]]`.  Otherwise it will try to decode JSON.

    On any hard failure (network, 5xx, decode error) **None** is returned so
    the calling task can decide what to do.
    """
    params = params or {}
    params["apikey"] = get_fmp_api_key()

    url: str = FMP_BASE_URL.rstrip("/") + endpoint_path

    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            logger.debug("Requesting %s with %s (attempt %d)", url, params, attempt)
            response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()  # raise on 4xx / 5xx

            # ----------------------------------------------------------------
            # 1)  CSV FIRST  (this is the critical change)
            # ----------------------------------------------------------------
            if not handle_csv:
                logger.debug("FMP RAW TEXT for %s: %s", url, response.text)
            if handle_csv:
                logger.debug("Parsing CSV payload")
                reader = csv.DictReader(io.StringIO(response.text))
                return [row for row in reader]

            # ----------------------------------------------------------------
            # 2)  otherwise: JSON
            # ----------------------------------------------------------------
            return response.json()

        except requests.exceptions.RequestException as ex:
            logger.warning(
                "Network/API error calling %s (attempt %d/%d): %s",
                url,
                attempt,
                RETRY_ATTEMPTS,
                ex,
            )
        except ValueError:
            # JSON decode failure (or any other `response.json()` error)
            # If we’re *supposed* to parse CSV we would already have handled
            # that, so this really is a bad payload.
            logger.error(
                "Failed to decode JSON from %s. First 200 chars: %s…",
                url,
                response.text[:200],
            )
            return None

        # Back‑off between retries
        if attempt < RETRY_ATTEMPTS:
            time.sleep(RETRY_DELAY_SECONDS)

    logger.error("Giving up after %d attempts calling %s", RETRY_ATTEMPTS, url)
    return None
