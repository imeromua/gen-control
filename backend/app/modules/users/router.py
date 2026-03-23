import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.auth.dependencies import require_admin
from app.modules.users.schemas import UserCreate, UserResponse, UserUpdate
from app.modules.users.service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=list[UserResponse])
async def list_users(
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_all()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.create(data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.get_by_id(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.update(user_id, data)


@router.delete("/{user_id}", response_model=UserResponse)
async def deactivate_user(
    user_id: uuid.UUID,
    _: None = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    return await service.deactivate(user_id)
