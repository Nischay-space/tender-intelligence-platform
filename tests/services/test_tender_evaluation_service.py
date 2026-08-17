from unittest.mock import Mock

from tender_intelligence_platform.models.eligibility_result import (
    EligibilityResult,
)
from tender_intelligence_platform.models.filter_result import (
    FilterResult,
)
from tender_intelligence_platform.models.tender import Tender
from tender_intelligence_platform.services.tender_evaluation_service import (
    TenderEvaluationService,
)


def create_tender() -> Tender:
    """Create a minimal valid tender for testing."""

    return Tender(
        tender_id="TEST-001",
        tender_title="Construction of office building",
        organization="Test Organization",
        tender_reference_number="TEST-REF-001",
        tender_url="https://example.com/tender/1",
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


def create_service(
    keyword_result: FilterResult,
    eligibility_result: EligibilityResult,
) -> TenderEvaluationService:
    """Create evaluation service with mocked engines."""

    keyword_engine = Mock()

    keyword_engine.evaluate.return_value = (
        keyword_result
    )

    eligibility_engine = Mock()

    eligibility_engine.evaluate.return_value = (
        eligibility_result
    )

    return TenderEvaluationService(
        keyword_engine,
        eligibility_engine,
    )


def test_qualified_tender():
    service = create_service(
        FilterResult(
            is_relevant=True,
            matched_keywords=["construction"],
        ),
        EligibilityResult(
            status="ELIGIBLE",
        ),
    )

    result = service.evaluate(
        create_tender()
    )

    assert result.status == "QUALIFIED"
    assert result.is_qualified is True


def test_irrelevant_tender_is_filtered_out():
    service = create_service(
        FilterResult(
            is_relevant=False,
            reasons=[
                "No configured keywords matched"
            ],
        ),
        EligibilityResult(
            status="ELIGIBLE",
        ),
    )

    result = service.evaluate(
        create_tender()
    )

    assert result.status == "FILTERED_OUT"
    assert result.is_qualified is False


def test_relevant_but_ineligible_tender():
    service = create_service(
        FilterResult(
            is_relevant=True,
            matched_keywords=["construction"],
        ),
        EligibilityResult(
            status="NOT_ELIGIBLE",
        ),
    )

    result = service.evaluate(
        create_tender()
    )

    assert result.status == "NOT_ELIGIBLE"
    assert result.is_qualified is False


def test_relevant_tender_with_unknown_eligibility():
    service = create_service(
        FilterResult(
            is_relevant=True,
            matched_keywords=["construction"],
        ),
        EligibilityResult(
            status="UNKNOWN",
        ),
    )

    result = service.evaluate(
        create_tender()
    )

    assert result.status == "REVIEW_REQUIRED"
    assert result.is_qualified is False