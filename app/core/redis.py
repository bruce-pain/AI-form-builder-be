from redis.asyncio import Redis, from_url

from app.core.config import settings


async def get_redis_client() -> Redis:
    redis = await from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.aclose()
