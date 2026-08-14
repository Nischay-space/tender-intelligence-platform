from dataclasses import dataclass, field


@dataclass
class FilterResult:
    """Result produced by the relevance filter."""

    is_relevant: bool

    matched_keywords: list[str] = field(
        default_factory=list
    )

    excluded_keywords: list[str] = field(
        default_factory=list
    )

    reasons: list[str] = field(
        default_factory=list
    )