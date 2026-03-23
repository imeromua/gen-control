import uuid
from datetime import datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ShiftStartRequest(BaseModel):
    generator_id: uuid.UUID


class ShiftResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    shift_number: int
    generator_id: uuid.UUID
    started_by: uuid.UUID | None
    started_at: datetime
    stopped_by: uuid.UUID | None
    stopped_at: datetime | None
    duration_minutes: Decimal | None
    fuel_consumed_liters: Decimal | None
    motohours_accumulated: Decimal | None
    status: str
    created_at: datetime


class WorkTimeUpdate(BaseModel):
    work_time_start: time
    work_time_end: time


class WorkTimeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    work_time_start: time
    work_time_end: time
    updated_by: uuid.UUID | None
    updated_at: datetime
