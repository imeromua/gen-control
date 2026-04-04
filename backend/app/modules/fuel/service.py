from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import EventType
from app.common.exceptions import ConflictException, NotFoundException
from app.modules.fuel.models import FuelDelivery, FuelRefill, FuelStock
from app.modules.fuel.repository import FuelRepository
from app.modules.fuel.schemas import (
    FuelDeliveryCreate,
    FuelRefillCreate,
    FuelStockUpdate,
)
from app.modules.generators.models import EventLog
from app.modules.generators.repository import GeneratorRepository
from app.modules.rules.service import RulesService
from app.modules.shifts.repository import ShiftRepository
from app.modules.users.models import User


class FuelService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FuelRepository(db)
        self.gen_repo = GeneratorRepository(db)
        self.shift_repo = ShiftRepository(db)
        self.rules = RulesService(db)

    async def get_stock(self) -> FuelStock:
        stock = await self.repo.get_stock()
        if stock is None:
            raise NotFoundException(detail="Fuel stock not found")
        return stock

    async def update_stock_settings(
        self, data: FuelStockUpdate, current_user: User
    ) -> FuelStock:
        stock = await self.get_stock()
        if data.max_limit_liters is not None:
            stock.max_limit_liters = data.max_limit_liters
        if data.warning_level_liters is not None:
            stock.warning_level_liters = data.warning_level_liters
        updated = await self.repo.update_stock(stock)

        await self.gen_repo.add_event(
            EventLog(
                event_type=EventType.FUEL_STOCK_UPDATED.value,
                generator_id=None,
                performed_by=current_user.id,
                meta={
                    "max_limit_liters": float(updated.max_limit_liters),
                    "warning_level_liters": float(updated.warning_level_liters),
                },
            )
        )

        await self.db.flush()
        return updated

    async def get_deliveries(self) -> list[FuelDelivery]:
        return await self.repo.get_deliveries()

    async def create_delivery(
        self, data: FuelDeliveryCreate, current_user: User
    ) -> FuelDelivery:
        await self.rules.check_working_hours()

        stock = await self.repo.get_stock()
        if stock is None:
            raise NotFoundException(detail="Fuel stock not found")

        new_total = Decimal(str(stock.current_liters)) + Decimal(str(data.liters))
        if new_total > Decimal(str(stock.max_limit_liters)):
            raise ConflictException(detail="Перевищення ліміту складу")

        stock_before = Decimal(str(stock.current_liters))
        stock_after = new_total

        delivery = FuelDelivery(
            fuel_type=stock.fuel_type,
            liters=data.liters,
            check_number=data.check_number,
            delivered_by_name=data.delivered_by_name,
            accepted_by=current_user.id,
            stock_before=stock_before,
            stock_after=stock_after,
        )

        self.db.add(delivery)
        stock.current_liters = stock_after

        self.db.add(
            EventLog(
                event_type=EventType.FUEL_DELIVERED.value,
                generator_id=None,
                performed_by=current_user.id,
                meta={
                    "liters": float(data.liters),
                    "check_number": data.check_number,
                    "stock_before": float(stock_before),
                    "stock_after": float(stock_after),
                },
            )
        )

        await self.db.flush()
        await self.db.refresh(delivery)
        return delivery

    async def get_refills(self) -> list[FuelRefill]:
        return await self.repo.get_refills()

    async def create_refill(
        self, data: FuelRefillCreate, current_user: User
    ) -> FuelRefill:
        await self.rules.check_working_hours()

        active_shift = await self.shift_repo.get_active_for_generator(data.generator_id)
        if active_shift is not None:
            raise ConflictException(detail="Заправка під час роботи заборонена")

        stock = await self.repo.get_stock()
        if stock is None:
            raise NotFoundException(detail="Fuel stock not found")

        if Decimal(str(stock.current_liters)) < Decimal(str(data.liters)):
            raise ConflictException(detail="Недостатньо палива на складі")

        tank_level_after = Decimal(str(data.tank_level_before)) + Decimal(str(data.liters))

        gen_settings = await self.gen_repo.get_settings(data.generator_id)
        if gen_settings and gen_settings.tank_capacity_liters is not None:
            if tank_level_after > Decimal(str(gen_settings.tank_capacity_liters)):
                raise ConflictException(detail="Перевищення місткості бака генератора")

        stock_before = Decimal(str(stock.current_liters))
        stock_after = stock_before - Decimal(str(data.liters))

        refill = FuelRefill(
            generator_id=data.generator_id,
            performed_by=current_user.id,
            liters=data.liters,
            tank_level_before=data.tank_level_before,
            tank_level_after=tank_level_after,
            stock_before=stock_before,
            stock_after=stock_after,
        )

        self.db.add(refill)
        stock.current_liters = stock_after

        self.db.add(
            EventLog(
                event_type=EventType.FUEL_REFILLED.value,
                generator_id=data.generator_id,
                performed_by=current_user.id,
                meta={
                    "liters": float(data.liters),
                    "tank_before": float(data.tank_level_before),
                    "tank_after": float(tank_level_after),
                    "stock_before": float(stock_before),
                    "stock_after": float(stock_after),
                },
            )
        )

        await self.db.flush()
        await self.db.refresh(refill)
        return refill
