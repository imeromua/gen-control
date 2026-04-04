import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import EventType
from app.common.exceptions import NotFoundException
from app.modules.generators.models import EventLog
from app.modules.generators.repository import GeneratorRepository
from app.modules.oil.models import OilStock
from app.modules.oil.repository import OilRepository
from app.modules.oil.schemas import OilStockCreate, OilStockUpdate
from app.modules.users.models import User


class OilService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OilRepository(db)
        self.gen_repo = GeneratorRepository(db)

    async def get_all(self) -> list[OilStock]:
        return await self.repo.get_all()

    async def create(self, data: OilStockCreate, current_user: User) -> OilStock:
        oil_stock = OilStock(
            generator_id=data.generator_id,
            oil_type=data.oil_type,
            current_quantity=data.current_quantity,
            unit=data.unit,
        )

        created = await self.repo.create(oil_stock)

        await self.gen_repo.add_event(
            EventLog(
                event_type=EventType.OIL_STOCK_UPDATED.value,
                generator_id=data.generator_id,
                performed_by=current_user.id,
                meta={
                    "oil_type": data.oil_type,
                    "current_quantity": float(data.current_quantity),
                    "unit": data.unit,
                },
            )
        )

        await self.db.flush()
        return created

    async def update(
        self, oil_id: uuid.UUID, data: OilStockUpdate, current_user: User
    ) -> OilStock:
        oil_stock = await self.repo.get_by_id(oil_id)
        if oil_stock is None:
            raise NotFoundException(detail=f"Oil stock with id '{oil_id}' not found")

        if data.current_quantity is not None:
            oil_stock.current_quantity = data.current_quantity
        if data.oil_type is not None:
            oil_stock.oil_type = data.oil_type
        if data.unit is not None:
            oil_stock.unit = data.unit

        updated = await self.repo.update(oil_stock)

        await self.gen_repo.add_event(
            EventLog(
                event_type=EventType.OIL_STOCK_UPDATED.value,
                generator_id=updated.generator_id,
                performed_by=current_user.id,
                meta={
                    "oil_id": str(oil_id),
                    "current_quantity": float(updated.current_quantity),
                    "unit": updated.unit,
                },
            )
        )

        await self.db.flush()
        return updated
