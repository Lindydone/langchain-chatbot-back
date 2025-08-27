# db/redis.py (내부에서 adapters의 팩토리를 사용)
from typing import Optional
from redis.asyncio import Redis
from api.adapters.redis_adapters import create_redis
import logging

logger = logging.getLogger(__name__)
_redis: Optional[Redis] = None

async def init_redis() -> None:
    global _redis
    if _redis is None:
        _redis = create_redis()
        try:
            ok = await _redis.ping()
            if not ok:
                logger.warning("Redis ping returned falsy result.")
        except Exception as e:
            logger.exception("Redis init failed: %s", e)
            _redis = None

def get_redis() -> Redis:
    if _redis is None:
        raise RuntimeError("Redis is not initialized. Call init_redis() first.")
    return _redis

async def close_redis() -> None:
    global _redis
    if _redis is not None:
        try:
            await _redis.aclose()
        finally:
            _redis = None
