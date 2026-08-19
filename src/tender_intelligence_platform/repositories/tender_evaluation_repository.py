from sqlalchemy import select
from sqlalchemy.orm import Session

from tender_intelligence_platform.database.models.tender_evaluation import (
    TenderEvaluationORM,
)
from tender_intelligence_platform.models.evaluation_result import (
    EvaluationResult,
)


class TenderEvaluationRepository:
    """Repository for tender evaluation persistence."""

    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        tender_db_id: int,
        evaluation: EvaluationResult,
    ) -> TenderEvaluationORM:
        """Create an evaluation record for a tender."""

        evaluation_orm = TenderEvaluationORM(
            tender_id=tender_db_id,
            keyword_status=evaluation.keyword_status,
            eligibility_status=evaluation.eligibility_status,
            final_status=evaluation.final_status,
            matched_keywords=evaluation.matched_keywords,
            excluded_keywords=evaluation.excluded_keywords,
            passed_rules=[
                rule.model_dump()
                for rule in evaluation.passed_rules
            ],
            failed_rules=[
                rule.model_dump()
                for rule in evaluation.failed_rules
            ],
            unknown_rules=[
                rule.model_dump()
                for rule in evaluation.unknown_rules
            ],
            reasons=evaluation.reasons,
        )

        self._session.add(evaluation_orm)

        return evaluation_orm

    def get_by_tender_id(
        self,
        tender_db_id: int,
    ) -> TenderEvaluationORM | None:
        """Get the evaluation belonging to a tender."""

        statement = select(
            TenderEvaluationORM
        ).where(
            TenderEvaluationORM.tender_id
            == tender_db_id
        )

        return self._session.scalar(statement)

    def update(
        self,
        evaluation_orm: TenderEvaluationORM,
        evaluation: EvaluationResult,
    ) -> TenderEvaluationORM:
        """Update an existing tender evaluation."""

        evaluation_orm.keyword_status = (
            evaluation.keyword_status
        )

        evaluation_orm.eligibility_status = (
            evaluation.eligibility_status
        )

        evaluation_orm.final_status = (
            evaluation.final_status
        )

        evaluation_orm.matched_keywords = (
            evaluation.matched_keywords
        )

        evaluation_orm.excluded_keywords = (
            evaluation.excluded_keywords
        )

        evaluation_orm.passed_rules = [
            rule.model_dump()
            for rule in evaluation.passed_rules
        ]

        evaluation_orm.failed_rules = [
            rule.model_dump()
            for rule in evaluation.failed_rules
        ]

        evaluation_orm.unknown_rules = [
            rule.model_dump()
            for rule in evaluation.unknown_rules
        ]

        evaluation_orm.reasons = (
            evaluation.reasons
        )

        return evaluation_orm

    def upsert(
        self,
        tender_db_id: int,
        evaluation: EvaluationResult,
    ) -> TenderEvaluationORM:
        """Create or update the evaluation for a tender."""

        existing = self.get_by_tender_id(
            tender_db_id
        )

        if existing is None:
            return self.create(
                tender_db_id,
                evaluation,
            )

        return self.update(
            existing,
            evaluation,
        )