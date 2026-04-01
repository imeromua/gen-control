import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_admin, require_admin_or_operator
from app.modules.generators.schemas import (
    GeneratorCreate,
    GeneratorResponse,
    GeneratorSettingsResponse,
    GeneratorSettingsUpdate,
    GeneratorStatusResponse,
    GeneratorUpdate,
)
from app.modules.generators.service import GeneratorService
from app.modules.users.models import User

router = APIRouter(prefix="/generators", tags=["generators"])


@router.get("/", response_model=list[GeneratorResponse])
async def list_generators(
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = GeneratorService(db)
    return await service.get_all()


@router.post("/", response_model=GeneratorResponse, status_code=201)
async def create_generator(
    data: GeneratorCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = GeneratorService(db)
    return await service.create(data, current_user.id)


@router.get("/{generator_id}", response_model=GeneratorResponse)
async def get_generator(
    generator_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = GeneratorService(db)
    return await service.get_by_id(generator_id)


@router.patch("/{generator_id}", response_model=GeneratorResponse)
async def update_generator(
    generator_id: uuid.UUID,
    data: GeneratorUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = GeneratorService(db)
    return await service.update(generator_id, data, current_user.id)


@router.delete("/{generator_id}", response_model=GeneratorResponse)
async def deactivate_generator(
    generator_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = GeneratorService(db)
    return await service.deactivate(generator_id, current_user.id)


@router.get("/{generator_id}/settings", response_model=GeneratorSettingsResponse)
async def get_settings(
    generator_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = GeneratorService(db)
    return await service.get_settings(generator_id)


@router.put("/{generator_id}/settings", response_model=GeneratorSettingsResponse)
async def update_settings(
    generator_id: uuid.UUID,
    data: GeneratorSettingsUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = GeneratorService(db)
    return await service.update_settings(generator_id, data, current_user.id)


@router.get("/{generator_id}/status", response_model=GeneratorStatusResponse)
async def get_status(
    generator_id: uuid.UUID,
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = GeneratorService(db)
    return await service.get_status(generator_id)
