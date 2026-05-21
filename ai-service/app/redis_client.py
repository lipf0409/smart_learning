# Redis Client
import redis.asyncio as redis
from typing import Optional, Any
import json
from app.config import settings


class RedisClient:
    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """连接 Redis"""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        print(f"[Redis] Connected to {settings.REDIS_HOST}:{settings.REDIS_PORT}")

    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.close()
            print("[Redis] Disconnected")

    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not self.client:
            return None
        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(self, key: str, value: Any, ttl: int = None):
        """设置缓存值"""
        if not self.client:
            return
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str):
        """删除缓存"""
        if self.client:
            await self.client.delete(key)

    async def incr(self, key: str) -> int:
        """计数器加1"""
        if not self.client:
            return 0
        return await self.client.incr(key)

    async def expire(self, key: str, seconds: int):
        """设置过期时间"""
        if self.client:
            await self.client.expire(key, seconds)

    async def exists(self, key: str) -> bool:
        """检查key是否存在"""
        if not self.client:
            return False
        return await self.client.exists(key) > 0


redis_client = RedisClient()
