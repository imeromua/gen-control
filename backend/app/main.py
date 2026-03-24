import logging
from contextlib import asynccontextmanager
from datetime import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.common.enums import RoleName
from app.common.utils import hash_password
from app.config import settings
from app.db.redis import close_redis, get_redis
from app.db.session import AsyncSessionLocal, engine
from app.modules.adjustments.models import Adjustment  # noqa: F401 – register models
from app.modules.adjustments.router import router as adjustments_router
from app.modules.auth.router import router as auth_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.eventlog.router import router as events_router
from app.modules.fuel.models import FuelDelivery, FuelRefill, FuelStock  # noqa: F401 – register models
from app.modules.fuel.repository import FuelRepository
from app.modules.fuel.router import router as fuel_router
from app.modules.generators.models import Generator, GeneratorSettings, EventLog  # noqa: F401 – register models
from app.modules.generators.router import router as generators_router
from app.modules.motohours.models import MotohoursLog, MaintenanceLog  # noqa: F401 – register models
from app.modules.motohours.router import router as motohours_router
from app.modules.oil.models import OilStock  # noqa: F401 – register models
from app.modules.oil.router import router as oil_router
from app.modules.outage.models import OutageSchedule  # noqa: F401 – register models
from app.modules.outage.router import router as outage_router
from app.modules.rules.service import RulesService  # noqa: F401
from app.modules.shifts.models import Shift, SystemSettings  # noqa: F401 – register models
from app.modules.shifts.repository import SystemSettingsRepository
from app.modules.shifts.router import router as shifts_router
from app.modules.users.models import Role, User  # noqa: F401 – register models
from app.modules.users.repository import UserRepository
from app.modules.users.router import router as users_router

logger = logging.getLogger(__name__)


async def _seed_initial_data() -> None:
    """Create default roles and first admin if tables are empty."""
    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)

        role_count = await repo.count_roles()
        if role_count == 0:
            logger.info("Seeding roles...")
            for role_name in RoleName:
                db.add(Role(name=role_name.value))
            await db.commit()
            logger.info("Roles created: ADMIN, OPERATOR, VIEWER")

        user_count = await repo.count_users()
        if user_count == 0:
            logger.info("Creating first admin user...")
            admin_role = await repo.get_role_by_name(RoleName.ADMIN.value)
            if admin_role:
                admin = User(
                    full_name=settings.ADMIN_FULLNAME,
                    username=settings.ADMIN_USERNAME,
                    password_hash=hash_password(settings.ADMIN_PASSWORD),
                    role_id=admin_role.id,
                )
                db.add(admin)
                await db.commit()
                logger.info(f"Admin user '{settings.ADMIN_USERNAME}' created")

        settings_repo = SystemSettingsRepository(db)
        existing_settings = await settings_repo.get()
        if existing_settings is None:
            logger.info("Seeding system_settings...")
            start_h, start_m = settings.DEFAULT_WORK_TIME_START.split(":")
            end_h, end_m = settings.DEFAULT_WORK_TIME_END.split(":")
            db.add(
                SystemSettings(
                    work_time_start=time(int(start_h), int(start_m)),
                    work_time_end=time(int(end_h), int(end_m)),
                )
            )
            await db.commit()
            logger.info(
                f"system_settings created: {settings.DEFAULT_WORK_TIME_START}–{settings.DEFAULT_WORK_TIME_END}"
            )

        fuel_repo = FuelRepository(db)
        existing_fuel_stock = await fuel_repo.get_stock()
        if existing_fuel_stock is None:
            logger.info("Seeding fuel_stock...")
            db.add(
                FuelStock(
                    fuel_type="A95",
                    current_liters=0,
                    max_limit_liters=200,
                    warning_level_liters=20,
                )
            )
            await db.commit()
            logger.info("fuel_stock created: A95, 0/200 liters, warning at 20")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _seed_initial_data()
    await get_redis()
    yield
    await close_redis()
    await engine.dispose()


app = FastAPI(title="GenControl API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(generators_router, prefix="/api")
app.include_router(motohours_router, prefix="/api")
app.include_router(shifts_router, prefix="/api")
app.include_router(fuel_router, prefix="/api")
app.include_router(oil_router, prefix="/api")
app.include_router(adjustments_router, prefix="/api")
app.include_router(outage_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}
