import uuid
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundException
from app.modules.outage.models import OutageSchedule
from app.modules.outage.repository import OutageRepository
from app.modules.outage.schemas import OutageScheduleCreate
from app.modules.users.models import User


class OutageService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OutageRepository(db)

    async def get_all(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> list[OutageSchedule]:
        return await self.repo.get_all(from_date=from_date, to_date=to_date)

    async def create(self, data: OutageScheduleCreate, current_user: User) -> OutageSchedule:
        outage = OutageSchedule(
            outage_date=data.outage_date,
            hour_start=data.hour_start,
            hour_end=data.hour_end,
            note=data.note,
            created_by=current_user.id,
        )
        return await self.repo.create(outage)

    async def delete(self, outage_id: uuid.UUID) -> None:
        outage = await self.repo.get_by_id(outage_id)
        if outage is None:
            raise NotFoundException(detail="Outage schedule entry not found")
        await self.repo.delete(outage)

    async def get_next(self) -> OutageSchedule | None:
        now = datetime.now(tz=timezone.utc)
        today = now.date()
        current_hour = now.hour
        return await self.repo.get_next(today, current_hour)
