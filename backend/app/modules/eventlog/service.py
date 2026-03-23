import uuid
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.modules.eventlog.repository import EventLogRepository
from app.modules.eventlog.schemas import EventLogResponse


class EventLogService:
    def __init__(self, db: AsyncSession):
        self.repo = EventLogRepository(db)

    async def get_all(
        self,
        event_type: str | None = None,
        generator_id: uuid.UUID | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[EventLogResponse]:
        entries = await self.repo.get_all(
            event_type=event_type,
            generator_id=generator_id,
            from_date=from_date,
            to_date=to_date,
        )
        return [EventLogResponse.model_validate(e) for e in entries]

    async def get_by_id(self, event_id: uuid.UUID) -> EventLogResponse:
        entry = await self.repo.get_by_id(event_id)
        if not entry:
            raise NotFoundException(detail=f"Event with id '{event_id}' not found")
        return EventLogResponse.model_validate(entry)
