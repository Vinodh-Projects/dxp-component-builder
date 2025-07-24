# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.routers import component_routes, health_router
from app.middleware import setup_middleware
from app.agents import AgentOrchestrator

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.orchestrator = AgentOrchestrator()
    await app.state.orchestrator.initialize()
    yield
    # Shutdown
    await app.state.orchestrator.cleanup()

# Create FastAPI app
app = FastAPI(
    title="AEM Component Generator Service",
    description="AI-powered AEM component generation from requirements and images",
    version="1.0.0",
    lifespan=lifespan
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(health_router.router, prefix="/api/v1/health", tags=["health"])
app.include_router(component_routes.router, prefix="/api/v1/components", tags=["components"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS
    )