import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import EventType
from app.common.exceptions import NotFoundException
from app.modules.generators.models import Generator, GeneratorSettings, EventLog
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
        self.repo = GeneratorRepository(db)
        self.motohours_repo = MotohoursRepository(db)

    async def _calculate_total_motohours(self, generator_id: uuid.UUID, settings: GeneratorSettings | None) -> Decimal:
        """Calculate total motohours = initial_motohours + sum of logged hours."""
        initial = Decimal(str(settings.initial_motohours)) if settings and settings.initial_motohours else Decimal("0")
        hours_sum = await self.motohours_repo.get_hours_sum(generator_id)
        return initial + Decimal(str(hours_sum))

    async def get_all(self) -> list[Generator]:
        return await self.repo.get_all()

    async def get_by_id(self, generator_id: uuid.UUID) -> Generator:
        generator = await self.repo.get_by_id(generator_id)
        if not generator:
            raise NotFoundException(detail=f"Generator with id '{generator_id}' not found")
        return generator

    async def create(self, data: GeneratorCreate, user_id: uuid.UUID) -> Generator:
        generator = Generator(
            name=data.name,
            type=data.type.value,
            model=data.model,
            serial_number=data.serial_number,
        )
        created = await self.repo.create(generator)

        # Auto-create default settings
        settings = GeneratorSettings(generator_id=created.id)
        await self.repo.create_settings(settings)

        # Write event log
        await self.repo.create_event_log(
            EventLog(
                event_type=EventType.GENERATOR_CREATED.value,
                generator_id=created.id,
                user_id=user_id,
                meta={"name": data.name, "type": data.type.value},
            )
        )

        return await self.repo.get_by_id(created.id)

    async def update(self, generator_id: uuid.UUID, data: GeneratorUpdate) -> Generator:
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

        return await self.repo.update(generator)

    async def deactivate(self, generator_id: uuid.UUID, user_id: uuid.UUID) -> Generator:
        generator = await self.get_by_id(generator_id)
        generator.is_active = False
        updated = await self.repo.update(generator)

        await self.repo.create_event_log(
            EventLog(
                event_type=EventType.GENERATOR_DEACTIVATED.value,
                generator_id=generator_id,
                user_id=user_id,
                meta={"name": generator.name},
            )
        )

        return updated

    async def get_settings(self, generator_id: uuid.UUID) -> GeneratorSettings:
        await self.get_by_id(generator_id)
        settings = await self.repo.get_settings(generator_id)
        if not settings:
            raise NotFoundException(detail=f"Settings for generator '{generator_id}' not found")
        return settings

    async def update_settings(
        self, generator_id: uuid.UUID, data: GeneratorSettingsUpdate, user_id: uuid.UUID
    ) -> GeneratorSettings:
        await self.get_by_id(generator_id)
        settings = await self.repo.get_settings(generator_id)
        if not settings:
            raise NotFoundException(detail=f"Settings for generator '{generator_id}' not found")

        old_data = {
            "fuel_type": settings.fuel_type,
            "tank_capacity_liters": str(settings.tank_capacity_liters) if settings.tank_capacity_liters else None,
            "to_interval_hours": str(settings.to_interval_hours) if settings.to_interval_hours else None,
            "initial_motohours": str(settings.initial_motohours) if settings.initial_motohours else None,
        }

        if data.fuel_type is not None:
            settings.fuel_type = data.fuel_type.value
        if data.tank_capacity_liters is not None:
            settings.tank_capacity_liters = data.tank_capacity_liters
        if data.fuel_consumption_per_hour is not None:
            settings.fuel_consumption_per_hour = data.fuel_consumption_per_hour
        if data.fuel_warning_level is not None:
            settings.fuel_warning_level = data.fuel_warning_level
        if data.fuel_critical_level is not None:
            settings.fuel_critical_level = data.fuel_critical_level
        if data.to_interval_hours is not None:
            settings.to_interval_hours = data.to_interval_hours
        if data.to_warning_before_hours is not None:
            settings.to_warning_before_hours = data.to_warning_before_hours
        if data.max_continuous_work_hours is not None:
            settings.max_continuous_work_hours = data.max_continuous_work_hours
        if data.max_daily_hours is not None:
            settings.max_daily_hours = data.max_daily_hours
        if data.min_pause_between_starts_min is not None:
            settings.min_pause_between_starts_min = data.min_pause_between_starts_min
        if data.expected_consumption_deviation_pct is not None:
            settings.expected_consumption_deviation_pct = data.expected_consumption_deviation_pct
        if data.initial_motohours is not None:
            settings.initial_motohours = data.initial_motohours

        settings.updated_by = user_id

        new_data = {
            "fuel_type": settings.fuel_type,
            "tank_capacity_liters": str(settings.tank_capacity_liters) if settings.tank_capacity_liters else None,
            "to_interval_hours": str(settings.to_interval_hours) if settings.to_interval_hours else None,
            "initial_motohours": str(settings.initial_motohours) if settings.initial_motohours else None,
        }

        updated = await self.repo.update_settings(settings)

        await self.repo.create_event_log(
            EventLog(
                event_type=EventType.GENERATOR_SETTINGS_UPDATED.value,
                generator_id=generator_id,
                user_id=user_id,
                meta={"old": old_data, "new": new_data},
            )
        )

        return updated

    async def get_status(self, generator_id: uuid.UUID) -> GeneratorStatusResponse:
        generator = await self.get_by_id(generator_id)
        settings = await self.repo.get_settings(generator_id)

        initial_motohours = Decimal(str(settings.initial_motohours)) if settings and settings.initial_motohours else Decimal("0")
        motohours_total = await self._calculate_total_motohours(generator_id, settings)

        hours_since_last_to = await self.motohours_repo.get_hours_since_last_maintenance(generator_id)
        motohours_since_last_to = Decimal(str(hours_since_last_to))

        to_interval = Decimal(str(settings.to_interval_hours)) if settings and settings.to_interval_hours else None
        to_warning_before = Decimal(str(settings.to_warning_before_hours)) if settings and settings.to_warning_before_hours else None

        next_to_at_hours: Decimal | None = None
        hours_to_next_to: Decimal | None = None
        to_warning_active = False

        if to_interval is not None:
            last_maintenance = await self.motohours_repo.get_last_maintenance(generator_id)
            base = Decimal(str(last_maintenance.motohours_at_service)) if last_maintenance else initial_motohours
            next_to_at_hours = base + to_interval
            hours_to_next_to = next_to_at_hours - motohours_total
            if to_warning_before is not None:
                to_warning_active = hours_to_next_to <= to_warning_before

        fuel_warning_active = False
        fuel_critical_active = False

        return GeneratorStatusResponse(
            generator_id=generator.id,
            name=generator.name,
            type=generator.type,
            is_active=generator.is_active,
            fuel_type=settings.fuel_type if settings else None,
            tank_capacity_liters=Decimal(str(settings.tank_capacity_liters)) if settings and settings.tank_capacity_liters else None,
            current_fuel_liters=None,
            motohours_total=motohours_total,
            motohours_since_last_to=motohours_since_last_to,
            next_to_at_hours=next_to_at_hours,
            hours_to_next_to=hours_to_next_to,
            to_warning_active=to_warning_active,
            fuel_warning_active=fuel_warning_active,
            fuel_critical_active=fuel_critical_active,
        )
