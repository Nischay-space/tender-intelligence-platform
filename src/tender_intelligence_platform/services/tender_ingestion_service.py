import logging

from sqlalchemy.orm import Session

from tender_intelligence_platform.engines.link_prefilter import (
    LinkPreFilter,
)
from tender_intelligence_platform.models.ingestion_result import (
    IngestionFailure,
    IngestionResult,
    IngestionSkip,
)
from tender_intelligence_platform.repositories.tender_evaluation_repository import (
    TenderEvaluationRepository,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)
from tender_intelligence_platform.scrapers.cppp_scraper import (
    CPPPScraper,
)
from tender_intelligence_platform.services.tender_evaluation_service import (
    TenderEvaluationService,
)


logger = logging.getLogger(__name__)


class TenderIngestionService:
    """Orchestrates tender scraping, evaluation, and persistence."""

    def __init__(
        self,
        scraper: CPPPScraper,
        repository: TenderRepository,
        evaluation_repository: TenderEvaluationRepository,
        evaluation_service: TenderEvaluationService,
        session: Session,
        link_prefilter: LinkPreFilter | None = None,
    ):
        self._scraper = scraper
        self._repository = repository
        self._evaluation_repository = evaluation_repository
        self._evaluation_service = evaluation_service
        self._session = session
        self._link_prefilter = link_prefilter

    def ingest(self) -> IngestionResult:
        """
        Scrape, evaluate, persist, and report tender ingestion.
        """

        logger.info(
            "Tender ingestion started"
        )

        links = self._scraper.scrape_homepage()

        result = IngestionResult(
            discovered=len(links)
        )

        logger.info(
            "Discovered %d tender links",
            result.discovered,
        )

        for link in links:
            if self._link_prefilter is not None:
                prefilter_result = self._link_prefilter.should_skip(
                    link
                )

                if prefilter_result.should_skip:
                    result.skipped += 1

                    result.skips.append(
                        IngestionSkip(
                            tender_reference_number=(
                                link.reference_number
                            ),
                            reason=prefilter_result.reason,
                        )
                    )

                    logger.info(
                        "Tender skipped by pre-filter: %s | reason=%s",
                        link.reference_number,
                        prefilter_result.reason,
                    )

                    continue

            try:
                with self._session.begin_nested():

                    # ---------------------------------------------
                    # Stage 1: Scrape tender detail
                    # ---------------------------------------------

                    tender = self._scraper.scrape_detail(
                        link
                    )

                    # ---------------------------------------------
                    # Stage 2: Evaluate tender
                    # ---------------------------------------------

                    evaluation = (
                        self._evaluation_service.evaluate(
                            tender
                        )
                    )

                    logger.info(
                        "Tender evaluated: %s | status=%s",
                        tender.tender_id,
                        evaluation.status,
                    )

                    # ---------------------------------------------
                    # Stage 3: Persist tender
                    # ---------------------------------------------

                    tender_orm = self._repository.upsert(
                        tender
                    )

                    # ---------------------------------------------
                    # Stage 4: Persist evaluation
                    # ---------------------------------------------

                    self._evaluation_repository.upsert(
                        tender_orm.id,
                        evaluation,
                    )

                result.tenders.append(
                    tender
                )

                result.successful += 1

                logger.info(
                    "Tender processed successfully: %s | status=%s",
                    tender.tender_id,
                    evaluation.status,
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