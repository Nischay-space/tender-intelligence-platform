from unittest.mock import MagicMock

from tender_intelligence_platform.models.ingestion_result import (
    IngestionResult,
)
from tender_intelligence_platform.services.tender_ingestion_service import (
    TenderIngestionService,
)


def test_ingestion_service_returns_successful_tenders():
    scraper = MagicMock()
    repository = MagicMock()
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

    savepoint = MagicMock()

    session.begin_nested.return_value = savepoint
    savepoint.__enter__.return_value = savepoint

    service = TenderIngestionService(
        scraper,
        repository,
        session,
    )

    result = service.ingest()

    assert isinstance(
        result,
        IngestionResult,
    )

    assert result.discovered == 2
    assert result.successful == 2
    assert result.failed == 0

    assert len(result.tenders) == 2
    assert len(result.failures) == 0

    assert repository.upsert.call_count == 2


def test_ingestion_service_isolates_failed_tender():
    scraper = MagicMock()
    repository = MagicMock()
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

    savepoint = MagicMock()

    session.begin_nested.return_value = savepoint
    savepoint.__enter__.return_value = savepoint

    service = TenderIngestionService(
        scraper,
        repository,
        session,
    )

    result = service.ingest()

    assert result.discovered == 3
    assert result.successful == 2
    assert result.failed == 1

    assert len(result.tenders) == 2
    assert len(result.failures) == 1

    assert (
        result.failures[0].tender_reference_number
        == "REF-002"
    )

    assert (
        result.failures[0].error
        == "Parser failed"
    )

    assert repository.upsert.call_count == 2