"""Main application module."""
import logging
import logging.config
import os
import uvicorn
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

from .core.config import settings
from .core.lifespan import lifespan
from .core.security import setup_security
from .item.api_v1.endpoints import router as items_router
from .supabase.login_swagger import router as auth_router


# Setup logging
logging_ini_path = Path(__file__).parents[2] / "logging.ini"
if logging_ini_path.exists():
    logging.config.fileConfig(logging_ini_path, disable_existing_loggers=False)
else:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )

logger = logging.getLogger("app")


def create_application() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        lifespan=lifespan,
    )

    # Security
    setup_security(app)

    # Middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Routers
    app.include_router(auth_router, prefix=settings.API_V1_STR)
    app.include_router(items_router, prefix=settings.API_V1_STR)

    return app


app = create_application()

if __name__ == "__main__":
    # Parse the host URL to get the hostname
    parsed_url = urlparse(str(settings.SERVER_HOST))
    
    uvicorn.run(
        "main:app",
        host=parsed_url.hostname or "localhost",
        port=settings.SERVER_PORT,
        reload=True,  # Development mode
    )
