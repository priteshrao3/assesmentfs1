import pickle
from typing import Any
import redis
import os
from fastapi import HTTPException

class CacheService:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.client = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            socket_connect_timeout=1,
            socket_timeout=1
        )

    def get(self, key: str) -> Any:
        try:
            cached = self.client.get(key)
            if cached:
                return pickle.loads(cached)
            return None
        except redis.RedisError:
            raise HTTPException(
                status_code=503,
                detail="Cache service unavailable"
            )

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        try:
            self.client.set(key, pickle.dumps(value), ex=ttl)
        except redis.RedisError:
            pass

    def delete(self, key: str) -> None:
        try:
            self.client.delete(key)
        except redis.RedisError:
            pass