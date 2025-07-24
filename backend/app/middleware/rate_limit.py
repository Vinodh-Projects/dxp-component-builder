from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = time.time()
        
        # Clean old entries
        self.clients[client_ip] = [
            timestamp for timestamp in self.clients[client_ip]
            if timestamp > now - self.period
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Add current request
        self.clients[client_ip].append(now)
        
        response = await call_next(request)
        return response