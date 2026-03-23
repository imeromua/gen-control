import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.common.enums import AdjustmentType


class AdjustmentCreate(BaseModel):
    adjustment_type: AdjustmentType
    entity_type: str
    entity_id: uuid.UUID
    value_before: Decimal
    value_after: Decimal
    reason: str
    document_ref: str | None = None


class AdjustmentResponse(BaseModel):
    id: uuid.UUID
    adjustment_type: str
    entity_type: str
    entity_id: uuid.UUID
    value_before: Decimal
    value_after: Decimal
    delta: Decimal
    reason: str
    document_ref: str | None
    performed_by: uuid.UUID | None
    performed_at: datetime

    model_config = {"from_attributes": True}
