import asyncio
from functools import wraps
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

def retry_async(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Async retry decorator with exponential backoff"""
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"Failed after {max_attempts} attempts: {e}")
                        raise
                    
                    logger.warning(
                        f"Attempt {attempt} failed: {e}. "
                        f"Retrying in {current_delay} seconds..."
                    )
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
            
            return None
        
        return wrapper
    
    return decorator