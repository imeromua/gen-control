import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class MotohoursLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    generator_id: uuid.UUID
    shift_id: uuid.UUID | None
    hours_added: Decimal
    total_after: Decimal
    recorded_at: datetime


class MotohoursTotalResponse(BaseModel):
    generator_id: uuid.UUID
    motohours_total: Decimal


class MaintenanceCreate(BaseModel):
    notes: str | None = None


class MaintenanceLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    generator_id: uuid.UUID
    performed_by: uuid.UUID | None
    motohours_at_service: Decimal
    next_service_at_hours: Decimal | None
    notes: str | None
    performed_at: datetime
