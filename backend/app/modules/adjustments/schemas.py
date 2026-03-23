import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.common.enums import AdjustmentType


class AdjustmentCreate(BaseModel):
    adjustment_type: AdjustmentType
    entity_type: str = Field(..., description="generator, fuel_stock, or oil_stock")
    entity_id: uuid.UUID
    value_before: Decimal
    value_after: Decimal
    reason: str = Field(..., min_length=1)
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
