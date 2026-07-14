from fastapi import APIRouter
from backend.app.models.base import BaseResponse

router = APIRouter()

import os
from backend.app.services.vector_store import vector_store
from backend.app.services.neo4j_service import neo4j_db
from backend.app.services.graph_query_service import graph_query

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
        data={
            "status": "healthy",
            "version": "1.0.0",
            "environment": "development",
            "service": "IndusMind AI Backend"
        }
    )

@router.get(
    "/system/status",
    response_model=BaseResponse[dict],
    summary="Live System Dashbaord Status",
    description="Aggregates connectivity and volume metrics across all intelligence layers."
)
async def system_status():
    """Returns total volume metrics for the live demo dashboard."""
    # Check Document Storage
    doc_dir = os.path.join("data", "raw")
    docs_count = len([name for name in os.listdir(doc_dir) if os.path.isfile(os.path.join(doc_dir, name))]) if os.path.exists(doc_dir) else 0
    
    # Check Vector Store
    chroma_status = "connected" if vector_store.collection else "offline"
    vector_count = vector_store.collection.count() if vector_store.collection else 0
    
    # Check Neo4j
    neo4j_status = "connected" if neo4j_db.is_online() else "offline"
    graph_stats = graph_query.get_database_statistics()
    node_count = graph_stats.get("nodes", 0)
    rel_count = graph_stats.get("relationships", 0)
    
    # Check Gemini
    gemini_status = "connected" if os.getenv("GEMINI_API_KEY") else "offline (missing key)"
    
    return BaseResponse(
        success=True,
        message="System telemetry retrieved successfully.",
        data={
            "backend": "healthy",
            "chromadb": chroma_status,
            "neo4j": neo4j_status,
            "gemini": gemini_status,
            "langgraph": "healthy",
            "documents": docs_count,
            "chunks": vector_count, # 1 Chunk = 1 Vector
            "vectors": vector_count,
            "nodes": node_count,
            "relationships": rel_count
        }
    )
