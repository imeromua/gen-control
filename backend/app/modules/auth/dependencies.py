from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.enums import RoleName
from app.common.exceptions import ForbiddenException, UnauthorizedException
from app.db.redis import get_redis
from app.db.session import get_db
from app.modules.auth.service import AuthService
from app.modules.users.models import User

# Ініціалізуємо схему безпеки
security = HTTPBearer()

def get_auth_service(
    db: AsyncSession = Depends(get_db), 
    redis: Redis = Depends(get_redis)
) -> AuthService:
    """Інжектить AuthService з необхідними залежностями."""
    return AuthService(db, redis)

async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> User:
    """Отримує поточного користувача за JWT токеном."""
    user = await auth_service.get_current_user(token.credentials)
    if not user:
        raise UnauthorizedException(detail="Invalid or expired token")
    return user

async def require_active(
    current_user: User = Depends(get_current_user)
) -> User:
    """Перевіряє, чи активний користувач."""
    if not current_user.is_active:
        raise ForbiddenException(detail="User is inactive")
    return current_user

async def require_admin(
    current_user: User = Depends(require_active)
) -> User:
    """Перевіряє, чи має користувач права адміністратора (для adjustments та users)."""
    if current_user.role.name != RoleName.ADMIN.value:
        raise ForbiddenException(detail="Admin privileges required")
    return current_user

async def require_admin_or_operator(
    current_user: User = Depends(require_active)
) -> User:
    """Перевіряє, чи має користувач права адміна АБО оператора (для dashboard)."""
    if current_user.role.name not in [RoleName.ADMIN.value, RoleName.OPERATOR.value]:
        raise ForbiddenException(detail="Admin or Operator privileges required")
    return current_user

def require_role(roles: list[RoleName]):
    """Універсальна фабрика для перевірки доступу за списком ролей."""
    async def role_checker(current_user: User = Depends(require_active)) -> User:
        if current_user.role.name not in [r.value for r in roles]:
            raise ForbiddenException(detail="Insufficient permissions")
        return current_user
    return role_checker

# Аліас для зворотної сумісності
get_current_active_user = require_active