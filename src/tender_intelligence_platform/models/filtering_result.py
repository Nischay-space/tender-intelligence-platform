from dataclasses import dataclass

from tender_intelligence_platform.models.eligibility_result import (
    EligibilityResult,
)
from tender_intelligence_platform.models.filter_result import (
    FilterResult,
)


@dataclass
class FilteringResult:
    """Combined result of keyword and eligibility filtering."""

    keyword_result: FilterResult

    eligibility_result: EligibilityResult | None

    status: str

    reasons: list[str]

    @property
    def is_accepted(self) -> bool:
        """Return True when the tender passes all filtering stages."""

        return self.status == "ACCEPTED"

    @property
    def requires_review(self) -> bool:
        """Return True when the tender cannot be conclusively accepted."""

        return self.status == "REVIEW_REQUIRED"