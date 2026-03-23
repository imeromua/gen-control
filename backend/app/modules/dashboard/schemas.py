import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class ActiveShiftSchema(BaseModel):
    id: uuid.UUID
    shift_number: int
    generator_id: uuid.UUID
    generator_name: str
    started_at: datetime
    started_by_name: str | None
    duration_minutes: float
    fuel_consumed_estimate_liters: float | None


class GeneratorDashboardSchema(BaseModel):
    id: uuid.UUID
    name: str
    type: str
    is_active: bool
    motohours_total: Decimal
    motohours_since_last_to: Decimal
    hours_to_next_to: Decimal | None
    to_warning_active: bool
    fuel_type: str | None
    tank_capacity_liters: Decimal | None


class FuelStockSchema(BaseModel):
    fuel_type: str
    current_liters: Decimal
    max_limit_liters: Decimal
    warning_level_liters: Decimal
    warning_active: bool
    critical_active: bool


class OilStockSchema(BaseModel):
    id: uuid.UUID
    generator_id: uuid.UUID
    generator_name: str
    oil_type: str
    current_quantity: Decimal
    unit: str


class NextOutageSchema(BaseModel):
    outage_date: date
    hour_start: int
    hour_end: int
    note: str | None


class TodayStatsSchema(BaseModel):
    shifts_count: int
    total_hours_worked: float
    total_fuel_consumed_liters: float
    total_fuel_delivered_liters: float
    maintenance_performed: bool


class RecentEventSchema(BaseModel):
    id: uuid.UUID
    event_type: str
    generator_name: str | None
    created_at: datetime
    meta: dict | None


class DashboardResponse(BaseModel):
    generated_at: datetime
    active_shift: ActiveShiftSchema | None
    generators: list[GeneratorDashboardSchema]
    fuel_stock: FuelStockSchema | None
    oil_stocks: list[OilStockSchema]
    next_outage: NextOutageSchema | None
    today_stats: TodayStatsSchema
    recent_events: list[RecentEventSchema]


class DashboardSummaryResponse(BaseModel):
    generated_at: datetime
    generator_is_running: bool
    active_shift_number: int | None
    active_shift_duration_minutes: float | None
    fuel_stock_liters: Decimal | None
    fuel_warning_active: bool
    next_outage_date: date | None
    next_outage_hour_start: int | None
    next_outage_hour_end: int | None
