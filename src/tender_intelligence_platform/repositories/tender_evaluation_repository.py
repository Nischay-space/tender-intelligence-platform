from sqlalchemy.orm import Session

from tender_intelligence_platform.database.models.tender_evaluation import (
    TenderEvaluationORM,
)
from tender_intelligence_platform.models.evaluation_result import (
    EvaluationResult,
)


class TenderEvaluationRepository:
    """Repository for persisting tender evaluation results."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_tender_id(
        self,
        tender_id: int,
    ) -> TenderEvaluationORM | None:
        """Return the evaluation associated with a tender."""

        return (
            self._session.query(TenderEvaluationORM)
            .filter(
                TenderEvaluationORM.tender_id == tender_id
            )
            .first()
        )

    def upsert(
        self,
        tender_id: int,
        result: EvaluationResult,
    ) -> TenderEvaluationORM:
        """Create or update the evaluation for a tender."""

        evaluation = self.get_by_tender_id(
            tender_id
        )

        if evaluation is None:
            evaluation = TenderEvaluationORM(
                tender_id=tender_id,
            )
            self._session.add(evaluation)

        evaluation.keyword_status = (
            "RELEVANT"
            if result.keyword_result.is_relevant
            else "FILTERED_OUT"
        )

        evaluation.eligibility_status = (
            result.eligibility_result.status
        )

        evaluation.final_status = result.status

        evaluation.matched_keywords = (
            result.keyword_result.matched_keywords
        )

        evaluation.excluded_keywords = (
            result.keyword_result.excluded_keywords
        )

        evaluation.passed_rules = [
            {
                "rule_name": rule.rule_name,
                "passed": rule.passed,
                "reason": rule.reason,
            }
            for rule in result.eligibility_result.passed_rules
        ]

        evaluation.failed_rules = [
            {
                "rule_name": rule.rule_name,
                "passed": rule.passed,
                "reason": rule.reason,
            }
            for rule in result.eligibility_result.failed_rules
        ]

        evaluation.unknown_rules = [
            {
                "rule_name": rule.rule_name,
                "passed": rule.passed,
                "reason": rule.reason,
            }
            for rule in result.eligibility_result.unknown_rules
        ]

        evaluation.reasons = result.reasons

        self._session.flush()

        return evaluation