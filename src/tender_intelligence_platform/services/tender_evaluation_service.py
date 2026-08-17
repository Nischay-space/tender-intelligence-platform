from tender_intelligence_platform.engines.eligibility_engine import (
    EligibilityEngine,
)
from tender_intelligence_platform.engines.keyword_engine import (
    KeywordEngine,
)
from tender_intelligence_platform.models.evaluation_result import (
    EvaluationResult,
)
from tender_intelligence_platform.models.tender import Tender


class TenderEvaluationService:
    """Evaluate a tender using the configured filtering engines."""

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
    ) -> EvaluationResult:
        """Run keyword and eligibility evaluation for a tender."""

        keyword_result = self._keyword_engine.evaluate(
            tender
        )

        eligibility_result = self._eligibility_engine.evaluate(
            tender
        )

        status = self._determine_status(
            keyword_result.is_relevant,
            eligibility_result.status,
        )

        reasons = self._build_reasons(
            keyword_result,
            eligibility_result,
            status,
        )

        return EvaluationResult(
            status=status,
            keyword_result=keyword_result,
            eligibility_result=eligibility_result,
            reasons=reasons,
        )

    @staticmethod
    def _determine_status(
        is_relevant: bool,
        eligibility_status: str,
    ) -> str:
        """Determine the final tender classification."""

        if not is_relevant:
            return "FILTERED_OUT"

        if eligibility_status == "NOT_ELIGIBLE":
            return "NOT_ELIGIBLE"

        if eligibility_status == "UNKNOWN":
            return "REVIEW_REQUIRED"

        return "QUALIFIED"

    @staticmethod
    def _build_reasons(
        keyword_result,
        eligibility_result,
        status: str,
    ) -> list[str]:
        """Build human-readable reasons for the final decision."""

        reasons = []

        reasons.extend(
            keyword_result.reasons
        )

        reasons.extend(
            eligibility_result.reasons
        )

        reasons.append(
            f"Final evaluation status: {status}"
        )

        return reasons