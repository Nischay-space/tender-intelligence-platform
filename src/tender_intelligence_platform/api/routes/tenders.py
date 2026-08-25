from fastapi import APIRouter, HTTPException, Query

from tender_intelligence_platform.api.schemas.tender import (
    TenderResponse,
)
from tender_intelligence_platform.database.connection import (
    SessionLocal,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)
from tender_intelligence_platform.api.schemas.evaluation import (
    TenderEvaluationResponse,
)
from tender_intelligence_platform.repositories.tender_evaluation_repository import (
    TenderEvaluationRepository,
)


router = APIRouter(
    prefix="/api/v1/tenders",
    tags=["Tenders"],
)


@router.get(
    "",
    response_model=list[TenderResponse],
)
def get_tenders(
    skip: int = Query(
        0,
        ge=0,
        description="Number of tenders to skip",
    ),
    limit: int = Query(
        50,
        ge=1,
        le=100,
        description="Maximum number of tenders to return",
    ),
):
    """Return stored tenders with pagination."""

    with SessionLocal() as session:
        repository = TenderRepository(session)

        return repository.get_all(
            skip=skip,
            limit=limit,
        )   


@router.get(
    "/{tender_id}/evaluation",
    response_model=TenderEvaluationResponse,
)
def get_tender_evaluation(
    tender_id: str,
):
    """Return the evaluation for a tender."""

    with SessionLocal() as session:
        tender_repository = TenderRepository(
            session
        )

        tender = tender_repository.get_by_tender_id(
            tender_id
        )

        if tender is None:
            raise HTTPException(
                status_code=404,
                detail=f"Tender '{tender_id}' not found",
            )

        evaluation_repository = TenderEvaluationRepository(
            session
        )

        evaluation = evaluation_repository.get_by_tender_id(
            tender.id
        )

        if evaluation is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Evaluation for tender "
                    f"'{tender_id}' not found"
                ),
            )

        return evaluation





@router.get(
    "/{tender_id}",
    response_model=TenderResponse,
)
def get_tender(tender_id: str):
    """Return a single tender by its business identifier."""

    with SessionLocal() as session:
        repository = TenderRepository(session)

        tender = repository.get_by_tender_id(
            tender_id
        )

        if tender is None:
            raise HTTPException(
                status_code=404,
                detail=f"Tender '{tender_id}' not found",
            )

        return tender

