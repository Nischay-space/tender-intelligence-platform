from dataclasses import dataclass


@dataclass
class PreFilterResult:
    """Result of a cheap, pre-download filtering decision on a TenderLink."""

    should_skip: bool
    reason: str | None = None