import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class OutageCreate(BaseModel):
    outage_date: date
    hour_start: int = Field(..., ge=0, le=23)
    hour_end: int = Field(..., ge=1, le=24)
    note: str | None = None


class OutageResponse(BaseModel):
    id: uuid.UUID
    outage_date: date
    hour_start: int
    hour_end: int
    note: str | None
    created_by: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
