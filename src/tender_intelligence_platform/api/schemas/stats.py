from pydantic import BaseModel


class TenderStatsResponse(BaseModel):
    """Aggregate counts of tenders by evaluation outcome, for dashboards."""

    total: int
    qualified: int
    filtered_out: int
    not_eligible: int
    review_required: int
    unevaluated: int