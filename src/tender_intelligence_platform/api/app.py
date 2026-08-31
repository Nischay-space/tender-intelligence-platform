from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from tender_intelligence_platform.api.routes.ingestion import (
    router as ingestion_router,
)
from tender_intelligence_platform.api.routes.tenders import (
    router as tender_router,
)
from tender_intelligence_platform.config.settings import settings


app = FastAPI(
    title="Tender Intelligence Platform",
    description="API for government tender intelligence and evaluation.",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


app.include_router(tender_router)
app.include_router(ingestion_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "tender-intelligence-platform",
    }