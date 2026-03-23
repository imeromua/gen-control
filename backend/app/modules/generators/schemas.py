import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.common.enums import GeneratorType, FuelType


class GeneratorCreate(BaseModel):
    name: str
    type: GeneratorType
    model: str
    serial_number: str


class GeneratorUpdate(BaseModel):
    name: str | None = None
    type: GeneratorType | None = None
    model: str | None = None
    serial_number: str | None = None
    is_active: bool | None = None


class GeneratorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: str
    model: str
    serial_number: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class GeneratorSettingsUpdate(BaseModel):
    fuel_type: FuelType | None = None
    tank_capacity_liters: Decimal | None = None
    fuel_consumption_per_hour: Decimal | None = None
    fuel_warning_level: Decimal | None = None
    fuel_critical_level: Decimal | None = None
    to_interval_hours: Decimal | None = None
    to_warning_before_hours: Decimal | None = None
    max_continuous_work_hours: Decimal | None = None
    max_daily_hours: Decimal | None = None
    min_pause_between_starts_min: int | None = None
    expected_consumption_deviation_pct: Decimal | None = None
    initial_motohours: Decimal | None = None


class GeneratorSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    generator_id: uuid.UUID
    fuel_type: str | None
    tank_capacity_liters: Decimal | None
    fuel_consumption_per_hour: Decimal | None
    fuel_warning_level: Decimal | None
    fuel_critical_level: Decimal | None
    to_interval_hours: Decimal | None
    to_warning_before_hours: Decimal | None
    max_continuous_work_hours: Decimal | None
    max_daily_hours: Decimal | None
    min_pause_between_starts_min: int | None
    expected_consumption_deviation_pct: Decimal | None
    initial_motohours: Decimal | None
    updated_at: datetime
    updated_by: uuid.UUID | None


class GeneratorStatusResponse(BaseModel):
    generator_id: uuid.UUID
    name: str
    type: str
    is_active: bool
    fuel_type: str | None
    tank_capacity_liters: Decimal | None
    current_fuel_liters: Decimal | None
    motohours_total: Decimal
    motohours_since_last_to: Decimal
    next_to_at_hours: Decimal | None
    hours_to_next_to: Decimal | None
    to_warning_active: bool
    fuel_warning_active: bool
    fuel_critical_active: bool
