from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload
from tender_intelligence_platform.database.models.tender import TenderORM
from tender_intelligence_platform.database.models.tender_evaluation import (
    TenderEvaluationORM,
)
from tender_intelligence_platform.models.tender import Tender


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
        search: str | None = None,
        final_status: str | None = None,
        category: str | None = None,
        state: str | None = None,
        status: str | None = None,
    ):
        """Apply the shared filter set to a select statement."""

        if search is not None:
            like_pattern = f"%{search}%"

            statement = statement.where(
                or_(
                    TenderORM.tender_title.ilike(like_pattern),
                    TenderORM.organization.ilike(like_pattern),
                )
            )

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
        search: str | None = None,
        final_status: str | None = None,
        category: str | None = None,
        state: str | None = None,
        status: str | None = None,
        sort_by: str = "id",
        sort_order: str = "desc",
    ) -> list[TenderORM]:
        """Return tenders with pagination, filtering, sorting, and search."""

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
            search=search,
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
        search: str | None = None,
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
            search=search,
            final_status=final_status,
            category=category,
            state=state,
            status=status,
        )

        return self._session.scalar(statement) or 0

    def get_facets(self) -> dict[str, list[str]]:
        """Return distinct category and state values present in the data."""

        categories = self._session.scalars(
            select(TenderORM.category)
            .where(TenderORM.category.is_not(None))
            .distinct()
            .order_by(TenderORM.category)
        ).all()

        states = self._session.scalars(
            select(TenderORM.state)
            .where(TenderORM.state.is_not(None))
            .distinct()
            .order_by(TenderORM.state)
        ).all()

        return {
            "categories": list(categories),
            "states": list(states),
        }

    def get_status_counts(self) -> dict:
        """
        Return tender counts grouped by evaluation final_status.

        Tenders with no evaluation yet are grouped under the key None,
        via the LEFT JOIN — an INNER JOIN would silently drop them.
        """

        statement = (
            select(
                TenderEvaluationORM.final_status,
                func.count(TenderORM.id),
            )
            .select_from(TenderORM)
            .outerjoin(TenderORM.evaluation)
            .group_by(TenderEvaluationORM.final_status)
        )

        rows = self._session.execute(statement).all()

        return {
            final_status: count
            for final_status, count in rows
        }