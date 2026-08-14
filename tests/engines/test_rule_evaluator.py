from dataclasses import dataclass

import pytest

from tender_intelligence_platform.engines.rule_evaluator import (
    RuleEvaluator,
)
from tender_intelligence_platform.models.rule import Rule


@dataclass
class SampleTender:
    estimated_value: float
    category: str
    status: str


@pytest.fixture
def evaluator():
    return RuleEvaluator()


@pytest.fixture
def tender():
    return SampleTender(
        estimated_value=5_000_000,
        category="Works",
        status="Open",
    )


def test_equals(evaluator, tender):
    rule = Rule(
        name="category_check",
        field="category",
        operator="equals",
        value="Works",
    )

    result = evaluator.evaluate(
        rule,
        tender,
    )

    assert result.passed is True


def test_not_equals(evaluator, tender):
    rule = Rule(
        name="category_check",
        field="category",
        operator="not_equals",
        value="Services",
    )

    result = evaluator.evaluate(
        rule,
        tender,
    )

    assert result.passed is True


def test_greater_than(evaluator, tender):
    rule = Rule(
        name="value_check",
        field="estimated_value",
        operator="gt",
        value=1_000_000,
    )

    result = evaluator.evaluate(
        rule,
        tender,
    )

    assert result.passed is True


def test_greater_than_or_equal(evaluator, tender):
    rule = Rule(
        name="value_check",
        field="estimated_value",
        operator="gte",
        value=5_000_000,
    )

    result = evaluator.evaluate(
        rule,
        tender,
    )

    assert result.passed is True


def test_less_than(evaluator, tender):
    rule = Rule(
        name="value_check",
        field="estimated_value",
        operator="lt",
        value=10_000_000,
    )

    result = evaluator.evaluate(
        rule,
        tender,
    )

    assert result.passed is True


def test_less_than_or_equal(evaluator, tender):
    rule = Rule(
        name="value_check",
        field="estimated_value",
        operator="lte",
        value=5_000_000,
    )

    result = evaluator.evaluate(
        rule,
        tender,
    )

    assert result.passed is True


def test_in(evaluator, tender):
    rule = Rule(
        name="category_check",
        field="category",
        operator="in",
        values=[
            "Works",
            "Services",
        ],
    )

    result = evaluator.evaluate(
        rule,
        tender,
    )

    assert result.passed is True


def test_not_in(evaluator, tender):
    rule = Rule(
        name="category_check",
        field="category",
        operator="not_in",
        values=[
            "Goods",
            "Consultancy",
        ],
    )

    result = evaluator.evaluate(
        rule,
        tender,
    )

    assert result.passed is True


def test_contains(evaluator):
    obj = {
        "description": "civil construction work"
    }

    rule = Rule(
        name="description_check",
        field="description",
        operator="contains",
        value="construction",
    )

    result = evaluator.evaluate(
        rule,
        obj,
    )

    assert result.passed is True


def test_not_contains(evaluator):
    obj = {
        "description": "civil construction work"
    }

    rule = Rule(
        name="description_check",
        field="description",
        operator="not_contains",
        value="highway",
    )

    result = evaluator.evaluate(
        rule,
        obj,
    )

    assert result.passed is True


def test_exists(evaluator, tender):
    rule = Rule(
        name="status_exists",
        field="status",
        operator="exists",
    )

    result = evaluator.evaluate(
        rule,
        tender,
    )

    assert result.passed is True


def test_missing_field_fails_exists(evaluator):
    obj = {}

    rule = Rule(
        name="location_exists",
        field="location",
        operator="exists",
    )

    result = evaluator.evaluate(
        rule,
        obj,
    )

    assert result.passed is False


def test_unsupported_operator_is_rejected(
    evaluator,
    tender,
):
    rule = Rule(
        name="invalid_rule",
        field="status",
        operator="between",
        value="Open",
    )

    with pytest.raises(ValueError):
        evaluator.evaluate(
            rule,
            tender,
        )