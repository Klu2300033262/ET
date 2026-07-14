from fastapi import APIRouter
from backend.app.models.base import BaseResponse

router = APIRouter()

@router.get(
    "/health", 
    response_model=BaseResponse[dict],
    summary="System Health Check",
    description="Returns the operational status of the backend API system."
)
async def health_check():
    """Verify that the FastAPI service is running and accessible."""
    return BaseResponse(
        success=True,
        message="System is fully operational",
        data={"status": "healthy"}
    )
