import uuid
from datetime import date

from sqlalchemy import cast, Date, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.generators.models import EventLog


class EventLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        event_type: str | None = None,
        generator_id: uuid.UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[EventLog]:
        query = select(EventLog).order_by(EventLog.created_at.desc())
        if event_type is not None:
            query = query.where(EventLog.event_type == event_type)
        if generator_id is not None:
            query = query.where(EventLog.generator_id == generator_id)
        if from_date is not None:
            query = query.where(cast(EventLog.created_at, Date) >= from_date)
        if to_date is not None:
            query = query.where(cast(EventLog.created_at, Date) <= to_date)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, event_id: uuid.UUID) -> EventLog | None:
        result = await self.db.execute(
            select(EventLog).where(EventLog.id == event_id)
        )
        return result.scalar_one_or_none()
