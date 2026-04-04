import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictException, NotFoundException
from app.common.utils import hash_password
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def get_all(self) -> list[User]:
        return await self.repo.get_all()

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundException(
                detail=f"User with id '{user_id}' not found"
            )
        return user

    async def create(self, data: UserCreate) -> User:
        existing = await self.repo.get_by_username(data.username)
        if existing:
            raise ConflictException(
                detail=f"Username '{data.username}' already taken"
            )

        role = await self.repo.get_role_by_id(data.role_id)
        if not role:
            raise NotFoundException(
                detail=f"Role with id '{data.role_id}' not found"
            )

        user = User(
            full_name=data.full_name,
            username=data.username,
            password_hash=hash_password(data.password),
            role_id=data.role_id,
        )

        created = await self.repo.create(user)
        await self.db.flush()
        return created

    async def update(self, user_id: uuid.UUID, data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)

        if data.role_id is not None:
            role = await self.repo.get_role_by_id(data.role_id)
            if not role:
                raise NotFoundException(detail=f"Role with id '{data.role_id}' not found")
            user.role_id = data.role_id

        if data.full_name is not None:
            user.full_name = data.full_name

        if data.is_active is not None:
            user.is_active = data.is_active

        updated = await self.repo.update(user)
        await self.db.flush()
        return updated

    async def deactivate(self, user_id: uuid.UUID) -> User:
        user = await self.get_by_id(user_id)
        user.is_active = False
        updated = await self.repo.update(user)
        await self.db.flush()
        return updated
