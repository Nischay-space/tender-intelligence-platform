from tender_intelligence_platform.engines.eligibility_engine import (
    EligibilityEngine,
)
from tender_intelligence_platform.engines.keyword_engine import (
    KeywordEngine,
)
from tender_intelligence_platform.models.filtering_result import (
    FilteringResult,
)
from tender_intelligence_platform.models.tender import Tender


class TenderFilteringService:
    """Orchestrate keyword and eligibility filtering."""

    def __init__(
        self,
        keyword_engine: KeywordEngine,
        eligibility_engine: EligibilityEngine,
    ):
        self._keyword_engine = keyword_engine
        self._eligibility_engine = eligibility_engine

    def evaluate(
        self,
        tender: Tender,
    ) -> FilteringResult:
        """Run the tender through the filtering pipeline."""

        keyword_result = self._keyword_engine.evaluate(
            tender
        )

        if not keyword_result.is_relevant:
            return FilteringResult(
                keyword_result=keyword_result,
                eligibility_result=None,
                status="REJECTED_KEYWORD",
                reasons=[
                    "Tender rejected by keyword filtering",
                    *keyword_result.reasons,
                ],
            )

        eligibility_result = (
            self._eligibility_engine.evaluate(
                tender
            )
        )

        status = self._determine_status(
            eligibility_result.status
        )

        reasons = [
            "Tender passed keyword filtering",
            *keyword_result.reasons,
            *eligibility_result.reasons,
        ]

        return FilteringResult(
            keyword_result=keyword_result,
            eligibility_result=eligibility_result,
            status=status,
            reasons=reasons,
        )

    @staticmethod
    def _determine_status(
        eligibility_status: str,
    ) -> str:
        """Convert eligibility status into final filtering status."""

        if eligibility_status == "ELIGIBLE":
            return "ACCEPTED"

        if eligibility_status == "NOT_ELIGIBLE":
            return "REJECTED_ELIGIBILITY"

        return "REVIEW_REQUIRED"