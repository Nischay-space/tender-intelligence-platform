from fastapi import APIRouter


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
def health_check() -> dict[str, str]:
    """Return API health status."""

    return {
        "status": "ok",
    }