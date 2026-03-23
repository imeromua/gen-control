import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FuelStockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fuel_type: str
    current_liters: Decimal
    max_limit_liters: Decimal
    warning_level_liters: Decimal
    updated_at: datetime


class FuelStockUpdate(BaseModel):
    max_limit_liters: Decimal | None = None
    warning_level_liters: Decimal | None = None


class FuelDeliveryCreate(BaseModel):
    liters: Decimal
    check_number: str | None = None
    delivered_by_name: str | None = None


class FuelDeliveryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fuel_type: str
    liters: Decimal
    check_number: str | None
    delivered_by_name: str | None
    accepted_by: uuid.UUID | None
    stock_before: Decimal
    stock_after: Decimal
    delivered_at: datetime


class FuelRefillCreate(BaseModel):
    generator_id: uuid.UUID
    liters: Decimal
    tank_level_before: Decimal


class FuelRefillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    generator_id: uuid.UUID
    performed_by: uuid.UUID | None
    liters: Decimal
    tank_level_before: Decimal
    tank_level_after: Decimal
    stock_before: Decimal
    stock_after: Decimal
    refilled_at: datetime
