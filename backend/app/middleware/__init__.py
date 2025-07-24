from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .rate_limit import RateLimitMiddleware
from .logging import LoggingMiddleware

def setup_middleware(app: FastAPI):
    """Setup all middleware for the application"""
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Rate limiting
    app.add_middleware(RateLimitMiddleware)
    
    # Request logging
    app.add_middleware(LoggingMiddleware)