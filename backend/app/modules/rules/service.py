import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, ForbiddenException
from app.modules.generators.repository import GeneratorRepository
from app.modules.shifts.repository import ShiftRepository, SystemSettingsRepository

KYIV_TZ = ZoneInfo("Europe/Kyiv")


class RulesService:
    def __init__(self, db: AsyncSession):
        self.settings_repo = SystemSettingsRepository(db)
        self.shift_repo = ShiftRepository(db)
        self.gen_repo = GeneratorRepository(db)

    async def check_working_hours(self) -> None:
        settings = await self.settings_repo.get()
        if settings is None:
            return

        now_kyiv = datetime.now(tz=timezone.utc).astimezone(KYIV_TZ).time()
        start = settings.work_time_start
        end = settings.work_time_end

        if not (start <= now_kyiv <= end):
            raise ForbiddenException(
                detail=f"Дії заборонені поза робочим часом ({start.strftime('%H:%M')}–{end.strftime('%H:%M')})"
            )

    async def check_no_active_shift(self, generator_id: uuid.UUID) -> None:
        active_shift = await self.shift_repo.get_active_for_generator(generator_id)
        if active_shift:
            raise ConflictException(
                detail=f"Вже є активна зміна #{active_shift.shift_number}. Спочатку зупиніть поточну."
            )

    async def check_only_one_generator_active(self) -> None:
        active_shift = await self.shift_repo.get_any_active()
        if active_shift:
            raise ConflictException(
                detail="Інший генератор вже працює. Одночасно може працювати лише один генератор."
            )

    async def check_min_pause_between_starts(self, generator_id: uuid.UUID) -> None:
        gen_settings = await self.gen_repo.get_settings(generator_id)
        if gen_settings is None or gen_settings.min_pause_between_starts_min is None:
            return

        last_shift = await self.shift_repo.get_last_closed_for_generator(generator_id)
        if last_shift is None or last_shift.stopped_at is None:
            return

        min_pause = gen_settings.min_pause_between_starts_min
        now = datetime.now(tz=timezone.utc)
        elapsed_minutes = (now - last_shift.stopped_at).total_seconds() / 60

        if elapsed_minutes < min_pause:
            remaining = int(min_pause - elapsed_minutes) + 1
            raise ConflictException(
                detail=f"Генератор ще на паузі. Залишилось {remaining} хв."
            )
