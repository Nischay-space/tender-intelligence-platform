from fastapi import FastAPI

from tender_intelligence_platform.api.routes.tenders import (
    router as tender_router,
)


app = FastAPI(
    title="Tender Intelligence Platform",
    description="API for government tender intelligence and evaluation.",
    version="0.1.0",
)


app.include_router(tender_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "tender-intelligence-platform",
    }