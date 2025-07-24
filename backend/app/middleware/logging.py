from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid

logger = logging.getLogger("api.requests")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Log request
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response {request_id}: "
            f"status={response.status_code} "
            f"duration={process_time:.3f}s"
        )
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response