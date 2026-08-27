from dataclasses import dataclass, field

from tender_intelligence_platform.models.tender import Tender


@dataclass
class IngestionFailure:
    """Information about a failed tender ingestion."""

    tender_reference_number: str
    error: str


@dataclass
class IngestionSkip:
    """Information about a tender skipped by the pre-download filter."""

    tender_reference_number: str
    reason: str


@dataclass
class IngestionResult:
    """Result of a tender ingestion run."""

    discovered: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0

    tenders: list[Tender] = field(
        default_factory=list
    )

    failures: list[IngestionFailure] = field(
        default_factory=list
    )

    skips: list[IngestionSkip] = field(
        default_factory=list
    )