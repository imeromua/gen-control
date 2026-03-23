from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.schemas import (
    ActiveShiftSchema,
    DashboardResponse,
    DashboardSummaryResponse,
    FuelStockSchema,
    GeneratorDashboardSchema,
    NextOutageSchema,
    OilStockSchema,
    RecentEventSchema,
    TodayStatsSchema,
)
from app.modules.fuel.repository import FuelRepository
from app.modules.generators.repository import GeneratorRepository
from app.modules.motohours.repository import MotohoursRepository
from app.modules.oil.repository import OilRepository
from app.modules.outage.repository import OutageRepository
from app.modules.shifts.repository import ShiftRepository
from app.modules.users.repository import UserRepository

_KYIV_TZ = ZoneInfo("Europe/Kyiv")


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.shift_repo = ShiftRepository(db)
        self.gen_repo = GeneratorRepository(db)
        self.moto_repo = MotohoursRepository(db)
        self.fuel_repo = FuelRepository(db)
        self.oil_repo = OilRepository(db)
        self.outage_repo = OutageRepository(db)
        self.user_repo = UserRepository(db)
        self.dash_repo = DashboardRepository(db)

    async def get_dashboard(self) -> DashboardResponse:
        now = datetime.now(tz=timezone.utc)

        active_shift = await self._build_active_shift(now)
        generators = await self._build_generators()
        fuel_stock = await self._build_fuel_stock()
        oil_stocks = await self._build_oil_stocks()
        next_outage = await self._build_next_outage(now)
        today_stats = await self._build_today_stats(now)
        recent_events = await self._build_recent_events()

        return DashboardResponse(
            generated_at=now,
            active_shift=active_shift,
            generators=generators,
            fuel_stock=fuel_stock,
            oil_stocks=oil_stocks,
            next_outage=next_outage,
            today_stats=today_stats,
            recent_events=recent_events,
        )

    async def get_summary(self) -> DashboardSummaryResponse:
        now = datetime.now(tz=timezone.utc)

        shift = await self.shift_repo.get_any_active()
        active_shift_number: int | None = None
        active_shift_duration_minutes: float | None = None
        if shift is not None:
            active_shift_number = shift.shift_number
            active_shift_duration_minutes = round(
                (now - shift.started_at).total_seconds() / 60, 2
            )

        fuel_stock_liters: Decimal | None = None
        fuel_warning_active = False
        stock = await self.fuel_repo.get_stock()
        if stock is not None:
            fuel_stock_liters = Decimal(str(stock.current_liters))
            fuel_warning_active = fuel_stock_liters <= Decimal(str(stock.warning_level_liters))

        next_outage_date = None
        next_outage_hour_start = None
        next_outage_hour_end = None
        now_kyiv = now.astimezone(_KYIV_TZ)
        outage = await self.outage_repo.get_next(now_kyiv.date(), now_kyiv.hour)
        if outage is not None:
            next_outage_date = outage.outage_date
            next_outage_hour_start = outage.hour_start
            next_outage_hour_end = outage.hour_end

        return DashboardSummaryResponse(
            generated_at=now,
            generator_is_running=shift is not None,
            active_shift_number=active_shift_number,
            active_shift_duration_minutes=active_shift_duration_minutes,
            fuel_stock_liters=fuel_stock_liters,
            fuel_warning_active=fuel_warning_active,
            next_outage_date=next_outage_date,
            next_outage_hour_start=next_outage_hour_start,
            next_outage_hour_end=next_outage_hour_end,
        )

    # ── private helpers ──────────────────────────────────────────────────────

    async def _build_active_shift(self, now: datetime) -> ActiveShiftSchema | None:
        shift = await self.shift_repo.get_any_active()
        if shift is None:
            return None

        duration_minutes = round((now - shift.started_at).total_seconds() / 60, 2)

        generator = await self.gen_repo.get_by_id(shift.generator_id)
        generator_name = generator.name if generator else "Unknown"

        started_by_name: str | None = None
        if shift.started_by is not None:
            user = await self.user_repo.get_by_id(shift.started_by)
            if user is not None:
                started_by_name = user.full_name

        fuel_estimate: float | None = None
        if generator and generator.settings and generator.settings.fuel_consumption_per_hour:
            duration_hours = duration_minutes / 60
            fuel_estimate = round(
                duration_hours * float(generator.settings.fuel_consumption_per_hour), 3
            )

        return ActiveShiftSchema(
            id=shift.id,
            shift_number=shift.shift_number,
            generator_id=shift.generator_id,
            generator_name=generator_name,
            started_at=shift.started_at,
            started_by_name=started_by_name,
            duration_minutes=duration_minutes,
            fuel_consumed_estimate_liters=fuel_estimate,
        )

    async def _build_generators(self) -> list[GeneratorDashboardSchema]:
        generators = await self.gen_repo.get_all()
        active_generators = [g for g in generators if g.is_active]
        result = []
        for gen in active_generators:
            settings = gen.settings

            hours_added = await self.moto_repo.get_total_hours_added(gen.id)
            initial = (
                Decimal(str(settings.initial_motohours))
                if settings and settings.initial_motohours
                else Decimal("0")
            )
            motohours_total = initial + Decimal(str(hours_added))

            last_maintenance = await self.moto_repo.get_last_maintenance(gen.id)
            if last_maintenance is None:
                motohours_since_last_to = motohours_total
            else:
                hours_since = await self.moto_repo.get_motohours_since_last_maintenance(gen.id)
                motohours_since_last_to = Decimal(str(hours_since))

            to_interval = (
                Decimal(str(settings.to_interval_hours))
                if settings and settings.to_interval_hours
                else None
            )
            to_warning_before = (
                Decimal(str(settings.to_warning_before_hours))
                if settings and settings.to_warning_before_hours
                else None
            )

            hours_to_next_to: Decimal | None = None
            to_warning_active = False
            if to_interval is not None:
                if last_maintenance and last_maintenance.next_service_at_hours is not None:
                    next_to_at_hours = Decimal(str(last_maintenance.next_service_at_hours))
                elif last_maintenance is not None:
                    next_to_at_hours = motohours_since_last_to + to_interval
                else:
                    next_to_at_hours = motohours_total + to_interval
                hours_to_next_to = next_to_at_hours - motohours_total
                if to_warning_before is not None:
                    to_warning_active = hours_to_next_to <= to_warning_before

            result.append(
                GeneratorDashboardSchema(
                    id=gen.id,
                    name=gen.name,
                    type=gen.type,
                    is_active=gen.is_active,
                    motohours_total=motohours_total,
                    motohours_since_last_to=motohours_since_last_to,
                    hours_to_next_to=hours_to_next_to,
                    to_warning_active=to_warning_active,
                    fuel_type=settings.fuel_type if settings else None,
                    tank_capacity_liters=(
                        Decimal(str(settings.tank_capacity_liters))
                        if settings and settings.tank_capacity_liters
                        else None
                    ),
                )
            )
        return result

    async def _build_fuel_stock(self) -> FuelStockSchema | None:
        stock = await self.fuel_repo.get_stock()
        if stock is None:
            return None
        current = Decimal(str(stock.current_liters))
        warning_level = Decimal(str(stock.warning_level_liters))
        return FuelStockSchema(
            fuel_type=stock.fuel_type,
            current_liters=current,
            max_limit_liters=Decimal(str(stock.max_limit_liters)),
            warning_level_liters=warning_level,
            warning_active=current <= warning_level,
            critical_active=current <= (warning_level / 2),
        )

    async def _build_oil_stocks(self) -> list[OilStockSchema]:
        oils = await self.oil_repo.get_all()
        result = []
        gen_cache: dict[object, str] = {}
        for oil in oils:
            gen_id = oil.generator_id
            if gen_id not in gen_cache:
                gen = await self.gen_repo.get_by_id(gen_id)
                gen_cache[gen_id] = gen.name if gen else "Unknown"
            result.append(
                OilStockSchema(
                    id=oil.id,
                    generator_id=gen_id,
                    generator_name=gen_cache[gen_id],
                    oil_type=oil.oil_type,
                    current_quantity=Decimal(str(oil.current_quantity)),
                    unit=oil.unit,
                )
            )
        return result

    async def _build_next_outage(self, now: datetime) -> NextOutageSchema | None:
        now_kyiv = now.astimezone(_KYIV_TZ)
        outage = await self.outage_repo.get_next(now_kyiv.date(), now_kyiv.hour)
        if outage is None:
            return None
        return NextOutageSchema(
            outage_date=outage.outage_date,
            hour_start=outage.hour_start,
            hour_end=outage.hour_end,
            note=outage.note,
        )

    async def _build_today_stats(self, now: datetime) -> TodayStatsSchema:
        now_kyiv = now.astimezone(_KYIV_TZ)
        today_kyiv = now_kyiv.date()
        today_start = datetime(
            today_kyiv.year, today_kyiv.month, today_kyiv.day,
            tzinfo=_KYIV_TZ,
        )
        today_end = today_start + timedelta(days=1)

        today_shifts = await self.dash_repo.get_today_shifts(today_start, today_end)
        closed_today = [s for s in today_shifts if s.status == "CLOSED"]

        shifts_count = len(today_shifts)
        total_hours_worked = round(
            sum(float(s.duration_minutes or 0) / 60 for s in closed_today), 4
        )
        total_fuel_consumed = round(
            sum(float(s.fuel_consumed_liters or 0) for s in closed_today), 3
        )
        total_fuel_delivered = await self.dash_repo.get_today_fuel_delivered_sum(
            today_start, today_end
        )
        maintenance_performed = await self.dash_repo.has_maintenance_today(
            today_start, today_end
        )

        return TodayStatsSchema(
            shifts_count=shifts_count,
            total_hours_worked=total_hours_worked,
            total_fuel_consumed_liters=total_fuel_consumed,
            total_fuel_delivered_liters=float(total_fuel_delivered),
            maintenance_performed=maintenance_performed,
        )

    async def _build_recent_events(self) -> list[RecentEventSchema]:
        events = await self.dash_repo.get_recent_events(limit=10)
        result = []
        gen_cache: dict[object, str | None] = {}
        for event in events:
            gen_name: str | None = None
            if event.generator_id is not None:
                gen_id = event.generator_id
                if gen_id not in gen_cache:
                    gen = await self.gen_repo.get_by_id(gen_id)
                    gen_cache[gen_id] = gen.name if gen else None
                gen_name = gen_cache[gen_id]
            result.append(
                RecentEventSchema(
                    id=event.id,
                    event_type=event.event_type,
                    generator_name=gen_name,
                    created_at=event.created_at,
                    meta=event.meta,
                )
            )
        return result
