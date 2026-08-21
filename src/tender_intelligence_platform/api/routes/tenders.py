from fastapi import APIRouter

from tender_intelligence_platform.api.schemas.tender import (
    TenderResponse,
)
from tender_intelligence_platform.database.connection import (
    SessionLocal,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)


router = APIRouter(
    prefix="/api/v1/tenders",
    tags=["Tenders"],
)


@router.get(
    "",
    response_model=list[TenderResponse],
)
def get_tenders():
    """Return all stored tenders."""

    with SessionLocal() as session:
        repository = TenderRepository(session)

        tenders = repository.get_all()

        return tenders