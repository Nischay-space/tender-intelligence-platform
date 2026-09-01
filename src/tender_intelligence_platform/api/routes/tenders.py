from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from tender_intelligence_platform.api.schemas.evaluation import (
    TenderEvaluationResponse,
)
from tender_intelligence_platform.api.schemas.stats import (
    TenderStatsResponse,
)
from tender_intelligence_platform.api.schemas.tender import (
    TenderFacetsResponse,
    TenderListResponse,
    TenderResponse,
)
from tender_intelligence_platform.database.connection import (
    SessionLocal,
)
from tender_intelligence_platform.repositories.tender_evaluation_repository import (
    TenderEvaluationRepository,
)
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)


router = APIRouter(
    prefix="/api/v1/tenders",
    tags=["Tenders"],
)


# Keep in sync with SORTABLE_FIELDS in repositories/tender_repository.py
SortableField = Literal[
    "id",
    "created_at",
    "updated_at",
    "estimated_value",
    "bid_submission_end_date",
]


@router.get(
    "",
    response_model=TenderListResponse,
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
    search: str | None = Query(
        None,
        min_length=1,
        max_length=200,
        description=(
            "Case-insensitive substring match against tender title "
            "or organization"
        ),
    ),
    final_status: str | None = Query(
        None,
        description=(
            "Filter by evaluation final status, e.g. "
            "QUALIFIED, FILTERED_OUT, NOT_ELIGIBLE, REVIEW_REQUIRED"
        ),
    ),
    category: str | None = Query(
        None,
        description="Filter by tender category",
    ),
    state: str | None = Query(
        None,
        description="Filter by tender state",
    ),
    status: str | None = Query(
        None,
        description="Filter by tender status, e.g. Open",
    ),
    sort_by: SortableField = Query(
        "id",
        description="Field to sort by",
    ),
    sort_order: Literal["asc", "desc"] = Query(
        "desc",
        description="Sort direction",
    ),
):
    """Return stored tenders with pagination, filtering, sorting, and search."""

    with SessionLocal() as session:
        repository = TenderRepository(session)

        filters = dict(
            search=search,
            final_status=final_status,
            category=category,
            state=state,
            status=status,
        )

        items = repository.get_all(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            **filters,
        )

        total = repository.count(**filters)

        return TenderListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
        )


@router.get(
    "/stats",
    response_model=TenderStatsResponse,
)
def get_tender_stats():
    """Return aggregate tender counts by evaluation outcome, for dashboards."""

    with SessionLocal() as session:
        repository = TenderRepository(session)

        counts = repository.get_status_counts()
        total = repository.count()

        return TenderStatsResponse(
            total=total,
            qualified=counts.get("QUALIFIED", 0),
            filtered_out=counts.get("FILTERED_OUT", 0),
            not_eligible=counts.get("NOT_ELIGIBLE", 0),
            review_required=counts.get("REVIEW_REQUIRED", 0),
            unevaluated=counts.get(None, 0),
        )


@router.get(
    "/facets",
    response_model=TenderFacetsResponse,
)
def get_tender_facets():
    """
    Return the distinct category and state values actually present in
    the data, for populating real dropdown filters in the dashboard
    instead of free-text inputs.
    """

    with SessionLocal() as session:
        repository = TenderRepository(session)

        facets = repository.get_facets()

        return TenderFacetsResponse(**facets)


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