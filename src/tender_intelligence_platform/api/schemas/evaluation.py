from datetime import datetime

from pydantic import BaseModel


class RuleResultResponse(BaseModel):
    rule_name: str
    passed: bool
    reason: str


class TenderEvaluationResponse(BaseModel):
    id: int
    tender_id: int

    keyword_status: str
    eligibility_status: str
    final_status: str

    matched_keywords: list[str]
    excluded_keywords: list[str]

    passed_rules: list[RuleResultResponse]
    failed_rules: list[RuleResultResponse]
    unknown_rules: list[RuleResultResponse]

    reasons: list[str]

    evaluated_at: datetime