from pydantic import BaseModel, Field
from typing import Optional

class SearchRequest(BaseModel):
    """Schema for incoming semantic search queries."""
    query: str = Field(..., description="Natural language search query")
    document_id: Optional[str] = Field(None, description="Optional document ID to filter search scope")
    top_k: int = Field(5, ge=1, le=50, description="Maximum number of relevant chunks to return")
    threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Override default similarity threshold")
