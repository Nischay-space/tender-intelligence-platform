import logging

from sqlalchemy.orm import Session

from tender_intelligence_platform.models.ingestion_result import (
    IngestionFailure,
    IngestionResult,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)
from tender_intelligence_platform.scrapers.cppp_scraper import CPPPScraper


logger = logging.getLogger(__name__)


class TenderIngestionService:
    """Orchestrates tender scraping and persistence."""

    def __init__(
        self,
        scraper: CPPPScraper,
        repository: TenderRepository,
        session: Session,
    ):
        self._scraper = scraper
        self._repository = repository
        self._session = session

    def ingest(self) -> IngestionResult:
        """Scrape, persist, and report the ingestion result."""

        logger.info("Tender ingestion started")

        links = self._scraper.scrape_homepage()

        result = IngestionResult(
            discovered=len(links)
        )

        logger.info(
            "Discovered %d tender links",
            result.discovered,
        )

        for link in links:
            try:
                with self._session.begin_nested():
                    tender = self._scraper.scrape_detail(link)

                    self._repository.upsert(tender)

                result.tenders.append(tender)
                result.successful += 1

                logger.info(
                    "Tender processed successfully: %s",
                    tender.tender_id,
                )

            except Exception as exc:
                result.failed += 1

                result.failures.append(
                    IngestionFailure(
                        tender_reference_number=(
                            link.reference_number
                        ),
                        error=str(exc),
                    )
                )

                logger.exception(
                    "Failed to process tender: %s",
                    link.reference_number,
                )

        logger.info(
            "Tender ingestion completed | "
            "discovered=%d successful=%d failed=%d",
            result.discovered,
            result.successful,
            result.failed,
        )

        return result