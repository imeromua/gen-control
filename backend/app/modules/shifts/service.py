import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import EventType, RoleName, ShiftStatus
from app.common.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.modules.generators.models import EventLog
from app.modules.generators.repository import GeneratorRepository
from app.modules.motohours.models import MotohoursLog
from app.modules.motohours.repository import MotohoursRepository
from app.modules.rules.service import RulesService
from app.modules.shifts.models import Shift, SystemSettings
from app.modules.shifts.repository import ShiftRepository, SystemSettingsRepository
from app.modules.shifts.schemas import ShiftStartRequest, WorkTimeUpdate
from app.modules.users.models import User


class ShiftService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ShiftRepository(db)
        self.settings_repo = SystemSettingsRepository(db)
        self.gen_repo = GeneratorRepository(db)
        self.moto_repo = MotohoursRepository(db)
        self.rules = RulesService(db)

    async def get_all(
        self,
        generator_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> list[Shift]:
        return await self.repo.get_all(generator_id=generator_id, status=status)

    async def get_by_id(self, shift_id: uuid.UUID) -> Shift:
        shift = await self.repo.get_by_id(shift_id)
        if not shift:
            raise NotFoundException(detail=f"Shift with id '{shift_id}' not found")
        return shift

    async def get_active(self) -> Shift | None:
        return await self.repo.get_any_active()

    async def start(self, data: ShiftStartRequest, current_user: User) -> Shift:
        await self.rules.check_working_hours()
        await self.rules.check_only_one_generator_active()
        await self.rules.check_no_active_shift(data.generator_id)
        await self.rules.check_min_pause_between_starts(data.generator_id)

        generator = await self.gen_repo.get_by_id(data.generator_id)
        if not generator:
            raise NotFoundException(detail=f"Generator with id '{data.generator_id}' not found")
        if not generator.is_active:
            raise ConflictException(detail=f"Generator '{generator.name}' is not active")

        shift_number = await self.repo.get_next_shift_number()
        now = datetime.now(tz=timezone.utc)

        shift = Shift(
            shift_number=shift_number,
            generator_id=data.generator_id,
            started_by=current_user.id,
            started_at=now,
            status=ShiftStatus.ACTIVE.value,
        )
        created = await self.repo.create(shift)

        await self.gen_repo.add_event(
            EventLog(
                event_type=EventType.SHIFT_STARTED.value,
                generator_id=data.generator_id,
                performed_by=current_user.id,
                meta={
                    "shift_number": shift_number,
                    "generator_id": str(data.generator_id),
                    "generator_name": generator.name,
                },
            )
        )

        return created

    async def stop(self, shift_id: uuid.UUID, current_user: User) -> Shift:
        await self.rules.check_working_hours()

        shift = await self.get_by_id(shift_id)
        if shift.status != ShiftStatus.ACTIVE.value:
            raise ConflictException(detail="Shift is not active")

        if shift.started_by != current_user.id and current_user.role.name != RoleName.ADMIN:
            raise ForbiddenException(detail="Only ADMIN can stop another user's shift")

        now = datetime.now(tz=timezone.utc)
        duration_minutes = Decimal(str((now - shift.started_at).total_seconds() / 60))

        gen_settings = await self.gen_repo.get_settings(shift.generator_id)
        fuel_consumed: Decimal | None = None
        if gen_settings and gen_settings.fuel_consumption_per_hour:
            duration_hours = duration_minutes / Decimal("60")
            fuel_consumed = (
                duration_hours * Decimal(gen_settings.fuel_consumption_per_hour)
            ).quantize(Decimal("0.001"))

        motohours_accumulated = (duration_minutes / Decimal("60")).quantize(Decimal("0.001"))

        shift.stopped_by = current_user.id
        shift.stopped_at = now
        shift.duration_minutes = duration_minutes.quantize(Decimal("0.01"))
        shift.fuel_consumed_liters = fuel_consumed
        shift.motohours_accumulated = motohours_accumulated
        shift.status = ShiftStatus.CLOSED.value

        updated = await self.repo.update(shift)

        generator = await self.gen_repo.get_by_id(shift.generator_id)
        initial = (
            Decimal(str(generator.settings.initial_motohours))
            if generator and generator.settings and generator.settings.initial_motohours
            else Decimal("0")
        )
        hours_added = await self.moto_repo.get_total_hours_added(shift.generator_id)
        total_after = initial + Decimal(str(hours_added)) + motohours_accumulated

        moto_log = MotohoursLog(
            generator_id=shift.generator_id,
            shift_id=shift.id,
            hours_added=motohours_accumulated,
            total_after=total_after,
        )
        self.db.add(moto_log)
        await self.db.commit()

        await self.gen_repo.add_event(
            EventLog(
                event_type=EventType.SHIFT_STOPPED.value,
                generator_id=shift.generator_id,
                performed_by=current_user.id,
                meta={
                    "shift_number": shift.shift_number,
                    "duration_minutes": float(duration_minutes),
                    "fuel_consumed_liters": float(fuel_consumed) if fuel_consumed is not None else None,
                    "motohours_accumulated": float(motohours_accumulated),
                },
            )
        )

        return updated

    async def get_work_time_settings(self) -> SystemSettings | None:
        return await self.settings_repo.get()

    async def update_work_time_settings(
        self, data: WorkTimeUpdate, current_user: User
    ) -> SystemSettings:
        settings = await self.settings_repo.get()
        if settings is None:
            settings = SystemSettings(
                work_time_start=data.work_time_start,
                work_time_end=data.work_time_end,
                updated_by=current_user.id,
            )
            self.db.add(settings)
            await self.db.commit()
            await self.db.refresh(settings)
        else:
            settings.work_time_start = data.work_time_start
            settings.work_time_end = data.work_time_end
            settings.updated_by = current_user.id
            await self.settings_repo.update(settings)

        await self.gen_repo.add_event(
            EventLog(
                event_type=EventType.SYSTEM_SETTINGS_UPDATED.value,
                generator_id=None,
                performed_by=current_user.id,
                meta={
                    "work_time_start": data.work_time_start.strftime("%H:%M"),
                    "work_time_end": data.work_time_end.strftime("%H:%M"),
                },
            )
        )

        return settings
