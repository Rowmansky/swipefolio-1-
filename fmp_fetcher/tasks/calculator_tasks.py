# fmp_fetcher/tasks/calculator_tasks.py
import logging
from typing import List, Dict, Any

from ..clients import db_client
from ..calculator import calculate_metrics

logger = logging.getLogger(__name__)


def calculate_and_store_derived_metrics(symbols: List[str]):
    """Calculates derived financial metrics for the given symbols based on data
    already stored in the database, and upserts into the 'calculated_metrics' table.
    
    This task should run after all dependent data has been fetched in the same job.

    Args:
        symbols: A list of stock symbols to calculate metrics for.
    """
    if not symbols:
        logger.warning("No symbols provided to calculate_and_store_derived_metrics. Skipping.")
        return

    logger.info(f"Starting derived metrics calculation for {len(symbols)} symbols.")

    all_calculated_metrics = []
    has_errors = False

    for symbol in symbols:
        try:
            logger.debug(f"Calculating derived metrics for symbol: {symbol}")
            
            # Call calculator functions to calculate metrics
            calculated_values = calculate_metrics(symbol)
            
            if not calculated_values:
                logger.warning(f"No metrics could be calculated for {symbol}. Skipping symbol.")
                continue
                
            all_calculated_metrics.append(calculated_values)
            
        except Exception as e:
            logger.exception(f"Error calculating derived metrics for {symbol}: {e}")
            has_errors = True
            # Continue with other symbols even if one fails

    # --- Store Data ---    
    if not all_calculated_metrics:
        logger.warning(f"No derived metrics could be calculated for the target symbols.")
        # Still log finish status even if nothing to upsert
    else:
        logger.info(f"Attempting to upsert a total of {len(all_calculated_metrics)} calculated metric records...")
        success = db_client.update_calculated_metrics(all_calculated_metrics)

        if success:
            logger.info(f"Successfully upserted {len(all_calculated_metrics)} calculated metric records.")
        else:
            logger.error(f"Failed to upsert calculated metric records.")

    log_level = logging.WARNING if has_errors else logging.INFO
    logger.log(log_level, f"Finished derived metrics calculation for {len(symbols)} requested symbols. Encountered errors: {has_errors}")
