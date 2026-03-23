import uuid
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.motohours.models import MotohoursLog, MaintenanceLog


class MotohoursRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_log_by_generator(self, generator_id: uuid.UUID) -> list[MotohoursLog]:
        result = await self.db.execute(
            select(MotohoursLog)
            .where(MotohoursLog.generator_id == generator_id)
            .order_by(MotohoursLog.recorded_at)
        )
        return list(result.scalars().all())

    async def get_hours_sum(self, generator_id: uuid.UUID) -> Decimal:
        result = await self.db.execute(
            select(func.coalesce(func.sum(MotohoursLog.hours_added), 0)).where(
                MotohoursLog.generator_id == generator_id
            )
        )
        return result.scalar_one()

    async def get_maintenance_log(self, generator_id: uuid.UUID) -> list[MaintenanceLog]:
        result = await self.db.execute(
            select(MaintenanceLog)
            .where(MaintenanceLog.generator_id == generator_id)
            .order_by(MaintenanceLog.performed_at)
        )
        return list(result.scalars().all())

    async def get_last_maintenance(self, generator_id: uuid.UUID) -> MaintenanceLog | None:
        result = await self.db.execute(
            select(MaintenanceLog)
            .where(MaintenanceLog.generator_id == generator_id)
            .order_by(MaintenanceLog.performed_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_hours_since_last_maintenance(self, generator_id: uuid.UUID) -> Decimal:
        last_maintenance = await self.get_last_maintenance(generator_id)
        if last_maintenance is None:
            return await self.get_hours_sum(generator_id)

        result = await self.db.execute(
            select(func.coalesce(func.sum(MotohoursLog.hours_added), 0)).where(
                MotohoursLog.generator_id == generator_id,
                MotohoursLog.recorded_at > last_maintenance.performed_at,
            )
        )
        return result.scalar_one()

    async def create_maintenance(self, maintenance: MaintenanceLog) -> MaintenanceLog:
        self.db.add(maintenance)
        await self.db.commit()
        await self.db.refresh(maintenance)
        return maintenance
