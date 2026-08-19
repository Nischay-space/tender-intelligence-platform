from unittest.mock import MagicMock

from tender_intelligence_platform.models.filter_result import (
    FilterResult,
)
from tender_intelligence_platform.models.eligibility_result import (
    EligibilityResult,
)
from tender_intelligence_platform.models.ingestion_result import (
    IngestionResult,
)
from tender_intelligence_platform.services.tender_ingestion_service import (
    TenderIngestionService,
)


def create_eligible_result():
    """Create a keyword result that allows the tender to continue."""

    return FilterResult(
        is_relevant=True,
        matched_keywords=["construction"],
        excluded_keywords=[],
        reasons=[
            "Matched keywords: construction"
        ],
    )


def create_eligible_status():
    """Create an eligibility result that allows persistence."""

    return EligibilityResult(
        status="ELIGIBLE",
        reasons=[
            "All eligibility rules passed"
        ],
    )


def create_savepoint(session):
    """Configure the nested transaction context."""

    savepoint = MagicMock()

    session.begin_nested.return_value = savepoint
    savepoint.__enter__.return_value = savepoint

    return savepoint


def test_ingestion_service_returns_successful_tenders():
    """Eligible tenders should be persisted successfully."""

    scraper = MagicMock()
    repository = MagicMock()
    session = MagicMock()

    keyword_engine = MagicMock()
    eligibility_engine = MagicMock()

    keyword_engine.evaluate.return_value = (
        create_eligible_result()
    )

    eligibility_engine.evaluate.return_value = (
        create_eligible_status()
    )

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

    create_savepoint(session)

    service = TenderIngestionService(
        scraper,
        repository,
        session,
        keyword_engine,
        eligibility_engine,
    )

    result = service.ingest()

    assert isinstance(
        result,
        IngestionResult,
    )

    assert result.discovered == 2
    assert result.successful == 2
    assert result.failed == 0

    assert result.tenders == [
        tender_1,
        tender_2,
    ]

    assert (
        repository.upsert.call_count
        == 2
    )

    assert (
        keyword_engine.evaluate.call_count
        == 2
    )

    assert (
        eligibility_engine.evaluate.call_count
        == 2
    )


def test_ingestion_service_isolates_failed_tender():
    """A failed tender should not stop other tenders."""

    scraper = MagicMock()
    repository = MagicMock()
    session = MagicMock()

    keyword_engine = MagicMock()
    eligibility_engine = MagicMock()

    keyword_engine.evaluate.return_value = (
        create_eligible_result()
    )

    eligibility_engine.evaluate.return_value = (
        create_eligible_status()
    )

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

    create_savepoint(session)

    service = TenderIngestionService(
        scraper,
        repository,
        session,
        keyword_engine,
        eligibility_engine,
    )

    result = service.ingest()

    assert result.discovered == 3
    assert result.successful == 2
    assert result.failed == 1

    assert result.tenders == [
        tender_1,
        tender_3,
    ]

    assert (
        repository.upsert.call_count
        == 2
    )

    assert (
        keyword_engine.evaluate.call_count
        == 2
    )

    assert (
        eligibility_engine.evaluate.call_count
        == 2
    )

    assert (
        result.failures[0].tender_reference_number
        == "REF-002"
    )

    assert (
        "Parser failed"
        in result.failures[0].error
    )