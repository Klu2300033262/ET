from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
from backend.app.services.retriever_service import retriever_service
from backend.app.models.base import BaseResponse

logger = logging.getLogger("indusmind-ai")
router = APIRouter()

class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    document_id: Optional[str] = Field(None, description="Optional document ID to filter search scope")
    top_k: int = Field(5, ge=1, le=50, description="Maximum number of relevant chunks to return")
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Override default similarity threshold")

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
