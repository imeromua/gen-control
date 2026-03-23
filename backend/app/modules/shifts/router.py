import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_admin, require_admin_or_operator
from app.modules.shifts.schemas import ShiftResponse, ShiftStartRequest, WorkTimeResponse, WorkTimeUpdate
from app.modules.shifts.service import ShiftService
from app.modules.users.models import User

router = APIRouter(tags=["shifts"])


@router.get("/settings/work-time", response_model=WorkTimeResponse)
async def get_work_time(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ShiftService(db)
    return await service.get_work_time_settings()


@router.put("/settings/work-time", response_model=WorkTimeResponse)
async def update_work_time(
    data: WorkTimeUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = ShiftService(db)
    return await service.update_work_time_settings(data, current_user)


@router.get("/shifts/", response_model=list[ShiftResponse])
async def list_shifts(
    generator_id: uuid.UUID | None = Query(None),
    status: str | None = Query(None),
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = ShiftService(db)
    return await service.get_all(generator_id=generator_id, status=status)


@router.get("/shifts/active", response_model=ShiftResponse | None)
async def get_active_shift(
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = ShiftService(db)
    return await service.get_active()


@router.post("/shifts/start", response_model=ShiftResponse, status_code=201)
async def start_shift(
    data: ShiftStartRequest,
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = ShiftService(db)
    return await service.start(data, current_user)


@router.post("/shifts/{shift_id}/stop", response_model=ShiftResponse)
async def stop_shift(
    shift_id: uuid.UUID,
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = ShiftService(db)
    return await service.stop(shift_id, current_user)


@router.get("/shifts/{shift_id}", response_model=ShiftResponse)
async def get_shift(
    shift_id: uuid.UUID,
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = ShiftService(db)
    return await service.get_by_id(shift_id)
