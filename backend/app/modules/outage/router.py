import uuid
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_active, require_admin
from app.modules.outage.schemas import OutageCreate, OutageResponse
from app.modules.outage.service import OutageService
from app.modules.users.models import User

router = APIRouter(prefix="/outage", tags=["outage"])


@router.get("", response_model=list[OutageResponse])
async def list_outage(
    from_date: date | None = None,
    to_date: date | None = None,
    current_user: User = Depends(require_active),
    db: AsyncSession = Depends(get_db),
):
    service = OutageService(db)
    return await service.get_all(from_date=from_date, to_date=to_date)


@router.get("/next", response_model=OutageResponse | None)
async def get_next_outage(
    current_user: User = Depends(require_active),
    db: AsyncSession = Depends(get_db),
):
    service = OutageService(db)
    return await service.get_next()


@router.post("", response_model=OutageResponse, status_code=201)
async def create_outage(
    data: OutageCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = OutageService(db)
    return await service.create(data, current_user.id)


@router.delete("/{outage_id}", status_code=204)
async def delete_outage(
    outage_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = OutageService(db)
    await service.delete(outage_id)
