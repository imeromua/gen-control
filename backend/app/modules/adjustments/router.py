import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.adjustments.schemas import AdjustmentCreate, AdjustmentResponse
from app.modules.adjustments.service import AdjustmentService
from app.modules.auth.dependencies import require_admin
from app.modules.users.models import User

router = APIRouter(prefix="/adjustments", tags=["adjustments"])


@router.get("", response_model=list[AdjustmentResponse])
async def list_adjustments(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdjustmentService(db)
    return await service.get_all()


@router.post("", response_model=AdjustmentResponse, status_code=201)
async def create_adjustment(
    data: AdjustmentCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdjustmentService(db)
    return await service.create(data, current_user.id)


@router.get("/{adjustment_id}", response_model=AdjustmentResponse)
async def get_adjustment(
    adjustment_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = AdjustmentService(db)
    return await service.get_by_id(adjustment_id)
