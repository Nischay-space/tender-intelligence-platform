from uuid import uuid4

import pytest

from tender_intelligence_platform.database.connection import SessionLocal
from tender_intelligence_platform.models.eligibility_result import (
    EligibilityResult,
)
from tender_intelligence_platform.models.evaluation_result import (
    EvaluationResult,
)
from tender_intelligence_platform.models.filter_result import (
    FilterResult,
)
from tender_intelligence_platform.models.rule_result import (
    RuleResult,
)
from tender_intelligence_platform.models.tender import Tender


@pytest.fixture
def db_session():
    """Provide a real database session for a single test."""

    with SessionLocal() as session:
        yield session


@pytest.fixture
def make_tender():
    """Factory fixture: build a valid Tender with a unique business ID."""

    def _make_tender(prefix: str = "TEST", **overrides) -> Tender:
        unique_id = f"{prefix}-{uuid4().hex[:8]}"

        defaults = dict(
            tender_id=unique_id,
            tender_title="Test Tender",
            organization="Test Organization",
            tender_reference_number="REF-001",
            tender_url="https://example.com/tender",
            published_date="10-Aug-2026 10:00 AM",
            bid_submission_start_date="10-Aug-2026 10:30 AM",
            bid_submission_end_date="20-Aug-2026 05:30 PM",
            opening_date="21-Aug-2026 11:00 AM",
            estimated_value=100000.0,
            earnest_money_deposit=2000.0,
            tender_fee=500.0,
            currency="INR",
            tender_type="Open Tender",
            category="Works",
            procurement_type="Works",
            state="Delhi",
            city="New Delhi",
            work_location="New Delhi",
            status="Open",
            withdrawal_allowed=True,
            form_of_contract="Item Rate",
            payment_mode="Offline",
            work_description="Test tender description",
        )
        defaults.update(overrides)

        return Tender(**defaults)

    return _make_tender


@pytest.fixture
def make_evaluation_result():
    """Factory fixture: build a representative QUALIFIED EvaluationResult."""

    def _make_evaluation_result() -> EvaluationResult:
        keyword_result = FilterResult(
            is_relevant=True,
            matched_keywords=["construction", "renovation"],
            excluded_keywords=[],
            reasons=["Matched keywords: construction, renovation"],
        )

        passed_rule = RuleResult(
            rule_name="minimum_tender_value",
            passed=True,
            reason="Rule 'minimum_tender_value' passed",
        )

        eligibility_result = EligibilityResult(
            status="ELIGIBLE",
            passed_rules=[passed_rule],
            failed_rules=[],
            unknown_rules=[],
            reasons=["PASS: Rule 'minimum_tender_value' passed"],
        )

        return EvaluationResult(
            status="QUALIFIED",
            keyword_result=keyword_result,
            eligibility_result=eligibility_result,
            reasons=[
                "Matched keywords: construction, renovation",
                "PASS: Rule 'minimum_tender_value' passed",
                "Final evaluation status: QUALIFIED",
            ],
        )

    return _make_evaluation_result