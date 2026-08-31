import logging
import signal
import threading

from tender_intelligence_platform.main import ingest_once


logger = logging.getLogger(__name__)


_shutdown_event = threading.Event()


def _handle_shutdown_signal(signum, frame):
    logger.info(
        "Shutdown signal received (%s); finishing current cycle then "
        "stopping",
        signal.Signals(signum).name,
    )
    _shutdown_event.set()


def run_scheduler(interval_seconds: int = 900) -> None:
    """
    Run tender ingestion repeatedly until a shutdown signal is received.

    Uses threading.Event.wait() instead of time.sleep() so a shutdown
    signal (Ctrl+C / SIGTERM) interrupts the wait immediately rather
    than blocking until the full interval elapses. Must be called from
    the main thread, since signal.signal() only works there.

    Args:
        interval_seconds: Time between ingestion runs.
    """

    signal.signal(signal.SIGINT, _handle_shutdown_signal)
    signal.signal(signal.SIGTERM, _handle_shutdown_signal)

    logger.info(
        "Scheduler started | interval=%d seconds",
        interval_seconds,
    )

    while not _shutdown_event.is_set():
        try:
            logger.info("Starting scheduled ingestion")

            result = ingest_once()

            logger.info(
                "Scheduled ingestion completed | "
                "discovered=%d successful=%d failed=%d skipped=%d",
                result.discovered,
                result.successful,
                result.failed,
                result.skipped,
            )

        except Exception:
            logger.exception(
                "Scheduled ingestion failed"
            )

        if _shutdown_event.is_set():
            break

        logger.info(
            "Waiting %d seconds until next run",
            interval_seconds,
        )

        _shutdown_event.wait(interval_seconds)

    logger.info("Scheduler stopped")