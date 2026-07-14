from fastapi import APIRouter
from backend.app.api.endpoints import health, documents, processing

api_router = APIRouter()

# Grouping core endpoints under a stable v1 path
api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(processing.router, prefix="/documents", tags=["Processing"])

# Placeholder endpoints for OpenAPI Tag generation in Swagger UI
# We include empty routers to generate the tags cleanly in the UI
api_router.include_router(APIRouter(), prefix="/knowledge", tags=["Knowledge"])
api_router.include_router(APIRouter(), prefix="/agents", tags=["Agents"])
api_router.include_router(APIRouter(), prefix="/search", tags=["Search"])
api_router.include_router(APIRouter(), prefix="/compliance", tags=["Compliance"])
api_router.include_router(APIRouter(), prefix="/maintenance", tags=["Maintenance"])
