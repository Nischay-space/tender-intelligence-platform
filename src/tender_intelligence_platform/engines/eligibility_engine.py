from pathlib import Path

import yaml

from tender_intelligence_platform.engines.rule_evaluator import (
    RuleEvaluator,
)
from tender_intelligence_platform.models.eligibility_result import (
    EligibilityResult,
)
from tender_intelligence_platform.models.rule import Rule
from tender_intelligence_platform.models.rule_result import (
    RuleResult,
)
from tender_intelligence_platform.models.tender import Tender


class EligibilityEngine:
    """Configuration-driven tender eligibility engine."""

    def __init__(
        self,
        config_path: str | Path,
    ):
        self._config = self._load_config(
            config_path
        )

        self._settings = self._config.get(
            "eligibility",
            {},
        )

        self._evaluator = RuleEvaluator()

        self._rules = self._load_rules()

    @staticmethod
    def _load_config(
        config_path: str | Path,
    ) -> dict:
        """Load eligibility configuration."""

        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Eligibility configuration not found: {path}"
            )

        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            config = yaml.safe_load(file)

        if not isinstance(config, dict):
            raise ValueError(
                "Eligibility configuration must be a YAML mapping"
            )

        return config

    def _load_rules(self) -> list[Rule]:
        """Convert configured rules into Rule objects."""

        configured_rules = self._settings.get(
            "rules",
            [],
        )

        rules = []

        for rule_config in configured_rules:
            rules.append(
                Rule(
                    name=rule_config["name"],
                    field=rule_config["field"],
                    operator=rule_config["operator"],
                    value=rule_config.get("value"),
                    values=rule_config.get(
                        "values",
                        [],
                    ),
                    required=rule_config.get(
                        "required",
                        False,
                    ),
                )
            )

        return rules

    def evaluate(
        self,
        tender: Tender,
    ) -> EligibilityResult:
        """Evaluate tender eligibility."""

        if not self._settings.get(
            "enabled",
            True,
        ):
            return EligibilityResult(
                status="UNKNOWN",
                reasons=[
                    "Eligibility engine is disabled"
                ],
            )

        passed_rules: list[RuleResult] = []
        failed_rules: list[RuleResult] = []
        unknown_rules: list[RuleResult] = []

        for rule in self._rules:
            rule_result = self._evaluator.evaluate(
                rule,
                tender,
            )

            if rule_result.passed:
                passed_rules.append(
                    rule_result
                )
                continue

            if self._is_unknown(
                rule,
                tender,
            ):
                unknown_rules.append(
                    rule_result
                )
            else:
                failed_rules.append(
                    rule_result
                )

        status = self._determine_status(
            failed_rules,
            unknown_rules,
        )

        reasons = self._build_reasons(
            passed_rules,
            failed_rules,
            unknown_rules,
        )

        return EligibilityResult(
            status=status,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            unknown_rules=unknown_rules,
            reasons=reasons,
        )

    @staticmethod
    def _is_unknown(
        rule: Rule,
        tender: Tender,
    ) -> bool:
        """Determine whether a failed rule is unknown."""

        value = tender

        for part in rule.field.split("."):
            if value is None:
                return True

            if isinstance(value, dict):
                if part not in value:
                    return True

                value = value[part]

            else:
                if not hasattr(value, part):
                    return True

                value = getattr(
                    value,
                    part,
                )

        return value is None

    @staticmethod
    def _determine_status(
        failed_rules: list[RuleResult],
        unknown_rules: list[RuleResult],
    ) -> str:
        """Determine overall eligibility status."""

        if failed_rules:
            return "NOT_ELIGIBLE"

        if unknown_rules:
            return "UNKNOWN"

        return "ELIGIBLE"

    @staticmethod
    def _build_reasons(
        passed_rules: list[RuleResult],
        failed_rules: list[RuleResult],
        unknown_rules: list[RuleResult],
    ) -> list[str]:
        """Build human-readable eligibility reasons."""

        reasons = []

        for rule in passed_rules:
            reasons.append(
                f"PASS: {rule.reason}"
            )

        for rule in failed_rules:
            reasons.append(
                f"FAIL: {rule.reason}"
            )

        for rule in unknown_rules:
            reasons.append(
                f"UNKNOWN: {rule.reason}"
            )

        return reasons