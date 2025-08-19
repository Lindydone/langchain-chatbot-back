import redis
from api.core.config import settings

class RedisAdapter:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            password=settings.redis_password,
            db=settings.redis_db_sess,
            decode_responses=True,
        )

    def set_value(self, key: str, value: str):
        self.client.set(key, value)

    def get_value(self, key: str) -> str | None:
        return self.client.get(key)