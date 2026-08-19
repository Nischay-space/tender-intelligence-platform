import logging

from sqlalchemy.orm import Session

from tender_intelligence_platform.engines.eligibility_engine import (
    EligibilityEngine,
)
from tender_intelligence_platform.engines.keyword_engine import (
    KeywordEngine,
)
from tender_intelligence_platform.models.ingestion_result import (
    IngestionFailure,
    IngestionResult,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)
from tender_intelligence_platform.scrapers.cppp_scraper import (
    CPPPScraper,
)


logger = logging.getLogger(__name__)


class TenderIngestionService:
    """Orchestrates tender scraping, filtering, eligibility, and persistence."""

    def __init__(
        self,
        scraper: CPPPScraper,
        repository: TenderRepository,
        session: Session,
        keyword_engine: KeywordEngine,
        eligibility_engine: EligibilityEngine,
    ):
        self._scraper = scraper
        self._repository = repository
        self._session = session
        self._keyword_engine = keyword_engine
        self._eligibility_engine = eligibility_engine

    def ingest(self) -> IngestionResult:
        """Scrape, filter, evaluate eligibility, persist, and report."""

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

                    # -------------------------------------------------
                    # Stage 1: Keyword relevance filtering
                    # -------------------------------------------------

                    keyword_result = (
                        self._keyword_engine.evaluate(
                            tender
                        )
                    )

                    if not keyword_result.is_relevant:
                        logger.info(
                            "Tender filtered by keyword engine: %s | reasons=%s",
                            tender.tender_id,
                            keyword_result.reasons,
                        )
                        continue

                    # -------------------------------------------------
                    # Stage 2: Eligibility evaluation
                    # -------------------------------------------------

                    eligibility_result = (
                        self._eligibility_engine.evaluate(
                            tender
                        )
                    )

                    if eligibility_result.status != "ELIGIBLE":
                        logger.info(
                            "Tender rejected by eligibility engine: "
                            "%s | status=%s | reasons=%s",
                            tender.tender_id,
                            eligibility_result.status,
                            eligibility_result.reasons,
                        )
                        continue

                    # -------------------------------------------------
                    # Stage 3: Persist eligible tender
                    # -------------------------------------------------

                    self._repository.upsert(
                        tender
                    )

                result.tenders.append(
                    tender
                )
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