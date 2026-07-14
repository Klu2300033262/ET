from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    """The incoming user query payload."""
    question: str = Field(..., description="The user's industrial question.")
    document_filter: Optional[str] = Field(default=None, description="Optional document ID to restrict search context.")
    conversation_id: str = Field(..., description="Session identifier for the Memory Agent.")

class ChatResponse(BaseModel):
    """The rich, highly-explainable output payload from the LangGraph execution."""
    answer: str = Field(..., description="The synthesized answer from the Knowledge Agent.")
    summary: str = Field(default="", description="A short one-sentence TL;DR.")
    agents_used: List[str] = Field(default_factory=list, description="Which specialized agents were invoked.")
    retrieved_chunks: List[Dict[str, Any]] = Field(default_factory=list, description="Raw chunks returned by ChromaDB.")
    graph_nodes: List[Dict[str, Any]] = Field(default_factory=list, description="Raw topology returned by Neo4j.")
    maintenance_analysis: Optional[str] = Field(default=None, description="Raw output from the Maintenance Expert Agent.")
    compliance_analysis: Optional[str] = Field(default=None, description="Raw output from the Compliance Expert Agent.")
    confidence: float = Field(..., description="Overall confidence computed by the Knowledge Agent (0.0 - 1.0).")
    execution_time_ms: int = Field(..., description="Total milliseconds taken by the LangGraph runner.")
    reasoning_trace: List[str] = Field(default_factory=list, description="Step-by-step trace of agent execution.")
    sources: List[str] = Field(default_factory=list, description="Unique source document IDs utilized.")
