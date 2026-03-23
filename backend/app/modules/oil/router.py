import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_admin
from app.modules.oil.schemas import OilStockCreate, OilStockResponse, OilStockUpdate
from app.modules.oil.service import OilService
from app.modules.users.models import User

router = APIRouter(prefix="/oil", tags=["oil"])


@router.get("/", response_model=list[OilStockResponse])
async def list_oil_stocks(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = OilService(db)
    return await service.get_all()


@router.post("/", response_model=OilStockResponse, status_code=201)
async def create_oil_stock(
    data: OilStockCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = OilService(db)
    return await service.create(data, current_user)


@router.patch("/{oil_id}", response_model=OilStockResponse)
async def update_oil_stock(
    oil_id: uuid.UUID,
    data: OilStockUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = OilService(db)
    return await service.update(oil_id, data, current_user)
