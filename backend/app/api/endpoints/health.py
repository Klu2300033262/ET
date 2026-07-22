from fastapi import APIRouter, Request
from backend.app.models.base import BaseResponse

router = APIRouter()

import os
from backend.app.services.vector_store import vector_store
from backend.app.services.neo4j_service import neo4j_db
from backend.app.services.graph_query_service import graph_query
from backend.app.services.metrics_service import metrics_service

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
    import json
    
    # Check Document Storage
    doc_dir = os.path.join("data", "raw")
    docs_count = len([name for name in os.listdir(doc_dir) if os.path.isfile(os.path.join(doc_dir, name))]) if os.path.exists(doc_dir) else 0
    
    # Total Processed Documents
    metadata_dir = os.path.join("data", "processed", "metadata")
    processed_count = 0
    if os.path.exists(metadata_dir):
        for filename in os.listdir(metadata_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(metadata_dir, filename), "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        if meta.get("status") == "COMPLETED":
                            processed_count += 1
                except Exception:
                    pass
                    
    # Total Chunks
    chunks_dir = os.path.join("data", "processed", "chunks")
    chunks_count = 0
    if os.path.exists(chunks_dir):
        for doc_id in os.listdir(chunks_dir):
            chunks_file = os.path.join(chunks_dir, doc_id, "chunks.json")
            if os.path.exists(chunks_file):
                try:
                    with open(chunks_file, "r", encoding="utf-8") as f:
                        cdata = json.load(f)
                        chunks_count += len(cdata.get("chunks", []))
                except Exception:
                    pass

    # Check Vector Store
    chroma_status = "connected" if vector_store.collection else "offline"
    vector_count = vector_store.collection.count() if vector_store.collection else 0
    chroma_col_count = len(vector_store.client.list_collections()) if vector_store.client else 0
    
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
            "relationships": rel_count,
            # Extended Telemetry
            "total_uploaded_documents": docs_count,
            "total_processed_documents": processed_count,
            "total_chunks": chunks_count,
            "total_embeddings": vector_count,
            "total_vectors": vector_count,
            "total_neo4j_nodes": node_count,
            "total_relationships": rel_count,
            "chromadb_collection_count": chroma_col_count
        }
    )

@router.post(
    "/system/demo-mode",
    response_model=BaseResponse[dict],
    summary="Trigger Demo Mode",
    description="Automatically loads sample_manual.pdf, processes, embeds, and builds graph."
)
async def demo_mode():
    """Runs the full pipeline automatically on sample_manual.pdf."""
    import os
    import json
    import logging
    from fastapi import HTTPException
    from backend.app.services.document_service import process_document
    from backend.app.services.processing_service import process_document_pipeline
    from backend.app.services.vector_store import vector_store
    from backend.app.services.graph_builder import graph_builder
    
    logger = logging.getLogger("indusmind-ai")
    
    file_path = "sample_manual.pdf"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="sample_manual.pdf not found in root directory.")
        
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        class MockUploadFile:
            filename = "sample_manual.pdf"
            content_type = "application/pdf"
            
        upload_file = MockUploadFile()
        
        # 1. Upload & Parse
        doc_resp = await process_document(upload_file, file_bytes)
        doc_id = doc_resp.document_id
        
        # 2. Chunk
        process_document_pipeline(doc_id)
        
        # 3. Embed
        chunks_json_path = os.path.join("data", "processed", "chunks", doc_id, "chunks.json")
        with open(chunks_json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
            
        vector_store.ingest_chunks(payload.get("document_metadata", {}), payload.get("chunks", []))
        
        # 4. Graph
        graph_builder.build_graph_from_document(doc_id)
        
        return BaseResponse(
            success=True,
            message="Demo mode successfully processed sample_manual.pdf.",
            data={"document_id": doc_id}
        )
    except Exception as e:
        logger.error(f"Demo Mode Failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/system/logs",
    response_model=BaseResponse[dict],
    summary="Get System Logs",
    description="Retrieves the tail of the backend application logs."
)
async def system_logs(lines: int = 100):
    """Reads and returns the tail of the app.log file."""
    log_file = os.path.join("logs", "app.log")
    if not os.path.exists(log_file):
        return BaseResponse(success=False, message="Log file not found", data={"logs": []})
    try:
        with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
            log_lines = f.readlines()
            tail_lines = log_lines[-lines:]
            return BaseResponse(success=True, message="Logs retrieved successfully", data={"logs": [line.strip() for line in tail_lines]})
    except Exception as e:
        return BaseResponse(success=False, message=f"Failed to read logs: {str(e)}", data={"logs": []})

@router.get(
    "/system/routes",
    response_model=BaseResponse[dict],
    summary="Get System Routes",
    description="Lists all active FastAPI route patterns and methods."
)
async def system_routes(request: Request):
    """Iterates through and lists all registered routes."""
    routes = []
    for r in request.app.routes:
        routes.append({
            "path": r.path,
            "name": r.name,
            "methods": list(r.methods) if hasattr(r, "methods") else []
        })
    return BaseResponse(success=True, message="Routes retrieved successfully", data={"routes": routes})

@router.get(
    "/system/metrics",
    response_model=BaseResponse[dict],
    summary="Get System Metrics",
    description="Aggregates and returns core system metrics and usage statistics."
)
async def system_metrics():
    """Returns aggregated system metrics including documents, chunks, vectors, requests and processing statistics."""
    import json
    
    # Check Document Storage
    doc_dir = os.path.join("data", "raw")
    docs_count = len([name for name in os.listdir(doc_dir) if os.path.isfile(os.path.join(doc_dir, name))]) if os.path.exists(doc_dir) else 0
    
    # Total Processed Documents
    metadata_dir = os.path.join("data", "processed", "metadata")
    processed_count = 0
    if os.path.exists(metadata_dir):
        for filename in os.listdir(metadata_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(metadata_dir, filename), "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        if meta.get("status") == "COMPLETED":
                            processed_count += 1
                except Exception:
                    pass
                    
    # Total Chunks
    chunks_dir = os.path.join("data", "processed", "chunks")
    chunks_count = 0
    if os.path.exists(chunks_dir):
        for doc_id in os.listdir(chunks_dir):
            chunks_file = os.path.join(chunks_dir, doc_id, "chunks.json")
            if os.path.exists(chunks_file):
                try:
                    with open(chunks_file, "r", encoding="utf-8") as f:
                        cdata = json.load(f)
                        chunks_count += len(cdata.get("chunks", []))
                except Exception:
                    pass

    # Check Vector Store
    vector_count = vector_store.collection.count() if vector_store.collection else 0
    
    # Check Neo4j
    graph_stats = graph_query.get_database_statistics()
    node_count = graph_stats.get("nodes", 0)
    rel_count = graph_stats.get("relationships", 0)
    
    # Tracked Metrics
    metrics = metrics_service.get_metrics()
    
    return BaseResponse(
        success=True,
        message="System metrics retrieved successfully.",
        data={
            "documents": docs_count,
            "processed_documents": processed_count,
            "chunks": chunks_count,
            "embeddings": vector_count,
            "vectors": vector_count,
            "graph_nodes": node_count,
            "graph_relationships": rel_count,
            "ai_requests": metrics.get("ai_requests", 0),
            "search_requests": metrics.get("search_requests", 0),
            "avg_processing_time": metrics.get("avg_processing_time_ms", 0.0),
            "avg_confidence": metrics.get("avg_confidence", 0.0)
        }
    )
