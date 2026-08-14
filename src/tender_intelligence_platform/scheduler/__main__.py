from tender_intelligence_platform.core.logging import configure_logging
from tender_intelligence_platform.scheduler.runner import run_scheduler


def main():
    configure_logging()

    run_scheduler(
        interval_seconds=900
    )


if __name__ == "__main__":
    main()