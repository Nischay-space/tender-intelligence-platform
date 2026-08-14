from dataclasses import dataclass


@dataclass
class RuleResult:
    """Result of evaluating one rule."""

    rule_name: str
    passed: bool
    reason: str