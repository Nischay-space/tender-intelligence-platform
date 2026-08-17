from dataclasses import dataclass, field

from tender_intelligence_platform.models.eligibility_result import (
    EligibilityResult,
)
from tender_intelligence_platform.models.filter_result import (
    FilterResult,
)


@dataclass
class EvaluationResult:
    """Combined result of tender relevance and eligibility evaluation."""

    status: str

    keyword_result: FilterResult

    eligibility_result: EligibilityResult

    reasons: list[str] = field(
        default_factory=list
    )

    @property
    def is_qualified(self) -> bool:
        """Return True when the tender passes both stages."""

        return self.status == "QUALIFIED"