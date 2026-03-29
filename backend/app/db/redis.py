import asyncio

from redis.asyncio import Redis

from app.config import settings

redis_client: Redis | None = None
_redis_lock = asyncio.Lock()


async def get_redis() -> Redis:
    """Повертає єдиний глобальний Redis-клієнт. Потокобезпечна ініціалізація через asyncio.Lock."""
    global redis_client
    if redis_client is None:
        async with _redis_lock:
            if redis_client is None:
                redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client


async def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None
