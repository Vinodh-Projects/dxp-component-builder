from fastapi import APIRouter
from datetime import datetime
import psutil
import redis

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/detailed")
async def detailed_health_check():
    """Detailed health check with system metrics"""
    
    # Check Redis connection
    redis_status = "healthy"
    try:
        r = redis.from_url("redis://localhost:6379")
        r.ping()
    except:
        redis_status = "unhealthy"
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "services": {
            "redis": redis_status,
            "openai": "configured" if os.getenv("OPENAI_API_KEY") else "not configured",
            "anthropic": "configured" if os.getenv("ANTHROPIC_API_KEY") else "not configured"
        }
    }