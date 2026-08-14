from pathlib import Path

from tender_intelligence_platform.engines.eligibility_engine import (
    EligibilityEngine,
)
from tender_intelligence_platform.models.tender import Tender


CONFIG_PATH = Path(
    "config/eligibility.yaml"
)


def create_tender(
    estimated_value: float,
    category: str = "Works",
    procurement_type: str = "Works",
    status: str = "Open",
) -> Tender:
    """Create a tender for eligibility testing."""

    return Tender(
        tender_id="TEST-001",
        tender_title="Construction of office building",
        organization="Test Organization",
        tender_reference_number="REF-001",
        tender_url="https://example.com/tender",
        published_date=None,
        bid_submission_start_date=None,
        bid_submission_end_date=None,
        opening_date=None,
        estimated_value=estimated_value,
        earnest_money_deposit=None,
        tender_fee=None,
        currency="INR",
        tender_type="Open Tender",
        category=category,
        procurement_type=procurement_type,
        state=None,
        city=None,
        work_location=None,
        status=status,
        withdrawal_allowed=True,
        form_of_contract=None,
        payment_mode=None,
        work_description="Civil construction work",
    )


def test_eligible_tender():
    engine = EligibilityEngine(
        CONFIG_PATH
    )

    tender = create_tender(
        estimated_value=5_000_000
    )

    result = engine.evaluate(tender)

    assert result.status == "ELIGIBLE"
    assert len(result.failed_rules) == 0
    assert len(result.unknown_rules) == 0


def test_tender_fails_minimum_value():
    engine = EligibilityEngine(
        CONFIG_PATH
    )

    tender = create_tender(
        estimated_value=500_000
    )

    result = engine.evaluate(tender)

    assert result.status == "NOT_ELIGIBLE"

    assert any(
        rule.rule_name == "minimum_tender_value"
        for rule in result.failed_rules
    )


def test_tender_fails_category():
    engine = EligibilityEngine(
        CONFIG_PATH
    )

    tender = create_tender(
        estimated_value=5_000_000,
        category="Goods",
    )

    result = engine.evaluate(tender)

    assert result.status == "NOT_ELIGIBLE"

    assert any(
        rule.rule_name == "allowed_category"
        for rule in result.failed_rules
    )


def test_tender_fails_status():
    engine = EligibilityEngine(
        CONFIG_PATH
    )

    tender = create_tender(
        estimated_value=5_000_000,
        status="Closed",
    )

    result = engine.evaluate(tender)

    print(result.reasons)
    print(result.failed_rules)
    print(result.passed_rules)

    assert result.status == "NOT_ELIGIBLE"


def test_missing_field_returns_unknown():
    engine = EligibilityEngine(
        CONFIG_PATH
    )

    tender = create_tender(
        estimated_value=5_000_000
    )

    # Create a temporary rule that references
    # information not currently available.
    engine._rules.append(
        engine._rules[0].__class__(
            name="minimum_turnover",
            field="bidder.turnover",
            operator="gte",
            value=50_000_000,
            required=True,
        )
    )

    result = engine.evaluate(tender)

    assert result.status == "UNKNOWN"

    assert any(
        rule.rule_name == "minimum_turnover"
        for rule in result.unknown_rules
    )