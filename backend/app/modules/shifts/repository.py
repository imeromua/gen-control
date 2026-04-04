import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.shifts.models import Shift, SystemSettings


class SystemSettingsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self) -> SystemSettings | None:
        result = await self.db.execute(select(SystemSettings).limit(1))
        return result.scalar_one_or_none()

    async def update(self, settings: SystemSettings) -> SystemSettings:
        await self.db.flush()
        await self.db.refresh(settings)
        return settings


def _shift_query_with_joins():
    """Base select that eagerly loads Generator and started_by User."""
    from app.modules.generators.models import Generator
    from app.modules.users.models import User as UserModel

    return (
        select(Shift)
        .options(
            joinedload(Shift.generator),
            joinedload(Shift.operator),
        )
    )


class ShiftRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        generator_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[Shift]:
        query = _shift_query_with_joins().order_by(Shift.started_at.desc())
        if generator_id is not None:
            query = query.where(Shift.generator_id == generator_id)
        if status is not None:
            query = query.where(Shift.status == status)
        result = await self.db.execute(query)
        return list(result.unique().scalars().all())

    async def get_by_id(self, shift_id: uuid.UUID) -> Shift | None:
        result = await self.db.execute(
            _shift_query_with_joins().where(Shift.id == shift_id)
        )
        return result.unique().scalar_one_or_none()

    async def get_any_active(self) -> Shift | None:
        result = await self.db.execute(
            _shift_query_with_joins().where(Shift.status == "ACTIVE").limit(1)
        )
        return result.unique().scalar_one_or_none()

    async def get_active_for_generator(self, generator_id: uuid.UUID) -> Shift | None:
        result = await self.db.execute(
            select(Shift)
            .where(Shift.generator_id == generator_id, Shift.status == "ACTIVE")
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_last_closed_for_generator(self, generator_id: uuid.UUID) -> Shift | None:
        result = await self.db.execute(
            select(Shift)
            .where(Shift.generator_id == generator_id, Shift.status == "CLOSED")
            .order_by(Shift.stopped_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_next_shift_number(self) -> int:
        result = await self.db.execute(select(func.max(Shift.shift_number)))
        max_number = result.scalar_one_or_none()
        return (max_number or 0) + 1

    async def create(self, shift: Shift) -> Shift:
        self.db.add(shift)
        await self.db.flush()
        await self.db.refresh(shift)
        return shift

    async def update(self, shift: Shift) -> Shift:
        await self.db.flush()
        await self.db.refresh(shift)
        return shift
