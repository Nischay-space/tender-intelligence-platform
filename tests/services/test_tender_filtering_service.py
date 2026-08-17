from unittest.mock import Mock

from tender_intelligence_platform.models.eligibility_result import (
    EligibilityResult,
)
from tender_intelligence_platform.models.filter_result import (
    FilterResult,
)
from tender_intelligence_platform.models.tender import Tender
from tender_intelligence_platform.services.tender_filtering_service import (
    TenderFilteringService,
)


def create_tender() -> Tender:
    """Create a minimal tender for filtering tests."""

    return Tender(
        tender_id="TEST-001",
        tender_title="Construction of office building",
        organization="Test Organization",
        tender_reference_number="TEST-REF-001",
        tender_url="https://example.com/tender",
        published_date=None,
        bid_submission_start_date=None,
        bid_submission_end_date=None,
        opening_date=None,
        estimated_value=5_000_000,
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
        work_description="Civil works and renovation",
    )


def test_relevant_and_eligible_tender_is_accepted():
    keyword_engine = Mock()

    keyword_engine.evaluate.return_value = FilterResult(
        is_relevant=True,
        matched_keywords=[
            "construction",
            "civil works",
        ],
        reasons=[
            "Matched keywords: construction, civil works"
        ],
    )

    eligibility_engine = Mock()

    eligibility_engine.evaluate.return_value = EligibilityResult(
        status="ELIGIBLE",
        reasons=[
            "All eligibility rules passed"
        ],
    )

    service = TenderFilteringService(
        keyword_engine,
        eligibility_engine,
    )

    result = service.evaluate(
        create_tender()
    )

    assert result.status == "ACCEPTED"
    assert result.is_accepted is True
    assert result.requires_review is False

    keyword_engine.evaluate.assert_called_once()
    eligibility_engine.evaluate.assert_called_once()


def test_irrelevant_tender_is_rejected_before_eligibility():
    keyword_engine = Mock()

    keyword_engine.evaluate.return_value = FilterResult(
        is_relevant=False,
        matched_keywords=[],
        reasons=[
            "No configured keywords matched"
        ],
    )

    eligibility_engine = Mock()

    service = TenderFilteringService(
        keyword_engine,
        eligibility_engine,
    )

    result = service.evaluate(
        create_tender()
    )

    assert result.status == "REJECTED_KEYWORD"
    assert result.is_accepted is False

    keyword_engine.evaluate.assert_called_once()

    eligibility_engine.evaluate.assert_not_called()

    assert result.eligibility_result is None


def test_relevant_but_ineligible_tender_is_rejected():
    keyword_engine = Mock()

    keyword_engine.evaluate.return_value = FilterResult(
        is_relevant=True,
        matched_keywords=[
            "construction"
        ],
        reasons=[
            "Matched keywords: construction"
        ],
    )

    eligibility_engine = Mock()

    eligibility_engine.evaluate.return_value = EligibilityResult(
        status="NOT_ELIGIBLE",
        reasons=[
            "Minimum tender value rule failed"
        ],
    )

    service = TenderFilteringService(
        keyword_engine,
        eligibility_engine,
    )

    result = service.evaluate(
        create_tender()
    )

    assert result.status == "REJECTED_ELIGIBILITY"
    assert result.is_accepted is False

    keyword_engine.evaluate.assert_called_once()
    eligibility_engine.evaluate.assert_called_once()


def test_unknown_eligibility_requires_review():
    keyword_engine = Mock()

    keyword_engine.evaluate.return_value = FilterResult(
        is_relevant=True,
        matched_keywords=[
            "construction"
        ],
        reasons=[
            "Matched keywords: construction"
        ],
    )

    eligibility_engine = Mock()

    eligibility_engine.evaluate.return_value = EligibilityResult(
        status="UNKNOWN",
        reasons=[
            "Required field is missing"
        ],
    )

    service = TenderFilteringService(
        keyword_engine,
        eligibility_engine,
    )

    result = service.evaluate(
        create_tender()
    )

    assert result.status == "REVIEW_REQUIRED"
    assert result.is_accepted is False
    assert result.requires_review is True

    keyword_engine.evaluate.assert_called_once()
    eligibility_engine.evaluate.assert_called_once()
    