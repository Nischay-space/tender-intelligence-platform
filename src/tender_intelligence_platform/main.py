from pathlib import Path

from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.config.settings import settings
from tender_intelligence_platform.core.logging import configure_logging
from tender_intelligence_platform.database.connection import SessionLocal
from tender_intelligence_platform.engines.eligibility_engine import (
    EligibilityEngine,
)
from tender_intelligence_platform.engines.keyword_engine import (
    KeywordEngine,
)
from tender_intelligence_platform.engines.link_prefilter import (
    LinkPreFilter,
)
from tender_intelligence_platform.repositories.ingestion_run_repository import (
    IngestionRunRepository,
)
from tender_intelligence_platform.repositories.tender_evaluation_repository import (
    TenderEvaluationRepository,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)
from tender_intelligence_platform.scrapers.cppp_scraper import CPPPScraper
from tender_intelligence_platform.services.tender_evaluation_service import (
    TenderEvaluationService,
)
from tender_intelligence_platform.services.tender_ingestion_service import (
    TenderIngestionService,
)


# ---------------------------------------------------------
# Configuration paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

KEYWORD_CONFIG_PATH = (
    PROJECT_ROOT
    / "config"
    / "filters.yaml"
)

ELIGIBILITY_CONFIG_PATH = (
    PROJECT_ROOT
    / "config"
    / "eligibility.yaml"
)


# ---------------------------------------------------------
# Dependency construction
# ---------------------------------------------------------


def build_keyword_engine() -> KeywordEngine:
    """Create the configured keyword engine."""

    return KeywordEngine(
        config_path=KEYWORD_CONFIG_PATH,
    )


def build_link_prefilter() -> LinkPreFilter:
    """Create the configured pre-download link filter."""

    return LinkPreFilter(
        config_path=KEYWORD_CONFIG_PATH,
    )


def build_eligibility_engine() -> EligibilityEngine:
    """Create the configured eligibility engine."""

    return EligibilityEngine(
        config_path=ELIGIBILITY_CONFIG_PATH,
    )


def build_evaluation_service() -> TenderEvaluationService:
    """Create the tender evaluation service."""

    keyword_engine = build_keyword_engine()
    eligibility_engine = build_eligibility_engine()

    return TenderEvaluationService(
        keyword_engine=keyword_engine,
        eligibility_engine=eligibility_engine,
    )


# ---------------------------------------------------------
# Ingestion
# ---------------------------------------------------------


def ingest_once():
    """Run one complete tender ingestion cycle, recording its outcome."""

    # Run tracking deliberately uses its own short-lived sessions,
    # separate from the ingestion session below. If ingestion fails
    # catastrophically and its session is rolled back, the run record
    # documenting that failure must still be persisted, not undone
    # along with it.
    with SessionLocal() as run_session:
        run_repository = IngestionRunRepository(run_session)
        run = run_repository.start_run()
        run_session.commit()
        run_id = run.id

    client = HTTPClient()

    keyword_engine = build_keyword_engine()
    eligibility_engine = build_eligibility_engine()

    evaluation_service = TenderEvaluationService(
        keyword_engine=keyword_engine,
        eligibility_engine=eligibility_engine,
    )

    with SessionLocal() as session:

        tender_repository = TenderRepository(
            session
        )

        evaluation_repository = TenderEvaluationRepository(
            session
        )

        scraper = CPPPScraper(
            client,
            settings,
        )

        link_prefilter = build_link_prefilter()

        ingestion_service = TenderIngestionService(
            scraper=scraper,
            repository=tender_repository,
            evaluation_repository=evaluation_repository,
            evaluation_service=evaluation_service,
            session=session,
            link_prefilter=link_prefilter,
        )

        try:
            result = ingestion_service.ingest()

            session.commit()

            with SessionLocal() as run_session:
                IngestionRunRepository(run_session).complete_run(
                    run_id,
                    discovered=result.discovered,
                    successful=result.successful,
                    failed=result.failed,
                    skipped=result.skipped,
                )
                run_session.commit()

            return result

        except Exception as exc:
            session.rollback()

            with SessionLocal() as run_session:
                IngestionRunRepository(run_session).fail_run(
                    run_id,
                    error=str(exc),
                )
                run_session.commit()

            raise


# ---------------------------------------------------------
# Application entry point
# ---------------------------------------------------------


def main():
    """Run one ingestion cycle."""

    configure_logging()

    result = ingest_once()

    print(
        f"Successfully processed "
        f"{result.successful}/{result.discovered} tenders"
    )

    if result.skipped:
        print(
            f"Skipped by pre-filter: {result.skipped}"
        )

    if result.failed:
        print(
            f"Failed tenders: {result.failed}"
        )


if __name__ == "__main__":
    main()