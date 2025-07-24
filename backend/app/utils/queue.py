import redis.asyncio as redis
import json
from typing import Dict, Any, Optional
from app.config import settings

class TaskQueue:
    """Redis-based task queue for async processing"""
    
    def __init__(self):
        self.redis_client = None
        self.queue_name = "aem_generation_queue"
        self.status_prefix = "aem_status:"
        self.result_prefix = "aem_result:"
    
    async def initialize(self):
        """Initialize Redis connection"""
        self.redis_client = await redis.from_url(settings.REDIS_URL)
    
    async def cleanup(self):
        """Cleanup Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def enqueue(self, task: Dict[str, Any]):
        """Add task to queue"""
        request_id = task.get("request_id")
        
        # Save initial status
        await self.update_status(request_id, {
            "status": "queued",
            "progress": 0,
            "current_step": "Waiting in queue"
        })
        
        # Add to queue
        await self.redis_client.lpush(
            self.queue_name,
            json.dumps(task)
        )
    
    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """Get task from queue"""
        result = await self.redis_client.rpop(self.queue_name)
        if result:
            return json.loads(result)
        return None
    
    async def update_status(self, request_id: str, status: Dict[str, Any]):
        """Update task status"""
        key = f"{self.status_prefix}{request_id}"
        await self.redis_client.setex(
            key,
            3600,  # 1 hour TTL
            json.dumps(status)
        )
    
    async def get_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        key = f"{self.status_prefix}{request_id}"
        result = await self.redis_client.get(key)
        if result:
            return json.loads(result)
        return None
    
    async def save_result(self, request_id: str, result: Dict[str, Any]):
        """Save task result"""
        key = f"{self.result_prefix}{request_id}"
        await self.redis_client.setex(
            key,
            86400,  # 24 hour TTL
            json.dumps(result)
        )
    
    async def get_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get task result"""
        key = f"{self.result_prefix}{request_id}"
        result = await self.redis_client.get(key)
        if result:
            return json.loads(result)
        return None