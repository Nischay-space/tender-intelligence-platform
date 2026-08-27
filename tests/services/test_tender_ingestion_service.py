from unittest.mock import MagicMock

from tender_intelligence_platform.models.evaluation_result import (
    EvaluationResult,
)
from tender_intelligence_platform.models.filter_result import (
    FilterResult,
)
from tender_intelligence_platform.models.eligibility_result import (
    EligibilityResult,
)
from tender_intelligence_platform.models.prefilter_result import (
    PreFilterResult,
)
from tender_intelligence_platform.services.tender_ingestion_service import (
    TenderIngestionService,
)


def create_evaluation(
    status: str = "QUALIFIED",
) -> EvaluationResult:

    return EvaluationResult(
        status=status,
        keyword_result=FilterResult(
            is_relevant=status != "FILTERED_OUT",
            matched_keywords=["construction"]
            if status != "FILTERED_OUT"
            else [],
            excluded_keywords=[],
            reasons=[],
        ),
        eligibility_result=EligibilityResult(
            status=(
                "ELIGIBLE"
                if status == "QUALIFIED"
                else "NOT_ELIGIBLE"
            ),
            passed_rules=[],
            failed_rules=[],
            unknown_rules=[],
            reasons=[],
        ),
        reasons=[
            f"Final evaluation status: {status}"
        ],
    )


def test_ingestion_service_returns_successful_tenders():

    scraper = MagicMock()
    repository = MagicMock()
    evaluation_repository = MagicMock()
    evaluation_service = MagicMock()
    session = MagicMock()

    link_1 = MagicMock()
    link_1.reference_number = "REF-001"

    link_2 = MagicMock()
    link_2.reference_number = "REF-002"

    tender_1 = MagicMock()
    tender_1.tender_id = "TENDER-001"

    tender_2 = MagicMock()
    tender_2.tender_id = "TENDER-002"

    scraper.scrape_homepage.return_value = [
        link_1,
        link_2,
    ]

    scraper.scrape_detail.side_effect = [
        tender_1,
        tender_2,
    ]

    evaluation_service.evaluate.side_effect = [
        create_evaluation("QUALIFIED"),
        create_evaluation("NOT_ELIGIBLE"),
    ]

    savepoint = MagicMock()

    session.begin_nested.return_value = savepoint
    savepoint.__enter__.return_value = savepoint

    service = TenderIngestionService(
        scraper,
        repository,
        evaluation_repository,
        evaluation_service,
        session,
    )

    result = service.ingest()

    assert result.discovered == 2
    assert result.successful == 2
    assert result.failed == 0

    assert len(result.tenders) == 2

    assert evaluation_service.evaluate.call_count == 2

    assert evaluation_repository.upsert.call_count == 2

    assert repository.upsert.call_count == 2


def test_ingestion_service_isolates_failed_tender():

    scraper = MagicMock()
    repository = MagicMock()
    evaluation_repository = MagicMock()
    evaluation_service = MagicMock()
    session = MagicMock()

    link_1 = MagicMock()
    link_1.reference_number = "REF-001"

    link_2 = MagicMock()
    link_2.reference_number = "REF-002"

    link_3 = MagicMock()
    link_3.reference_number = "REF-003"

    tender_1 = MagicMock()
    tender_1.tender_id = "TENDER-001"

    tender_3 = MagicMock()
    tender_3.tender_id = "TENDER-003"

    scraper.scrape_homepage.return_value = [
        link_1,
        link_2,
        link_3,
    ]

    scraper.scrape_detail.side_effect = [
        tender_1,
        RuntimeError("Parser failed"),
        tender_3,
    ]

    evaluation_service.evaluate.side_effect = [
        create_evaluation("QUALIFIED"),
        create_evaluation("QUALIFIED"),
    ]

    savepoint = MagicMock()

    session.begin_nested.return_value = savepoint
    savepoint.__enter__.return_value = savepoint

    service = TenderIngestionService(
        scraper,
        repository,
        evaluation_repository,
        evaluation_service,
        session,
    )

    result = service.ingest()

    assert result.discovered == 3
    assert result.successful == 2
    assert result.failed == 1

    assert len(result.tenders) == 2
    assert len(result.failures) == 1

    assert result.failures[0].tender_reference_number == (
        "REF-002"
    )

    assert repository.upsert.call_count == 2
    assert evaluation_repository.upsert.call_count == 2


def test_ingestion_service_skips_link_rejected_by_prefilter():

    scraper = MagicMock()
    repository = MagicMock()
    evaluation_repository = MagicMock()
    evaluation_service = MagicMock()
    session = MagicMock()
    link_prefilter = MagicMock()

    link_1 = MagicMock()
    link_1.reference_number = "REF-001"

    link_2 = MagicMock()
    link_2.reference_number = "REF-002"

    tender_1 = MagicMock()
    tender_1.tender_id = "TENDER-001"

    scraper.scrape_homepage.return_value = [
        link_1,
        link_2,
    ]

    scraper.scrape_detail.side_effect = [
        tender_1,
    ]

    evaluation_service.evaluate.side_effect = [
        create_evaluation("QUALIFIED"),
    ]

    link_prefilter.should_skip.side_effect = [
        PreFilterResult(should_skip=False),
        PreFilterResult(
            should_skip=True,
            reason="Title matched exclude keyword: highway",
        ),
    ]

    savepoint = MagicMock()

    session.begin_nested.return_value = savepoint
    savepoint.__enter__.return_value = savepoint

    service = TenderIngestionService(
        scraper,
        repository,
        evaluation_repository,
        evaluation_service,
        session,
        link_prefilter=link_prefilter,
    )

    result = service.ingest()

    assert result.discovered == 2
    assert result.successful == 1
    assert result.failed == 0
    assert result.skipped == 1

    assert len(result.skips) == 1
    assert result.skips[0].tender_reference_number == "REF-002"
    assert "highway" in result.skips[0].reason.lower()

    # skipped link never reaches the expensive detail scrape
    assert scraper.scrape_detail.call_count == 1