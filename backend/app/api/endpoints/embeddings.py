import os
import json
import logging
from fastapi import APIRouter, HTTPException, status
from backend.app.services.vector_store import vector_store
from backend.app.models.base import BaseResponse

logger = logging.getLogger("indusmind-ai")
router = APIRouter()

@router.post(
    "/{document_id}/embed",
    response_model=BaseResponse,
    summary="Generate and Store Vector Embeddings",
    description="Consumes a chunks.json file produced by Stage 4, converts it into embeddings, and safely loads it into ChromaDB."
)
async def embed_document(document_id: str):
    """Triggers the Stage 5 Embedding Pipeline for a chunked document."""
    
    chunks_json_path = os.path.join("data", "processed", "chunks", document_id, "chunks.json")
    
    if not os.path.exists(chunks_json_path):
        logger.error(f"Missing chunk data for document_id: {document_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chunk data missing for {document_id}. Has Stage 4 completed?"
        )
        
    try:
        with open(chunks_json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
            
        document_metadata = payload.get("document_metadata", {})
        chunks = payload.get("chunks", [])
        
        if not chunks:
            raise ValueError("No chunks found in payload.")
            
        was_ingested = vector_store.ingest_chunks(document_metadata, chunks)
        
        if not was_ingested:
            return BaseResponse(
                success=True,
                message="Embeddings already exist in cache. Skipped regeneration.",
                data={"status": "CACHED"}
            )
            
        return BaseResponse(
            success=True,
            message=f"Successfully generated and stored {len(chunks)} embeddings.",
            data={"status": "EMBEDDED", "chunks_processed": len(chunks)}
        )
        
    except Exception as e:
        logger.error(f"Error during embedding generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating embeddings: {str(e)}"
        )
