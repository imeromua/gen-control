import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.common.enums import RoleName
from app.common.utils import hash_password
from app.config import settings
from app.db.redis import close_redis, get_redis
from app.db.session import AsyncSessionLocal, engine
from app.modules.auth.router import router as auth_router
from app.modules.generators.models import Generator, GeneratorSettings, EventLog  # noqa: F401 – register models
from app.modules.generators.router import router as generators_router
from app.modules.motohours.models import MotohoursLog, MaintenanceLog  # noqa: F401 – register models
from app.modules.motohours.router import router as motohours_router
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _seed_initial_data()
    await get_redis()
    yield
    await close_redis()
    await engine.dispose()


app = FastAPI(title="GenControl API", version="1.0.0", lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(generators_router)
app.include_router(motohours_router)


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}
