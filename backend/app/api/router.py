from fastapi import APIRouter
from backend.app.api.endpoints import health

api_router = APIRouter()

# Grouping core endpoints under a stable v1 path
api_router.include_router(health.router, tags=["System Health"])

# Placeholders for future stage endpoints:
# api_router.include_router(documents.router, prefix="/documents", tags=["Document Ingestion"])
# api_router.include_router(search.router, prefix="/search", tags=["Semantic Search"])
# api_router.include_router(agents.router, prefix="/agents", tags=["Agent Workflows"])
