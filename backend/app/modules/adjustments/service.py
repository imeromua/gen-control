import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import AdjustmentType, EventType
from app.common.exceptions import NotFoundException
from app.modules.adjustments.models import Adjustment
from app.modules.adjustments.repository import AdjustmentRepository
from app.modules.adjustments.schemas import AdjustmentCreate, AdjustmentResponse
from app.modules.generators.models import EventLog
from app.modules.generators.repository import GeneratorRepository
from app.modules.motohours.models import MotohoursLog
from app.modules.motohours.repository import MotohoursRepository


class AdjustmentService:
    def __init__(self, db: AsyncSession):
        self.repo = AdjustmentRepository(db)
        self.gen_repo = GeneratorRepository(db)
        self.moto_repo = MotohoursRepository(db)

    async def get_all(self) -> list[AdjustmentResponse]:
        entries = await self.repo.get_all()
        return [AdjustmentResponse.model_validate(e) for e in entries]

    async def get_by_id(self, adjustment_id: uuid.UUID) -> AdjustmentResponse:
        entry = await self.repo.get_by_id(adjustment_id)
        if not entry:
            raise NotFoundException(detail=f"Adjustment with id '{adjustment_id}' not found")
        return AdjustmentResponse.model_validate(entry)

    async def create(self, data: AdjustmentCreate, current_user_id: uuid.UUID) -> AdjustmentResponse:
        delta = data.value_after - data.value_before

        adjustment = Adjustment(
            adjustment_type=data.adjustment_type.value,
            entity_type=data.entity_type,
            entity_id=data.entity_id,
            value_before=data.value_before,
            value_after=data.value_after,
            delta=delta,
            reason=data.reason,
            document_ref=data.document_ref,
            performed_by=current_user_id,
        )
        created = await self.repo.create(adjustment)

        await self._apply_side_effects(data, delta, current_user_id)

        await self.gen_repo.add_event(
            EventLog(
                event_type=EventType.ADJUSTMENT_CREATED.value,
                performed_by=current_user_id,
                meta={
                    "adjustment_type": data.adjustment_type.value,
                    "entity_type": data.entity_type,
                    "entity_id": str(data.entity_id),
                    "delta": str(delta),
                    "reason": data.reason,
                },
            )
        )

        return AdjustmentResponse.model_validate(created)

    async def _apply_side_effects(
        self, data: AdjustmentCreate, delta: Decimal, current_user_id: uuid.UUID
    ) -> None:
        if data.adjustment_type == AdjustmentType.MOTOHOURS_ADJUST:
            generator = await self.gen_repo.get_by_id(data.entity_id)
            if not generator:
                raise NotFoundException(detail=f"Generator with id '{data.entity_id}' not found")
            hours_added = await self.moto_repo.get_total_hours_added(data.entity_id)
            settings = generator.settings
            initial = (
                Decimal(str(settings.initial_motohours))
                if settings and settings.initial_motohours
                else Decimal("0")
            )
            total_after = initial + Decimal(str(hours_added)) + delta
            entry = MotohoursLog(
                generator_id=data.entity_id,
                hours_added=delta,
                total_after=total_after,
            )
            await self.moto_repo.create_log_entry(entry)

        elif data.adjustment_type == AdjustmentType.FUEL_STOCK_ADJUST:
            stock = await self.repo.get_fuel_stock(data.entity_id)
            if not stock:
                raise NotFoundException(detail=f"FuelStock with id '{data.entity_id}' not found")
            stock.current_liters = data.value_after
            await self.repo.update_fuel_stock(stock)

        elif data.adjustment_type == AdjustmentType.OIL_STOCK_ADJUST:
            stock = await self.repo.get_oil_stock(data.entity_id)
            if not stock:
                raise NotFoundException(detail=f"OilStock with id '{data.entity_id}' not found")
            stock.current_quantity = data.value_after
            await self.repo.update_oil_stock(stock)
