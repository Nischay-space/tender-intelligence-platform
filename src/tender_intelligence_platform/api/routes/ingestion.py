from fastapi import APIRouter, HTTPException

from tender_intelligence_platform.api.schemas.ingestion import (
    IngestionRunResponse,
)
from tender_intelligence_platform.database.connection import (
    SessionLocal,
)
from tender_intelligence_platform.repositories.ingestion_run_repository import (
    IngestionRunRepository,
)


router = APIRouter(
    prefix="/api/v1/ingestion",
    tags=["Ingestion"],
)


@router.get(
    "/status",
    response_model=IngestionRunResponse,
)
def get_ingestion_status():
    """Return the most recently started ingestion run."""

    with SessionLocal() as session:
        repository = IngestionRunRepository(session)

        run = repository.get_last_run()

        if run is None:
            raise HTTPException(
                status_code=404,
                detail="No ingestion runs recorded yet",
            )

        return run