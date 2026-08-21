from types import SimpleNamespace

import pytest

from tender_intelligence_platform.engines.rule_evaluator import (
    RuleEvaluator,
)
from tender_intelligence_platform.models.rule import Rule


@pytest.fixture
def evaluator():
    return RuleEvaluator()


@pytest.fixture
def tender():
    return SimpleNamespace(
        estimated_value=500000,
        category="Works",
        procurement_type="Works",
        status="Open",
        title="Construction of Office Building",
        state="Delhi",
    )


def test_equals_operator(evaluator, tender):
    rule = Rule(
        name="category_check",
        field="category",
        operator="equals",
        value="Works",
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True
    assert result.rule_name == "category_check"


def test_not_equals_operator(evaluator, tender):
    rule = Rule(
        name="category_check",
        field="category",
        operator="not_equals",
        value="Services",
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_greater_than_operator(evaluator, tender):
    rule = Rule(
        name="minimum_value",
        field="estimated_value",
        operator="gt",
        value=100000,
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_greater_than_or_equal_operator(evaluator, tender):
    rule = Rule(
        name="minimum_value",
        field="estimated_value",
        operator="gte",
        value=500000,
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_less_than_operator(evaluator, tender):
    rule = Rule(
        name="value_limit",
        field="estimated_value",
        operator="lt",
        value=1000000,
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_less_than_or_equal_operator(evaluator, tender):
    rule = Rule(
        name="value_limit",
        field="estimated_value",
        operator="lte",
        value=500000,
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_in_operator(evaluator, tender):
    rule = Rule(
        name="allowed_category",
        field="category",
        operator="in",
        values=["Works", "Goods"],
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_not_in_operator(evaluator, tender):
    rule = Rule(
        name="blocked_category",
        field="category",
        operator="not_in",
        values=["Services", "Consultancy"],
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_contains_operator(evaluator, tender):
    rule = Rule(
        name="title_contains",
        field="title",
        operator="contains",
        value="Construction",
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_not_contains_operator(evaluator, tender):
    rule = Rule(
        name="title_check",
        field="title",
        operator="not_contains",
        value="Bridge",
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_exists_operator(evaluator, tender):
    rule = Rule(
        name="state_exists",
        field="state",
        operator="exists",
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_exists_returns_false_for_missing_value(evaluator, tender):
    rule = Rule(
        name="unknown_field",
        field="nonexistent_field",
        operator="exists",
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is False


def test_missing_field_fails_comparison(evaluator, tender):
    rule = Rule(
        name="missing_value",
        field="nonexistent_field",
        operator="gte",
        value=100,
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is False


def test_invalid_operator_raises_error(evaluator, tender):
    rule = Rule(
        name="invalid_rule",
        field="category",
        operator="invalid_operator",
        value="Works",
    )

    with pytest.raises(ValueError, match="Unsupported operator"):
        evaluator.evaluate(rule, tender)


def test_nested_field_lookup(evaluator):
    tender = {
        "organization": {
            "name": "Test Organization",
        }
    }

    rule = Rule(
        name="organization_check",
        field="organization.name",
        operator="equals",
        value="Test Organization",
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is True


def test_failed_rule_contains_useful_reason(evaluator, tender):
    rule = Rule(
        name="minimum_value",
        field="estimated_value",
        operator="gte",
        value=1000000,
    )

    result = evaluator.evaluate(rule, tender)

    assert result.passed is False
    assert "minimum_value" in result.reason
    assert "estimated_value" in result.reason
    assert "500000" in result.reason