import uuid
from datetime import date

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.outage.models import OutageSchedule


class OutageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[OutageSchedule]:
        query = select(OutageSchedule).order_by(
            OutageSchedule.outage_date, OutageSchedule.hour_start
        )
        if from_date is not None:
            query = query.where(OutageSchedule.outage_date >= from_date)
        if to_date is not None:
            query = query.where(OutageSchedule.outage_date <= to_date)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, outage_id: uuid.UUID) -> OutageSchedule | None:
        result = await self.db.execute(
            select(OutageSchedule).where(OutageSchedule.id == outage_id)
        )
        return result.scalar_one_or_none()

    async def create(self, outage: OutageSchedule) -> OutageSchedule:
        self.db.add(outage)
        await self.db.flush()
        await self.db.refresh(outage)
        return outage

    async def delete(self, outage: OutageSchedule) -> None:
        await self.db.delete(outage)
        await self.db.flush()

    async def get_next(self, today: date, current_hour: int) -> OutageSchedule | None:
        result = await self.db.execute(
            select(OutageSchedule)
            .where(
                or_(
                    OutageSchedule.outage_date > today,
                    and_(
                        OutageSchedule.outage_date == today,
                        OutageSchedule.hour_start > current_hour,
                    ),
                )
            )
            .order_by(OutageSchedule.outage_date, OutageSchedule.hour_start)
            .limit(1)
        )
        return result.scalar_one_or_none()
