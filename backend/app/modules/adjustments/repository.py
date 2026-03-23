import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.adjustments.models import Adjustment, FuelStock, OilStock


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

    async def get_fuel_stock(self, stock_id: uuid.UUID) -> FuelStock | None:
        result = await self.db.execute(
            select(FuelStock).where(FuelStock.id == stock_id)
        )
        return result.scalar_one_or_none()

    async def get_oil_stock(self, stock_id: uuid.UUID) -> OilStock | None:
        result = await self.db.execute(
            select(OilStock).where(OilStock.id == stock_id)
        )
        return result.scalar_one_or_none()

    async def update_fuel_stock(self, stock: FuelStock) -> None:
        await self.db.commit()

    async def update_oil_stock(self, stock: OilStock) -> None:
        await self.db.commit()
