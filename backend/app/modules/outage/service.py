import uuid
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.modules.outage.models import OutageSchedule
from app.modules.outage.repository import OutageRepository
from app.modules.outage.schemas import OutageCreate, OutageResponse


class OutageService:
    def __init__(self, db: AsyncSession):
        self.repo = OutageRepository(db)

    async def get_all(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[OutageResponse]:
        entries = await self.repo.get_all(from_date=from_date, to_date=to_date)
        return [OutageResponse.model_validate(e) for e in entries]

    async def get_next(self) -> OutageResponse | None:
        now = datetime.now(tz=timezone.utc)
        today = now.date()
        current_hour = now.hour
        entry = await self.repo.get_next(today, current_hour)
        if entry is None:
            return None
        return OutageResponse.model_validate(entry)

    async def create(self, data: OutageCreate, current_user_id: uuid.UUID) -> OutageResponse:
        outage = OutageSchedule(
            outage_date=data.outage_date,
            hour_start=data.hour_start,
            hour_end=data.hour_end,
            note=data.note,
            created_by=current_user_id,
        )
        created = await self.repo.create(outage)
        return OutageResponse.model_validate(created)

    async def delete(self, outage_id: uuid.UUID) -> None:
        outage = await self.repo.get_by_id(outage_id)
        if not outage:
            raise NotFoundException(detail=f"Outage schedule with id '{outage_id}' not found")
        await self.repo.delete(outage)
