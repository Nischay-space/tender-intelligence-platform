from pydantic import BaseModel


class TenderEvaluationResponse(BaseModel):
    keyword_status: str
    eligibility_status: str
    final_status: str

    matched_keywords: list[str]
    excluded_keywords: list[str]

    passed_rules: list[dict]
    failed_rules: list[dict]
    unknown_rules: list[dict]

    reasons: list[str]


class TenderResponse(BaseModel):
    id: int
    tender_id: str
    tender_title: str

    organization: str | None = None
    tender_reference_number: str | None = None
    tender_url: str

    published_date: str | None = None
    bid_submission_start_date: str | None = None
    bid_submission_end_date: str | None = None
    opening_date: str | None = None

    estimated_value: float | None = None
    earnest_money_deposit: float | None = None
    tender_fee: float | None = None
    currency: str | None = None

    tender_type: str | None = None
    category: str | None = None
    procurement_type: str | None = None

    state: str | None = None
    city: str | None = None
    work_location: str | None = None

    status: str | None = None
    withdrawal_allowed: bool | None = None

    form_of_contract: str | None = None
    payment_mode: str | None = None
    work_description: str | None = None

    created_at: str
    updated_at: str

    evaluation: TenderEvaluationResponse | None = None