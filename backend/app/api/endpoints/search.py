from fastapi import APIRouter, HTTPException, status
from typing import Optional, List, Dict, Any
import logging
from backend.app.services.retriever_service import retriever_service
from backend.app.models.base import BaseResponse
from backend.app.models.search import SearchRequest

logger = logging.getLogger("indusmind-ai")
router = APIRouter()

@router.post(
    "",
    response_model=BaseResponse,
    summary="Semantic Vector Retrieval",
    description="Retrieves the most semantically relevant text chunks from the local ChromaDB vector store based on the query."
)
async def search_documents(request: SearchRequest):
    """Executes a semantic vector search without invoking AI response generation."""
    try:
        results = retriever_service.search(
            query=request.query,
            top_k=request.top_k,
            document_id=request.document_id,
            threshold=request.threshold
        )
        
        return BaseResponse(
            success=True,
            message=f"Retrieved {len(results)} relevant chunks.",
            data={"results": results}
        )
    except Exception as e:
        logger.error(f"Search Execution Failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during semantic search: {str(e)}"
        )
