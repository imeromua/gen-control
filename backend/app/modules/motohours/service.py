import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import EventType
from app.common.exceptions import NotFoundException
from app.modules.generators.models import EventLog
from app.modules.generators.repository import GeneratorRepository
from app.modules.motohours.models import MaintenanceLog
from app.modules.motohours.repository import MotohoursRepository
from app.modules.motohours.schemas import (
    MaintenanceCreate,
    MaintenanceLogResponse,
    MotohoursLogResponse,
    MotohoursTotalResponse,
)


class MotohoursService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MotohoursRepository(db)
        self.gen_repo = GeneratorRepository(db)

    async def _ensure_generator_exists(self, generator_id: uuid.UUID) -> None:
        generator = await self.gen_repo.get_by_id(generator_id)
        if not generator:
            raise NotFoundException(
                detail=f"Generator with id '{generator_id}' not found"
            )

    async def get_log(
        self, generator_id: uuid.UUID
    ) -> list[MotohoursLogResponse]:
        await self._ensure_generator_exists(generator_id)
        entries = await self.repo.get_log(generator_id)
        return [MotohoursLogResponse.model_validate(e) for e in entries]

    async def get_total(self, generator_id: uuid.UUID) -> MotohoursTotalResponse:
        generator = await self.gen_repo.get_by_id(generator_id)
        if not generator:
            raise NotFoundException(
                detail=f"Generator with id '{generator_id}' not found"
            )

        hours_added = await self.repo.get_total_hours_added(generator_id)
        settings = generator.settings
        initial = (
            Decimal(str(settings.initial_motohours))
            if settings and settings.initial_motohours
            else Decimal("0")
        )
        total = initial + Decimal(str(hours_added))

        return MotohoursTotalResponse(
            generator_id=generator_id, motohours_total=total
        )

    async def get_maintenance_log(
        self, generator_id: uuid.UUID
    ) -> list[MaintenanceLogResponse]:
        await self._ensure_generator_exists(generator_id)
        entries = await self.repo.get_maintenance_log(generator_id)
        return [MaintenanceLogResponse.model_validate(e) for e in entries]

    async def create_maintenance(
        self,
        generator_id: uuid.UUID,
        data: MaintenanceCreate,
        current_user_id: uuid.UUID,
    ) -> MaintenanceLogResponse:
        generator = await self.gen_repo.get_by_id(generator_id)
        if not generator:
            raise NotFoundException(
                detail=f"Generator with id '{generator_id}' not found"
            )

        hours_added = await self.repo.get_total_hours_added(generator_id)
        settings = generator.settings
        initial = (
            Decimal(str(settings.initial_motohours))
            if settings and settings.initial_motohours
            else Decimal("0")
        )
        motohours_total = initial + Decimal(str(hours_added))

        to_interval = (
            Decimal(str(settings.to_interval_hours))
            if settings and settings.to_interval_hours
            else None
        )
        next_service_at_hours = (
            motohours_total + to_interval if to_interval is not None else None
        )

        entry = MaintenanceLog(
            generator_id=generator_id,
            performed_by=current_user_id,
            motohours_at_service=motohours_total,
            next_service_at_hours=next_service_at_hours,
            notes=data.notes,
        )
        
        async with self.db.begin():
            created = await self.repo.create_maintenance(entry)

            event = EventLog(
                event_type=EventType.MAINTENANCE_PERFORMED.value,
                generator_id=generator_id,
                performed_by=current_user_id,
                meta={
                    "motohours_at_service": str(motohours_total),
                    "next_service_at_hours": (
                        str(next_service_at_hours)
                        if next_service_at_hours
                        else None
                    ),
                },
            )
            await self.gen_repo.add_event(event)

        return MaintenanceLogResponse.model_validate(created)
