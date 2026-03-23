import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.modules.eventlog.repository import EventLogRepository
from app.modules.generators.models import EventLog


class EventLogService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EventLogRepository(db)

    async def get_all(
        self,
        event_type: str | None = None,
        generator_id: uuid.UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[EventLog]:
        return await self.repo.get_all(
            event_type=event_type,
            generator_id=generator_id,
            from_date=from_date,
            to_date=to_date,
        )

    async def get_by_id(self, event_id: uuid.UUID) -> EventLog:
        event = await self.repo.get_by_id(event_id)
        if event is None:
            raise NotFoundException(detail="Event not found")
        return event
