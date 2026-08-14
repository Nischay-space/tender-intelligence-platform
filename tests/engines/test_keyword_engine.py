from pathlib import Path

from tender_intelligence_platform.engines.keyword_engine import (
    KeywordEngine,
)
from tender_intelligence_platform.models.tender import Tender


CONFIG_PATH = Path(
    "config/filters.yaml"
)


def create_tender(
    title: str,
    description: str,
) -> Tender:
    """Create a minimal tender for testing."""

    return Tender(
        tender_id="TEST-001",
        tender_title=title,
        organization="Test Organization",
        tender_reference_number="REF-001",
        tender_url="https://example.com/tender",
        published_date=None,
        bid_submission_start_date=None,
        bid_submission_end_date=None,
        opening_date=None,
        estimated_value=None,
        earnest_money_deposit=None,
        tender_fee=None,
        currency="INR",
        tender_type="Open Tender",
        category="Works",
        procurement_type="Works",
        state=None,
        city=None,
        work_location=None,
        status="Open",
        withdrawal_allowed=True,
        form_of_contract=None,
        payment_mode=None,
        work_description=description,
    )


def test_keyword_engine_matches_relevant_tender():
    engine = KeywordEngine(
        CONFIG_PATH
    )

    tender = create_tender(
        title="Construction of office building",
        description="Civil works and renovation",
    )

    result = engine.evaluate(tender)

    assert result.is_relevant is True

    assert "construction" in (
        result.matched_keywords
    )


def test_keyword_engine_rejects_excluded_tender():
    engine = KeywordEngine(
        CONFIG_PATH
    )

    tender = create_tender(
        title="Highway construction work",
        description="Road construction project",
    )

    result = engine.evaluate(tender)

    assert result.is_relevant is False

    assert len(
        result.excluded_keywords
    ) > 0


def test_keyword_engine_rejects_without_matches():
    engine = KeywordEngine(
        CONFIG_PATH
    )

    tender = create_tender(
        title="Supply of office stationery",
        description="Supply of paper and files",
    )

    result = engine.evaluate(tender)

    assert result.is_relevant is False

    assert result.matched_keywords == []