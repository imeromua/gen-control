from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fuel.models import FuelDelivery
from app.modules.generators.models import EventLog
from app.modules.motohours.models import MaintenanceLog
from app.modules.shifts.models import Shift


class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_today_shifts(
        self, today_start: datetime, today_end: datetime
    ) -> list[Shift]:
        result = await self.db.execute(
            select(Shift)
            .where(Shift.started_at >= today_start, Shift.started_at < today_end)
            .order_by(Shift.started_at.desc())
        )
        return list(result.scalars().all())

    async def get_today_fuel_delivered_sum(
        self, today_start: datetime, today_end: datetime
    ) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(FuelDelivery.liters), 0)).where(
                FuelDelivery.delivered_at >= today_start,
                FuelDelivery.delivered_at < today_end,
            )
        )
        return Decimal(str(result.scalar_one()))

    async def has_maintenance_today(
        self, today_start: datetime, today_end: datetime
    ) -> bool:
        result = await self.db.execute(
            select(func.count(MaintenanceLog.id)).where(
                MaintenanceLog.performed_at >= today_start,
                MaintenanceLog.performed_at < today_end,
            )
        )
        return result.scalar_one() > 0

    async def get_recent_events(self, limit: int = 10) -> list[EventLog]:
        result = await self.db.execute(
            select(EventLog).order_by(EventLog.created_at.desc()).limit(limit)
        )
        return list(result.scalars().all())
