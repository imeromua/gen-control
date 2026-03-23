from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import RoleName
from app.common.exceptions import ForbiddenException
from app.db.redis import get_redis
from app.db.session import get_db
from app.modules.auth.service import AuthService
from app.modules.users.models import User

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> User:
    token = credentials.credentials
    service = AuthService(db, redis)
    return await service.get_current_user(token)


async def require_active(user: User = Depends(get_current_user)) -> User:
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role.name != RoleName.ADMIN:
        raise ForbiddenException(detail="Admin role required")
    return user
