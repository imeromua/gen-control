import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import AdjustmentType, EventType
from app.common.exceptions import NotFoundException
from app.modules.adjustments.models import Adjustment
from app.modules.adjustments.repository import AdjustmentRepository
from app.modules.adjustments.schemas import AdjustmentCreate
from app.modules.fuel.repository import FuelRepository
from app.modules.generators.models import EventLog
from app.modules.generators.repository import GeneratorRepository
from app.modules.motohours.models import MotohoursLog
from app.modules.motohours.repository import MotohoursRepository
from app.modules.oil.repository import OilRepository
from app.modules.users.models import User


class AdjustmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AdjustmentRepository(db)
        self.gen_repo = GeneratorRepository(db)
        self.fuel_repo = FuelRepository(db)
        self.oil_repo = OilRepository(db)
        self.motohours_repo = MotohoursRepository(db)

    async def get_all(self) -> list[Adjustment]:
        return await self.repo.get_all()

    async def get_by_id(self, adjustment_id: uuid.UUID) -> Adjustment:
        adjustment = await self.repo.get_by_id(adjustment_id)
        if adjustment is None:
            raise NotFoundException(detail="Adjustment not found")
        return adjustment

    async def create(self, data: AdjustmentCreate, current_user: User) -> Adjustment:
        delta = Decimal(str(data.value_after)) - Decimal(str(data.value_before))

        adjustment = Adjustment(
            adjustment_type=data.adjustment_type.value,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            value_before=data.value_before,
            value_after=data.value_after,
            delta=delta,
            reason=data.reason,
            document_ref=data.document_ref,
            performed_by=current_user.id,
        )

        async with self.db.begin():
            created = await self.repo.create(adjustment)

            if data.adjustment_type == AdjustmentType.MOTOHOURS_ADJUST:
                total = await self.motohours_repo.get_total_hours_added(data.entity_id)
                log = MotohoursLog(
                    generator_id=data.entity_id,
                    shift_id=None,
                    hours_added=delta,
                    total_after=Decimal(str(total)) + delta,
                )
                self.db.add(log)

            elif data.adjustment_type == AdjustmentType.FUEL_STOCK_ADJUST:
                stock = await self.fuel_repo.get_stock()
                if stock is not None:
                    stock.current_liters = data.value_after
                    await self.fuel_repo.update_stock(stock)

            elif data.adjustment_type == AdjustmentType.OIL_STOCK_ADJUST:
                oil = await self.oil_repo.get_by_id(data.entity_id)
                if oil is not None:
                    oil.current_quantity = data.value_after
                    await self.oil_repo.update(oil)

            await self.gen_repo.add_event(
                EventLog(
                    event_type=EventType.ADJUSTMENT_CREATED.value,
                    generator_id=None,
                    performed_by=current_user.id,
                    meta={
                        "adjustment_id": str(created.id),
                        "adjustment_type": data.adjustment_type.value,
                        "entity_type": data.entity_type,
                        "entity_id": str(data.entity_id),
                        "delta": float(delta),
                    },
                )
            )

        return created
