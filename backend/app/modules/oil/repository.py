import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.oil.models import OilStock


class OilRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[OilStock]:
        result = await self.db.execute(select(OilStock).order_by(OilStock.updated_at.desc()))
        return list(result.scalars().all())

    async def get_by_id(self, oil_id: uuid.UUID) -> OilStock | None:
        result = await self.db.execute(select(OilStock).where(OilStock.id == oil_id))
        return result.scalar_one_or_none()

    async def create(self, oil_stock: OilStock) -> OilStock:
        self.db.add(oil_stock)
        await self.db.commit()
        await self.db.refresh(oil_stock)
        return oil_stock

    async def update(self, oil_stock: OilStock) -> OilStock:
        await self.db.commit()
        await self.db.refresh(oil_stock)
        return oil_stock
