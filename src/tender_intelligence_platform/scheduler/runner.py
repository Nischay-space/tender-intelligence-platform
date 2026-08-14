import logging
import time

from tender_intelligence_platform.main import ingest_once


logger = logging.getLogger(__name__)


def run_scheduler(interval_seconds: int = 900) -> None:
    """
    Run tender ingestion repeatedly.

    Args:
        interval_seconds: Time between ingestion runs.
    """

    logger.info(
        "Scheduler started | interval=%d seconds",
        interval_seconds,
    )

    while True:
        try:
            logger.info("Starting scheduled ingestion")

            result = ingest_once()

            logger.info(
                "Scheduled ingestion completed | "
                "discovered=%d successful=%d failed=%d",
                result.discovered,
                result.successful,
                result.failed,
            )

        except Exception:
            logger.exception(
                "Scheduled ingestion failed"
            )

        logger.info(
            "Waiting %d seconds until next run",
            interval_seconds,
        )

        time.sleep(interval_seconds)