import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.motohours.models import MaintenanceLog, MotohoursLog


class MotohoursRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_log(self, generator_id: uuid.UUID) -> list[MotohoursLog]:
        result = await self.db.execute(
            select(MotohoursLog)
            .where(MotohoursLog.generator_id == generator_id)
            .order_by(MotohoursLog.recorded_at)
        )
        return list(result.scalars().all())

    async def get_total_hours_added(self, generator_id: uuid.UUID) -> float:
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

    async def get_motohours_since_last_maintenance(self, generator_id: uuid.UUID) -> float:
        last = await self.get_last_maintenance(generator_id)
        if last is None:
            return await self.get_total_hours_added(generator_id)
        result = await self.db.execute(
            select(func.coalesce(func.sum(MotohoursLog.hours_added), 0)).where(
                MotohoursLog.generator_id == generator_id,
                MotohoursLog.recorded_at > last.performed_at,
            )
        )
        return result.scalar_one()

    async def create_maintenance(self, entry: MaintenanceLog) -> MaintenanceLog:
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def create_log_entry(self, entry: MotohoursLog) -> MotohoursLog:
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry
