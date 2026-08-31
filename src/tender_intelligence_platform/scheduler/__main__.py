from tender_intelligence_platform.config.settings import settings
from tender_intelligence_platform.core.logging import configure_logging
from tender_intelligence_platform.scheduler.runner import run_scheduler


def main():
    configure_logging()

    run_scheduler(
        interval_seconds=settings.ingestion_interval_seconds
    )


if __name__ == "__main__":
    main()