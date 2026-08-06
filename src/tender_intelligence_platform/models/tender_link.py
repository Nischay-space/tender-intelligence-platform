from datetime import datetime

from pydantic import BaseModel, HttpUrl


class TenderLink(BaseModel):
    title: str
    reference_number: str
    detail_url: HttpUrl
    closing_date: datetime
    opening_date: datetime