import uuid
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import EventType
from app.modules.generators.models import EventLog
from app.modules.generators.repository import GeneratorRepository
from app.modules.generators.service import GeneratorService
from app.modules.motohours.models import MaintenanceLog
from app.modules.motohours.repository import MotohoursRepository
from app.modules.motohours.schemas import MaintenanceLogCreate


class MotohoursService:
    def __init__(self, db: AsyncSession):
        self.repo = MotohoursRepository(db)
        self.gen_repo = GeneratorRepository(db)
        self.gen_service = GeneratorService(db)

    async def _calculate_total_motohours(self, generator_id: uuid.UUID) -> Decimal:
        """Calculate total motohours = initial_motohours + sum of logged hours."""
        settings = await self.gen_repo.get_settings(generator_id)
        initial = Decimal(str(settings.initial_motohours)) if settings and settings.initial_motohours else Decimal("0")
        hours_sum = await self.repo.get_hours_sum(generator_id)
        return initial + Decimal(str(hours_sum))

    async def get_motohours_log(self, generator_id: uuid.UUID) -> list:
        await self.gen_service.get_by_id(generator_id)
        return await self.repo.get_log_by_generator(generator_id)

    async def get_motohours_total(self, generator_id: uuid.UUID) -> dict:
        await self.gen_service.get_by_id(generator_id)
        total = await self._calculate_total_motohours(generator_id)
        return {"generator_id": generator_id, "total_hours": total}

    async def get_maintenance_log(self, generator_id: uuid.UUID) -> list:
        await self.gen_service.get_by_id(generator_id)
        return await self.repo.get_maintenance_log(generator_id)

    async def create_maintenance(
        self, generator_id: uuid.UUID, data: MaintenanceLogCreate, user_id: uuid.UUID
    ) -> MaintenanceLog:
        await self.gen_service.get_by_id(generator_id)
        settings = await self.gen_repo.get_settings(generator_id)

        motohours_total = await self._calculate_total_motohours(generator_id)
        to_interval = Decimal(str(settings.to_interval_hours)) if settings and settings.to_interval_hours else Decimal("0")
        next_service_at_hours = motohours_total + to_interval

        maintenance = MaintenanceLog(
            generator_id=generator_id,
            performed_by=user_id,
            motohours_at_service=motohours_total,
            next_service_at_hours=next_service_at_hours,
            notes=data.notes,
        )
        created = await self.repo.create_maintenance(maintenance)

        # Write event log
        await self.gen_repo.create_event_log(
            EventLog(
                event_type=EventType.MAINTENANCE_PERFORMED.value,
                generator_id=generator_id,
                user_id=user_id,
                meta={
                    "motohours_at_service": str(motohours_total),
                    "next_service_at_hours": str(next_service_at_hours),
                    "notes": data.notes,
                },
            )
        )

        return created
