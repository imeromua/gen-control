import hashlib
from datetime import datetime, timezone
import logging

from jose import JWTError, jwt
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import UnauthorizedException
from app.common.utils import verify_password
from app.config import settings
from app.modules.auth.schemas import LoginRequest, TokenResponse
from app.modules.users.models import User
from app.modules.users.repository import UserRepository

ALGORITHM = "HS256"
REDIS_TOKEN_PREFIX = "token:"

logger = logging.getLogger(__name__)


def _token_hash(token: str) -> str:
    """SHA-256 хеш токена — використовується як Redis-ключ, щоб не зберігати повний JWT."""
    return hashlib.sha256(token.encode()).hexdigest()


def _create_access_token(user: User) -> str:
    now = datetime.now(tz=timezone.utc)
    expire_seconds = settings.jwt_expiration_seconds
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role.name,
        "iat": int(now.timestamp()),
        "exp": int(now.timestamp()) + expire_seconds,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


class AuthService:
    def __init__(self, db: AsyncSession, redis: Redis):
        self.repo = UserRepository(db)
        self.redis = redis

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.repo.get_by_username(data.username)
        if not user or not verify_password(data.password, user.password_hash):
            raise UnauthorizedException(detail="Invalid username or password")

        if not user.is_active:
            raise UnauthorizedException(detail="User account is disabled")

        token = _create_access_token(user)
        redis_key = f"{REDIS_TOKEN_PREFIX}{_token_hash(token)}"
        await self.redis.setex(redis_key, settings.jwt_expiration_seconds, str(user.id))

        return TokenResponse(access_token=token)

    async def logout(self, token: str) -> None:
        try:
            redis_key = f"{REDIS_TOKEN_PREFIX}{_token_hash(token)}"
            await self.redis.delete(redis_key)
        except RedisError as exc:
            logger.error("Failed to invalidate token in Redis during logout: %s", exc)
            raise UnauthorizedException(
                detail="Logout failed: session storage unavailable. Please try again later."
            ) from exc

    async def get_current_user(self, token: str) -> User:
        redis_key = f"{REDIS_TOKEN_PREFIX}{_token_hash(token)}"
        stored = await self.redis.get(redis_key)
        if not stored:
            raise UnauthorizedException(detail="Token is invalid or expired")

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        except JWTError:
            raise UnauthorizedException(detail="Token signature is invalid")

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedException(detail="Token payload is malformed")

        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UnauthorizedException(detail="User not found")

        if not user.is_active:
            raise UnauthorizedException(detail="User account is disabled")

        return user
