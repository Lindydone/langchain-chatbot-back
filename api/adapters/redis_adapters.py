from __future__ import annotations
from typing import Optional
from redis.asyncio import Redis
from config import settings

def create_redis(
    host: Optional[str] = None,
    port: Optional[int] = None,
    db: Optional[int] = None,
    password: Optional[str] = None,
    decode_responses: bool = True,
) -> Redis:
    kwargs = dict(
        host=host or settings.redis_host,
        port=port or settings.redis_port,
        db=(db if db is not None else settings.redis_db_sess),
        decode_responses=decode_responses,
    )
    pwd = password if password is not None else getattr(settings, "redis_password", None)
    if pwd:
        kwargs["password"] = pwd
    return Redis(**kwargs)