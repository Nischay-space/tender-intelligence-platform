from typing import Any

from tender_intelligence_platform.models.rule import Rule
from tender_intelligence_platform.models.rule_result import (
    RuleResult,
)


class RuleEvaluator:
    """Evaluates configurable rules against objects."""

    SUPPORTED_OPERATORS = {
        "equals",
        "not_equals",
        "gt",
        "gte",
        "lt",
        "lte",
        "in",
        "not_in",
        "contains",
        "not_contains",
        "exists",
    }

    def evaluate(
        self,
        rule: Rule,
        obj: Any,
    ) -> RuleResult:
        """Evaluate one rule against an object."""

        if rule.operator not in self.SUPPORTED_OPERATORS:
            raise ValueError(
                f"Unsupported operator: "
                f"{rule.operator}"
            )

        actual_value = self._get_field_value(
            obj,
            rule.field,
        )

        passed = self._evaluate_operator(
            actual_value,
            rule,
        )

        reason = self._build_reason(
            rule,
            actual_value,
            passed,
        )

        return RuleResult(
            rule_name=rule.name,
            passed=passed,
            reason=reason,
        )

    @staticmethod
    def _get_field_value(
        obj: Any,
        field: str,
    ) -> Any:
        """Get a field value from an object."""

        value = obj

        for part in field.split("."):
            if value is None:
                return None

            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = getattr(
                    value,
                    part,
                    None,
                )

        return value

    def _evaluate_operator(
        self,
        actual_value: Any,
        rule: Rule,
    ) -> bool:
        """Evaluate the configured operator."""

        operator = rule.operator

        if operator == "exists":
            return actual_value is not None

        if operator == "equals":
            return actual_value == rule.value

        if operator == "not_equals":
            return actual_value != rule.value

        if operator == "gt":
            return self._compare(
                actual_value,
                rule.value,
                lambda a, b: a > b,
            )

        if operator == "gte":
            return self._compare(
                actual_value,
                rule.value,
                lambda a, b: a >= b,
            )

        if operator == "lt":
            return self._compare(
                actual_value,
                rule.value,
                lambda a, b: a < b,
            )

        if operator == "lte":
            return self._compare(
                actual_value,
                rule.value,
                lambda a, b: a <= b,
            )

        if operator == "in":
            return actual_value in rule.values

        if operator == "not_in":
            return actual_value not in rule.values

        if operator == "contains":
            return self._contains(
                actual_value,
                rule.value,
            )

        if operator == "not_contains":
            return not self._contains(
                actual_value,
                rule.value,
            )

        return False

    @staticmethod
    def _compare(
        actual_value: Any,
        expected_value: Any,
        operation,
    ) -> bool:
        """Safely perform a comparison."""

        if (
            actual_value is None
            or expected_value is None
        ):
            return False

        try:
            return operation(
                actual_value,
                expected_value,
            )
        except TypeError:
            return False

    @staticmethod
    def _contains(
        actual_value: Any,
        expected_value: Any,
    ) -> bool:
        """Check whether a value contains another value."""

        if (
            actual_value is None
            or expected_value is None
        ):
            return False

        try:
            return expected_value in actual_value
        except TypeError:
            return False

    @staticmethod
    def _build_reason(
        rule: Rule,
        actual_value: Any,
        passed: bool,
    ) -> str:
        """Build a human-readable rule result."""

        status = "passed" if passed else "failed"

        return (
            f"Rule '{rule.name}' {status}: "
            f"field '{rule.field}' "
            f"has value {actual_value!r}"
        )