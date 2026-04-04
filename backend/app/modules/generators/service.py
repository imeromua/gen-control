import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import EventType, FuelType
from app.common.exceptions import NotFoundException
from app.modules.generators.models import (
    EventLog,
    Generator,
    GeneratorSettings,
)
from app.modules.generators.repository import GeneratorRepository
from app.modules.generators.schemas import (
    GeneratorCreate,
    GeneratorSettingsUpdate,
    GeneratorStatusResponse,
    GeneratorUpdate,
)
from app.modules.motohours.repository import MotohoursRepository


class GeneratorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = GeneratorRepository(db)
        self.moto_repo = MotohoursRepository(db)

    async def get_all(self) -> list[Generator]:
        return await self.repo.get_all()

    async def get_by_id(self, generator_id: uuid.UUID) -> Generator:
        generator = await self.repo.get_by_id(generator_id)
        if not generator:
            raise NotFoundException(
                detail=f"Generator with id '{generator_id}' not found"
            )
        return generator

    async def create(
        self, data: GeneratorCreate, current_user_id: uuid.UUID
    ) -> Generator:
        try:
            generator = Generator(
                name=data.name,
                type=data.type.value,
                model=data.model,
                serial_number=data.serial_number,
            )
            settings = GeneratorSettings(
                generator_id=generator.id,
                fuel_type=FuelType.A95.value,
                initial_motohours=Decimal("0"),
            )
            generator.settings = settings

            created = await self.repo.create(generator)

            await self.repo.add_event(
                EventLog(
                    event_type=EventType.GENERATOR_CREATED.value,
                    generator_id=created.id,
                    performed_by=current_user_id,
                    meta={"name": data.name, "type": data.type.value},
                )
            )

            await self.db.commit()
            await self.db.refresh(created)
            return created
        except Exception as e:
            await self.db.rollback()
            raise e

    async def update(
        self, generator_id: uuid.UUID, data: GeneratorUpdate, current_user_id: uuid.UUID
    ) -> Generator:
        try:
            generator = await self.get_by_id(generator_id)

            if data.name is not None:
                generator.name = data.name
            if data.type is not None:
                generator.type = data.type.value
            if data.model is not None:
                generator.model = data.model
            if data.serial_number is not None:
                generator.serial_number = data.serial_number
            if data.is_active is not None:
                generator.is_active = data.is_active

            updated = await self.repo.update(generator)

            await self.repo.add_event(
                EventLog(
                    event_type=EventType.GENERATOR_UPDATED.value,
                    generator_id=generator_id,
                    performed_by=current_user_id,
                )
            )

            await self.db.commit()
            await self.db.refresh(updated)
            return updated
        except Exception as e:
            await self.db.rollback()
            raise e

    async def deactivate(
        self, generator_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> Generator:
        try:
            generator = await self.get_by_id(generator_id)
            generator.is_active = False

            updated = await self.repo.update(generator)

            await self.repo.add_event(
                EventLog(
                    event_type=EventType.GENERATOR_DEACTIVATED.value,
                    generator_id=generator_id,
                    performed_by=current_user_id,
                )
            )

            await self.db.commit()
            await self.db.refresh(updated)
            return updated
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_settings(self, generator_id: uuid.UUID) -> GeneratorSettings:
        await self.get_by_id(generator_id)
        settings = await self.repo.get_settings(generator_id)
        if not settings:
            raise NotFoundException(
                detail=f"Settings for generator '{generator_id}' not found"
            )
        return settings

    async def update_settings(
        self, generator_id: uuid.UUID, data: GeneratorSettingsUpdate, current_user_id: uuid.UUID
    ) -> GeneratorSettings:
        try:
            await self.get_by_id(generator_id)
            settings = await self.repo.get_settings(generator_id)
            if not settings:
                raise NotFoundException(detail=f"Settings for generator '{generator_id}' not found")

            old_data = {
                "fuel_type": settings.fuel_type,
                "tank_capacity_liters": (
                    str(settings.tank_capacity_liters)
                    if settings.tank_capacity_liters
                    else None
                ),
                "initial_motohours": str(settings.initial_motohours),
            }

            settings.fuel_type = data.fuel_type.value
            settings.tank_capacity_liters = data.tank_capacity_liters
            settings.fuel_consumption_per_hour = data.fuel_consumption_per_hour
            settings.fuel_warning_level = data.fuel_warning_level
            settings.fuel_critical_level = data.fuel_critical_level
            settings.to_interval_hours = data.to_interval_hours
            settings.to_warning_before_hours = data.to_warning_before_hours
            settings.max_continuous_work_hours = data.max_continuous_work_hours
            settings.max_daily_hours = data.max_daily_hours
            settings.min_pause_between_starts_min = data.min_pause_between_starts_min
            settings.expected_consumption_deviation_pct = data.expected_consumption_deviation_pct
            settings.initial_motohours = data.initial_motohours
            settings.updated_by = current_user_id

            updated = await self.repo.update_settings(settings)

            new_data = {
                "fuel_type": updated.fuel_type,
                "tank_capacity_liters": str(updated.tank_capacity_liters) if updated.tank_capacity_liters else None,
                "initial_motohours": str(updated.initial_motohours),
            }

            await self.repo.add_event(
                EventLog(
                    event_type=EventType.GENERATOR_SETTINGS_UPDATED.value,
                    generator_id=generator_id,
                    performed_by=current_user_id,
                    meta={"old": old_data, "new": new_data},
                )
            )

            await self.db.commit()
            await self.db.refresh(updated)
            return updated
        except Exception as e:
            await self.db.rollback()
            raise e

    async def get_status(self, generator_id: uuid.UUID) -> GeneratorStatusResponse:
        generator = await self.get_by_id(generator_id)
        settings = generator.settings

        hours_added = await self.moto_repo.get_total_hours_added(generator_id)
        initial = (
            Decimal(str(settings.initial_motohours))
            if settings and settings.initial_motohours is not None
            else Decimal("0")
        )
        motohours_total = (
            initial + Decimal(str(hours_added))
            if hours_added is not None
            else initial
        )

        hours_since_to = await self.moto_repo.get_motohours_since_last_maintenance(generator_id)
        last_maintenance = await self.moto_repo.get_last_maintenance(generator_id)
        if last_maintenance is None:
            motohours_since_last_to = motohours_total
        else:
            motohours_since_last_to = Decimal(str(hours_since_to))

        to_interval = Decimal(str(settings.to_interval_hours)) if settings and settings.to_interval_hours else None
        to_warning_before = (
            Decimal(str(settings.to_warning_before_hours)) if settings and settings.to_warning_before_hours else None
        )

        next_to_at_hours = None
        hours_to_next_to = None
        to_warning_active = False

        if to_interval is not None:
            if last_maintenance is not None and last_maintenance.next_service_at_hours is not None:
                next_to_at_hours = Decimal(str(last_maintenance.next_service_at_hours))
            elif last_maintenance is not None:
                next_to_at_hours = motohours_since_last_to + to_interval
            else:
                next_to_at_hours = motohours_total + to_interval
            hours_to_next_to = next_to_at_hours - motohours_total
            if to_warning_before is not None:
                to_warning_active = hours_to_next_to <= to_warning_before

        fuel_type = settings.fuel_type if settings else None
        tank_capacity = (
            Decimal(str(settings.tank_capacity_liters))
            if settings and settings.tank_capacity_liters is not None
            else None
        )
        fuel_warning_level = (
            Decimal(str(settings.fuel_warning_level))
            if settings and settings.fuel_warning_level is not None
            else None
        )
        fuel_critical_level = (
            Decimal(str(settings.fuel_critical_level))
            if settings and settings.fuel_critical_level is not None
            else None
        )

        _ = fuel_warning_level
        _ = fuel_critical_level

        return GeneratorStatusResponse(
            generator_id=generator.id,
            name=generator.name,
            type=generator.type,
            is_active=generator.is_active,
            fuel_type=fuel_type,
            tank_capacity_liters=tank_capacity,
            current_fuel_liters=None,
            motohours_total=motohours_total,
            motohours_since_last_to=motohours_since_last_to,
            next_to_at_hours=next_to_at_hours,
            hours_to_next_to=hours_to_next_to,
            to_warning_active=to_warning_active,
            fuel_warning_active=False,
            fuel_critical_active=False,
        )