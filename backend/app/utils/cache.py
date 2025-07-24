import redis.asyncio as redis
import json
from typing import Any, Optional
import hashlib
from app.config import settings

class CacheManager:
    """Redis-based cache manager"""
    
    def __init__(self):
        self.redis_client = None
        self.enabled = settings.ENABLE_CACHING
    
    async def _get_client(self):
        if not self.redis_client:
            self.redis_client = await redis.from_url(settings.REDIS_URL)
        return self.redis_client
    
    def _generate_key(self, key: str) -> str:
        """Generate cache key with prefix"""
        return f"aem_gen:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            client = await self._get_client()
            value = await client.get(self._generate_key(key))
            if value:
                return json.loads(value)
        except Exception as e:
            # Log error but don't fail
            print(f"Cache get error: {e}")
        
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        if not self.enabled:
            return
        
        try:
            client = await self._get_client()
            ttl = ttl or settings.CACHE_TTL
            await client.setex(
                self._generate_key(key),
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            # Log error but don't fail
            print(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete value from cache"""
        if not self.enabled:
            return
        
        try:
            client = await self._get_client()
            await client.delete(self._generate_key(key))
        except Exception as e:
            print(f"Cache delete error: {e}")