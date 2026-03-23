import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_admin, require_admin_or_operator
from app.modules.motohours.schemas import MaintenanceCreate, MaintenanceLogResponse, MotohoursLogResponse, MotohoursTotalResponse
from app.modules.motohours.service import MotohoursService
from app.modules.users.models import User

router = APIRouter(prefix="/generators", tags=["motohours"])


@router.get("/{generator_id}/motohours", response_model=list[MotohoursLogResponse])
async def list_motohours(
    generator_id: uuid.UUID,
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = MotohoursService(db)
    return await service.get_log(generator_id)


@router.get("/{generator_id}/motohours/total", response_model=MotohoursTotalResponse)
async def get_motohours_total(
    generator_id: uuid.UUID,
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = MotohoursService(db)
    return await service.get_total(generator_id)


@router.get("/{generator_id}/maintenance", response_model=list[MaintenanceLogResponse])
async def list_maintenance(
    generator_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = MotohoursService(db)
    return await service.get_maintenance_log(generator_id)


@router.post("/{generator_id}/maintenance", response_model=MaintenanceLogResponse, status_code=201)
async def create_maintenance(
    generator_id: uuid.UUID,
    data: MaintenanceCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = MotohoursService(db)
    return await service.create_maintenance(generator_id, data, current_user.id)
