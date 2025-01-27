"""
Application Lifespan Events

This module handles the application's startup and shutdown events.
It initializes necessary resources and ensures proper cleanup.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..supabase.deps import init_super_client, close_super_client

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manages the application's lifespan events.
    
    Startup:
    - Initializes Supabase client
    - Sets up logging
    
    Shutdown:
    - Closes Supabase client
    - Performs cleanup
    """
    try:
        logger.info("Starting application...")
        await init_super_client()
        logger.info("Application startup complete")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        logger.info("Shutting down application...")
        try:
            await close_super_client()
            logger.info("Application shutdown complete")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")
