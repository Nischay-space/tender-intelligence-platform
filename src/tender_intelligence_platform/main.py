from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.config.settings import settings
from tender_intelligence_platform.core.logging import configure_logging
from tender_intelligence_platform.database.connection import SessionLocal
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)
from tender_intelligence_platform.scrapers.cppp_scraper import CPPPScraper
from tender_intelligence_platform.services.tender_ingestion_service import (
    TenderIngestionService,
)


def main():
    configure_logging()

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
        )

        try:
            result = ingestion_service.ingest()

            session.commit()

        except Exception:
            session.rollback()
            raise

    print(
        f"Successfully ingested "
        f"{result.successful}/{result.discovered} tenders"
    )


if __name__ == "__main__":
    main()