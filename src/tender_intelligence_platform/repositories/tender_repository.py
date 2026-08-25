from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from tender_intelligence_platform.database.models.tender import TenderORM
from tender_intelligence_platform.models.tender import Tender
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
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> list[TenderORM]:
        """Return tenders with pagination and evaluations."""

        statement = (
            select(TenderORM)
            .options(
                selectinload(TenderORM.evaluation)
            )
            .order_by(TenderORM.id.desc())
            .offset(skip)
            .limit(limit)
        )

        return list(
            self._session.scalars(statement).all()
        )
        