import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.users.models import Role, User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User).options(selectinload(User.role)).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(
            select(User).options(selectinload(User.role)).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[User]:
        result = await self.db.execute(
            select(User).options(selectinload(User.role)).order_by(User.created_at)
        )
        return list(result.scalars().all())

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        # Reload with relationships
        return await self.get_by_id(user.id)

    async def update(self, user: User) -> User:
        await self.db.flush()
        await self.db.refresh(user)
        return await self.get_by_id(user.id)

    async def get_role_by_name(self, name: str) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def get_role_by_id(self, role_id: uuid.UUID) -> Role | None:
        result = await self.db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def count_users(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(User))
        return result.scalar_one()

    async def count_roles(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Role))
        return result.scalar_one()
