import json
import redis.asyncio as aioredis
from typing import Optional

REDIS_URL = "redis://localhost:6379/0"


class RedisClient:
    def __init__(self, url: str = REDIS_URL):
        self.redis = aioredis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> Optional[dict]:
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: dict, ttl: int = 30) -> None:
        await self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        async for key in self.redis.scan_iter(match=pattern):
            await self.redis.delete(key)