from uuid import uuid4

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
from tender_intelligence_platform.repositories.tender_evaluation_repository import (
    TenderEvaluationRepository,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)


def make_tender() -> Tender:
    """Create a valid test tender."""

    unique_id = f"TEST-EVAL-{uuid4().hex[:8]}"

    return Tender(
        tender_id=unique_id,
        tender_title="Evaluation Test Tender",
        organization="Test Organization",
        tender_reference_number="EVAL-REF-001",
        tender_url="https://example.com/tender",
        published_date="10-Aug-2026 10:00 AM",
        bid_submission_start_date="10-Aug-2026 10:30 AM",
        bid_submission_end_date="20-Aug-2026 05:30 PM",
        opening_date="21-Aug-2026 11:00 AM",
        estimated_value=500000.0,
        earnest_money_deposit=5000.0,
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
        work_description="Construction and renovation work",
    )


def make_evaluation_result() -> EvaluationResult:
    """Create a representative qualified evaluation result."""

    keyword_result = FilterResult(
        is_relevant=True,
        matched_keywords=[
            "construction",
            "renovation",
        ],
        excluded_keywords=[],
        reasons=[
            "Matched keywords: construction, renovation",
        ],
    )

    passed_rule = RuleResult(
        rule_name="minimum_tender_value",
        passed=True,
        reason=(
            "Rule 'minimum_tender_value' passed: "
            "field 'estimated_value' has value 500000.0"
        ),
    )

    eligibility_result = EligibilityResult(
        status="ELIGIBLE",
        passed_rules=[passed_rule],
        failed_rules=[],
        unknown_rules=[],
        reasons=[
            "PASS: Rule 'minimum_tender_value' passed"
        ],
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


def create_tender(
    session,
    tender: Tender,
):
    """Persist a tender and return its ORM record."""

    repository = TenderRepository(session)

    return repository.create(tender)


def test_upsert_creates_evaluation():
    tender = make_tender()
    result = make_evaluation_result()

    with SessionLocal() as session:
        tender_orm = create_tender(
            session,
            tender,
        )

        repository = TenderEvaluationRepository(
            session
        )

        evaluation = repository.upsert(
            tender_orm.id,
            result,
        )

        session.commit()

        assert evaluation.id is not None
        assert evaluation.tender_id == tender_orm.id
        assert evaluation.keyword_status == "RELEVANT"
        assert evaluation.eligibility_status == "ELIGIBLE"
        assert evaluation.final_status == "QUALIFIED"


def test_get_by_tender_id():
    tender = make_tender()
    result = make_evaluation_result()

    with SessionLocal() as session:
        tender_orm = create_tender(
            session,
            tender,
        )

        repository = TenderEvaluationRepository(
            session
        )

        repository.upsert(
            tender_orm.id,
            result,
        )

        session.commit()

        found = repository.get_by_tender_id(
            tender_orm.id
        )

        assert found is not None
        assert found.tender_id == tender_orm.id
        assert found.final_status == "QUALIFIED"


def test_upsert_updates_existing_evaluation():
    tender = make_tender()

    first_result = make_evaluation_result()

    with SessionLocal() as session:
        tender_orm = create_tender(
            session,
            tender,
        )

        repository = TenderEvaluationRepository(
            session
        )

        first = repository.upsert(
            tender_orm.id,
            first_result,
        )

        session.commit()

        first_id = first.id

        updated_result = EvaluationResult(
            status="FILTERED_OUT",
            keyword_result=FilterResult(
                is_relevant=False,
                matched_keywords=[],
                excluded_keywords=["software"],
                reasons=[
                    "Excluded keywords: software"
                ],
            ),
            eligibility_result=EligibilityResult(
                status="NOT_ELIGIBLE",
                passed_rules=[],
                failed_rules=[
                    RuleResult(
                        rule_name="minimum_tender_value",
                        passed=False,
                        reason=(
                            "Rule 'minimum_tender_value' failed"
                        ),
                    )
                ],
                unknown_rules=[],
                reasons=[
                    "FAIL: Rule 'minimum_tender_value' failed"
                ],
            ),
            reasons=[
                "Excluded keywords: software",
                "Final evaluation status: FILTERED_OUT",
            ],
        )

        second = repository.upsert(
            tender_orm.id,
            updated_result,
        )

        session.commit()

        assert second.id == first_id
        assert second.keyword_status == "FILTERED_OUT"
        assert second.eligibility_status == "NOT_ELIGIBLE"
        assert second.final_status == "FILTERED_OUT"


def test_evaluation_results_are_persisted():
    tender = make_tender()
    result = make_evaluation_result()

    with SessionLocal() as session:
        tender_orm = create_tender(
            session,
            tender,
        )

        repository = TenderEvaluationRepository(
            session
        )

        repository.upsert(
            tender_orm.id,
            result,
        )

        session.commit()

        found = repository.get_by_tender_id(
            tender_orm.id
        )

        assert found is not None

        assert found.matched_keywords == [
            "construction",
            "renovation",
        ]

        assert found.excluded_keywords == []

        assert len(found.passed_rules) == 1
        assert (
            found.passed_rules[0]["rule_name"]
            == "minimum_tender_value"
        )
        assert (
            found.passed_rules[0]["passed"]
            is True
        )

        assert found.failed_rules == []
        assert found.unknown_rules == []

        assert len(found.reasons) == 3


def test_evaluation_is_unique_per_tender():
    tender = make_tender()
    result = make_evaluation_result()

    with SessionLocal() as session:
        tender_orm = create_tender(
            session,
            tender,
        )

        repository = TenderEvaluationRepository(
            session
        )

        first = repository.upsert(
            tender_orm.id,
            result,
        )

        session.commit()

        second = repository.upsert(
            tender_orm.id,
            result,
        )

        session.commit()

        assert first.id == second.id

        found = repository.get_by_tender_id(
            tender_orm.id
        )

        assert found is not None
        assert found.id == first.id