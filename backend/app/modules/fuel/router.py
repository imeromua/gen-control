from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_admin, require_admin_or_operator
from app.modules.fuel.schemas import (
    FuelDeliveryCreate,
    FuelDeliveryResponse,
    FuelRefillCreate,
    FuelRefillResponse,
    FuelStockResponse,
    FuelStockUpdate,
)
from app.modules.fuel.service import FuelService
from app.modules.users.models import User

router = APIRouter(prefix="/fuel", tags=["fuel"])


@router.get("/stock", response_model=FuelStockResponse)
async def get_stock(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = FuelService(db)
    return await service.get_stock()


@router.put("/stock", response_model=FuelStockResponse)
async def update_stock(
    data: FuelStockUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = FuelService(db)
    return await service.update_stock_settings(data, current_user)


@router.get("/deliveries", response_model=list[FuelDeliveryResponse])
async def list_deliveries(
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = FuelService(db)
    return await service.get_deliveries()


@router.post("/deliveries", response_model=FuelDeliveryResponse, status_code=201)
async def create_delivery(
    data: FuelDeliveryCreate,
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = FuelService(db)
    return await service.create_delivery(data, current_user)


@router.get("/refills", response_model=list[FuelRefillResponse])
async def list_refills(
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = FuelService(db)
    return await service.get_refills()


@router.post("/refills", response_model=FuelRefillResponse, status_code=201)
async def create_refill(
    data: FuelRefillCreate,
    current_user: User = Depends(require_admin_or_operator),
    db: AsyncSession = Depends(get_db),
):
    service = FuelService(db)
    return await service.create_refill(data, current_user)
