from dataclasses import dataclass, field

from tender_intelligence_platform.models.rule_result import RuleResult


@dataclass
class EligibilityResult:
    """Result of evaluating tender eligibility."""

    status: str

    passed_rules: list[RuleResult] = field(
        default_factory=list
    )

    failed_rules: list[RuleResult] = field(
        default_factory=list
    )

    unknown_rules: list[RuleResult] = field(
        default_factory=list
    )

    reasons: list[str] = field(
        default_factory=list
    )