from fastapi import APIRouter, HTTPException, status
from typing import Optional, List, Dict, Any
import logging
from backend.app.services.retriever_service import retriever_service
from backend.app.models.base import BaseResponse
from backend.app.models.search import SearchRequest
from backend.app.services.metrics_service import metrics_service

logger = logging.getLogger("indusmind-ai")
router = APIRouter()

from pydantic import BaseModel

class SearchResponse(BaseModel):
    success: bool
    message: str
    results: List[Dict[str, Any]]
    data: Dict[str, Any]

@router.post(
    "",
    response_model=SearchResponse,
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
        
        metrics_service.record_search()
        
        # Return standardized response supporting multiple access patterns
        # 1. response.data.results (body.results)
        # 2. response.data.data.results (body.data.results)
        return SearchResponse(
            success=True,
            message=f"Retrieved {len(results)} relevant chunks.",
            results=results,
            data={"results": results}
        )
    except Exception as e:
        logger.error(f"Search Execution Failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during semantic search: {str(e)}"
        )
