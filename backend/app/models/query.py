from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, description="The query string to search for")
    limit: int = Field(5, ge=1, le=50, description="Max number of context results to return")
    mode: str = Field("hybrid", description="Search mode: vector, graph, hybrid")

class SearchResultCard(BaseModel):
    chunk_id: str
    filename: str
    page_number: int
    text_content: str
    score: float
    metadata: Dict[str, Any] = {}

class AgentQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    stream: bool = False

class AgentQueryResponse(BaseModel):
    session_id: str
    response_text: str
    agent_routed: str
    citations: List[Dict[str, Any]] = []
    graph_context: Optional[Dict[str, Any]] = None
