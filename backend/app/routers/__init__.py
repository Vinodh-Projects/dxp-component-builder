from .component_routes import router as component_router
from .project_routes import router as project_router
from .aem_routes import router as aem_router

__all__ = ["component_router", "project_router", "aem_router"]