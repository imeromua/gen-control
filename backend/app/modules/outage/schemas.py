import uuid
from datetime import date, datetime

from pydantic import BaseModel, field_validator


class OutageScheduleCreate(BaseModel):
    outage_date: date
    hour_start: int
    hour_end: int
    note: str | None = None

    @field_validator("hour_start")
    @classmethod
    def validate_hour_start(cls, v: int) -> int:
        if not 0 <= v <= 23:
            raise ValueError("hour_start must be between 0 and 23")
        return v

    @field_validator("hour_end")
    @classmethod
    def validate_hour_end(cls, v: int) -> int:
        if not 1 <= v <= 24:
            raise ValueError("hour_end must be between 1 and 24")
        return v


class OutageScheduleResponse(BaseModel):
    id: uuid.UUID
    outage_date: date
    hour_start: int
    hour_end: int
    note: str | None
    created_by: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
