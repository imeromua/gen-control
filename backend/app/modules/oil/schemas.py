import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class OilStockCreate(BaseModel):
    generator_id: uuid.UUID
    oil_type: str
    current_quantity: Decimal = Decimal("0")
    unit: str = "LITERS"


class OilStockUpdate(BaseModel):
    current_quantity: Decimal | None = None
    oil_type: str | None = None
    unit: str | None = None


class OilStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    generator_id: uuid.UUID
    oil_type: str
    current_quantity: Decimal
    unit: str
    updated_at: datetime
