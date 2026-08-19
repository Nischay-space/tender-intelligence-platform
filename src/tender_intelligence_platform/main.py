from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.config.settings import settings
from tender_intelligence_platform.core.logging import configure_logging
from tender_intelligence_platform.database.connection import SessionLocal
from tender_intelligence_platform.engines import eligibility_engine, keyword_engine
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)
from tender_intelligence_platform.scrapers.cppp_scraper import CPPPScraper
from tender_intelligence_platform.services.tender_ingestion_service import (
    TenderIngestionService,
)


def ingest_once():
    """Run one complete tender ingestion cycle."""

    client = HTTPClient()

    with SessionLocal() as session:
        repository = TenderRepository(session)

        scraper = CPPPScraper(
            client,
            settings,
        )

        ingestion_service = TenderIngestionService(
            scraper,
            repository,
            session,
            keyword_engine,
            eligibility_engine,
        )

        try:
            result = ingestion_service.ingest()

            session.commit()

            return result

        except Exception:
            session.rollback()
            raise


def main():
    """Run one ingestion cycle."""

    configure_logging()

    result = ingest_once()

    print(
        f"Successfully ingested "
        f"{result.successful}/{result.discovered} tenders"
    )


if __name__ == "__main__":
    main()