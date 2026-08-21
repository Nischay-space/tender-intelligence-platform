from fastapi import FastAPI

from tender_intelligence_platform.api.routes.health import (
    router as health_router,
)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title="Tender Intelligence Platform",
        version="0.1.0",
    )

    app.include_router(
        health_router,
        prefix="/api/v1",
    )

    return app


app = create_app()