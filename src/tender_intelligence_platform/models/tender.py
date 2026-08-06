from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, HttpUrl, Field

class TenderStatus(str, Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"


class ProcurementType(str, Enum):
    GOODS = "Goods"
    WORKS = "Works"
    SERVICES = "Services"

class TenderDocument(BaseModel):

    name: str

    document_type: str

    description: str | None = None

    download_url: HttpUrl

    size_kb: float | None = None
    
    

class Tender(BaseModel):

    tender_id: str
    reference_number: str | None = None

    title: str
    description: str | None = None

    organization: str
    tender_url: HttpUrl

    procurement_type: ProcurementType
    tender_type: str

    estimated_value: Decimal | None = None
    currency: str = "INR"

    tender_fee: Decimal | None = None
    emd_amount: Decimal | None = None

    published_date: datetime | None = None
    bid_start_date: datetime | None = None
    bid_end_date: datetime | None = None
    bid_opening_date: datetime | None = None

    work_location: str | None = None
    documents: list[TenderDocument] = Field(default_factory=list)

    status: TenderStatus

