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


def make_tender() -> Tender:
    return Tender(
        tender_id="TEST-EVAL-001",
        tender_title="Test Construction Tender",
        tender_url="https://example.com/tender",
        estimated_value=1000000.0,
        category="Works",
        procurement_type="Works",
        status="Open",
        work_description="Construction of office building",
    )


def make_keyword_result(
    is_relevant: bool,
) -> FilterResult:
    return FilterResult(
        is_relevant=is_relevant,
        matched_keywords=(
            ["construction"]
            if is_relevant
            else []
        ),
        reasons=[
            "Keyword evaluation completed"
        ],
    )


def make_eligibility_result(
    status: str,
) -> EligibilityResult:
    return EligibilityResult(
        status=status,
        reasons=[
            "Eligibility evaluation completed"
        ],
    )


def make_service(
    keyword_result: FilterResult,
    eligibility_result: EligibilityResult,
) -> TenderEvaluationService:

    keyword_engine = Mock()
    eligibility_engine = Mock()

    keyword_engine.evaluate.return_value = (
        keyword_result
    )

    eligibility_engine.evaluate.return_value = (
        eligibility_result
    )

    return TenderEvaluationService(
        keyword_engine=keyword_engine,
        eligibility_engine=eligibility_engine,
    )


def test_relevant_and_eligible_is_qualified():

    service = make_service(
        make_keyword_result(True),
        make_eligibility_result("ELIGIBLE"),
    )

    result = service.evaluate(
        make_tender()
    )

    assert result.status == "QUALIFIED"
    assert result.is_qualified is True


def test_irrelevant_tender_is_filtered_out():

    service = make_service(
        make_keyword_result(False),
        make_eligibility_result("ELIGIBLE"),
    )

    result = service.evaluate(
        make_tender()
    )

    assert result.status == "FILTERED_OUT"
    assert result.is_qualified is False


def test_relevant_but_not_eligible():

    service = make_service(
        make_keyword_result(True),
        make_eligibility_result("NOT_ELIGIBLE"),
    )

    result = service.evaluate(
        make_tender()
    )

    assert result.status == "NOT_ELIGIBLE"
    assert result.is_qualified is False


def test_relevant_but_unknown_requires_review():

    service = make_service(
        make_keyword_result(True),
        make_eligibility_result("UNKNOWN"),
    )

    result = service.evaluate(
        make_tender()
    )

    assert result.status == "REVIEW_REQUIRED"
    assert result.is_qualified is False


def test_evaluation_reasons_include_final_status():

    service = make_service(
        make_keyword_result(True),
        make_eligibility_result("ELIGIBLE"),
    )

    result = service.evaluate(
        make_tender()
    )

    assert (
        "Final evaluation status: QUALIFIED"
        in result.reasons
    )