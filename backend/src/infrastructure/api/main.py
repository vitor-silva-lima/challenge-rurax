from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.api.controllers.auth_controller import (
    router as auth_router
)
from src.infrastructure.api.controllers.movie_controller import (
    router as movie_router
)
from src.infrastructure.api.controllers.like_controller import (
    router as like_router
)
from src.infrastructure.api.controllers.recommendation_controller import (
    router as recommendation_router
)
from src.infrastructure.api.controllers.csv_controller import (
    router as csv_router
)
from src.infrastructure.config.settings import settings
from src.infrastructure.config.logging import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager to manage application lifecycle."""
    # Startup
    configure_logging()

    yield

    # Shutdown
    pass


def create_application() -> FastAPI:
    """Factory function to create FastAPI application."""
    app = FastAPI(
        title=settings.project_name,
        description="Movie Recommendation System - Clean Architecture",
        version="2.0.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routers
    app.include_router(
        router=auth_router,
        prefix=f"{settings.api_v1_str}/auth",
        tags=["Authentication"]
    )

    app.include_router(
        router=movie_router,
        prefix=f"{settings.api_v1_str}/movies",
        tags=["Movies"]
    )

    app.include_router(
        router=like_router,
        prefix=f"{settings.api_v1_str}/likes",
        tags=["Likes"]
    )

    app.include_router(
        router=recommendation_router,
        prefix=f"{settings.api_v1_str}/recommendations",
        tags=["Recommendations"]
    )

    app.include_router(
        router=csv_router,
        prefix=f"{settings.api_v1_str}/csv",
        tags=["CSV Import"]
    )

    # Health check endpoint
    @app.get(path="/health")
    def health_check():
        return {
            "status": "healthy",
            "service": settings.project_name,
            "version": "2.0.0"
        }

    return app


# Create application instance
app = create_application()
