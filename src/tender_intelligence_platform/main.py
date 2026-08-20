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
    """Run one complete tender ingestion cycle."""

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

        ingestion_service = TenderIngestionService(
            scraper=scraper,
            repository=tender_repository,
            evaluation_repository=evaluation_repository,
            evaluation_service=evaluation_service,
            session=session,
        )

        try:
            result = ingestion_service.ingest()

            session.commit()

            return result

        except Exception:
            session.rollback()
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

    if result.failed:
        print(
            f"Failed tenders: {result.failed}"
        )


if __name__ == "__main__":
    main()