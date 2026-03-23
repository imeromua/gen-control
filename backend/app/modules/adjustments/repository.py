import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.adjustments.models import Adjustment


class AdjustmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Adjustment]:
        result = await self.db.execute(
            select(Adjustment).order_by(Adjustment.performed_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, adjustment_id: uuid.UUID) -> Adjustment | None:
        result = await self.db.execute(
            select(Adjustment).where(Adjustment.id == adjustment_id)
        )
        return result.scalar_one_or_none()

    async def create(self, adjustment: Adjustment) -> Adjustment:
        self.db.add(adjustment)
        await self.db.commit()
        await self.db.refresh(adjustment)
        return adjustment
