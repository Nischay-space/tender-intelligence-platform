from datetime import datetime

from pydantic import BaseModel, ConfigDict


class IngestionRunResponse(BaseModel):
    id: int
    started_at: datetime
    finished_at: datetime | None
    status: str

    discovered: int
    successful: int
    failed: int
    skipped: int

    error: str | None

    model_config = ConfigDict(
        from_attributes=True
    )