import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.fuel.models import FuelDelivery, FuelRefill, FuelStock


class FuelRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_stock(self) -> FuelStock | None:
        result = await self.db.execute(select(FuelStock).limit(1))
        return result.scalar_one_or_none()

    async def create_stock(self, stock: FuelStock) -> FuelStock:
        self.db.add(stock)
        await self.db.flush()
        await self.db.refresh(stock)
        return stock

    async def update_stock(self, stock: FuelStock) -> FuelStock:
        await self.db.flush()
        await self.db.refresh(stock)
        return stock

    async def get_deliveries(self) -> list[FuelDelivery]:
        result = await self.db.execute(
            select(FuelDelivery).order_by(FuelDelivery.delivered_at.desc())
        )
        return list(result.scalars().all())

    async def create_delivery(self, delivery: FuelDelivery) -> FuelDelivery:
        self.db.add(delivery)
        await self.db.flush()
        await self.db.refresh(delivery)
        return delivery

    async def get_refills(self) -> list[FuelRefill]:
        result = await self.db.execute(
            select(FuelRefill).order_by(FuelRefill.refilled_at.desc())
        )
        return list(result.scalars().all())

    async def create_refill(self, refill: FuelRefill) -> FuelRefill:
        self.db.add(refill)
        await self.db.flush()
        await self.db.refresh(refill)
        return refill
