import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.lifespan import lifespan
from .item.api_v1 import endpoints as items
from .supabase.login_swagger import router as auth_router


def create_app() -> FastAPI:
    # init FastAPI with lifespan
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        generate_unique_id_function=lambda router: f"{router.tags[0]}-{router.name}",
    )
    # set CORS
    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include the routers
    app.include_router(items.router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    host = "localhost"
    port = 5000
    uvicorn.run(app, host=host, port=port)
