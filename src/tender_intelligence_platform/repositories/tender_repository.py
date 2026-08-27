from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from tender_intelligence_platform.database.models.tender import TenderORM
from tender_intelligence_platform.database.models.tender_evaluation import (
    TenderEvaluationORM,
)
from tender_intelligence_platform.models.tender import Tender


# Whitelist of columns GET /tenders is allowed to sort by. Keep this in
# sync with the SortableField Literal in api/routes/tenders.py.
SORTABLE_FIELDS = {
    "id": TenderORM.id,
    "created_at": TenderORM.created_at,
    "updated_at": TenderORM.updated_at,
    "estimated_value": TenderORM.estimated_value,
    "bid_submission_end_date": TenderORM.bid_submission_end_date,
}


class TenderRepository:
    """Repository for tender persistence operations."""

    def __init__(self, session: Session):
        self._session = session

    def get_by_tender_id(
        self,
        tender_id: str,
    ) -> TenderORM | None:
        """Return a tender by its business identifier."""

        statement = (
            select(TenderORM)
            .options(
                selectinload(TenderORM.evaluation)
            )
            .where(
                TenderORM.tender_id == tender_id
            )
        )

        return self._session.scalar(statement)

    def create(
        self,
        tender: Tender,
    ) -> TenderORM:
        """Create a new tender record."""

        tender_orm = TenderORM(
            **tender.model_dump()
        )

        self._session.add(tender_orm)
        self._session.flush()

        return tender_orm

    def update(
        self,
        existing: TenderORM,
        tender: Tender,
    ) -> TenderORM:
        """Update an existing tender record."""

        data = tender.model_dump()

        for field, value in data.items():
            setattr(existing, field, value)

        self._session.flush()

        return existing

    def upsert(
        self,
        tender: Tender,
    ) -> TenderORM:
        """
        Create a tender if it does not exist.
        Update it if it already exists.
        """

        existing = self.get_by_tender_id(
            tender.tender_id
        )

        if existing is None:
            return self.create(tender)

        return self.update(
            existing,
            tender,
        )

    def _apply_filters(
        self,
        statement,
        *,
        final_status: str | None,
        category: str | None,
        state: str | None,
        status: str | None,
    ):
        """Apply the shared filter set to a select statement."""

        if final_status is not None:
            statement = statement.join(
                TenderORM.evaluation
            ).where(
                TenderEvaluationORM.final_status
                == final_status
            )

        if category is not None:
            statement = statement.where(
                TenderORM.category == category
            )

        if state is not None:
            statement = statement.where(
                TenderORM.state == state
            )

        if status is not None:
            statement = statement.where(
                TenderORM.status == status
            )

        return statement

    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
        *,
        final_status: str | None = None,
        category: str | None = None,
        state: str | None = None,
        status: str | None = None,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> list[TenderORM]:
        """Return tenders with pagination, filtering, and sorting."""

        sort_column = SORTABLE_FIELDS.get(
            sort_by, TenderORM.id
        )

        order = (
            sort_column.desc()
            if sort_order == "desc"
            else sort_column.asc()
        )

        statement = select(TenderORM).options(
            selectinload(TenderORM.evaluation)
        )

        statement = self._apply_filters(
            statement,
            final_status=final_status,
            category=category,
            state=state,
            status=status,
        )

        statement = (
            statement.order_by(order)
            .offset(skip)
            .limit(limit)
        )

        return list(
            self._session.scalars(statement).all()
        )

    def count(
        self,
        *,
        final_status: str | None = None,
        category: str | None = None,
        state: str | None = None,
        status: str | None = None,
    ) -> int:
        """Return the total count of tenders matching the given filters."""

        statement = select(
            func.count()
        ).select_from(TenderORM)

        statement = self._apply_filters(
            statement,
            final_status=final_status,
            category=category,
            state=state,
            status=status,
        )

        return self._session.scalar(statement) or 0