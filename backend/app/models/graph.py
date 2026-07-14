from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Offset(BaseModel):
    start: int
    end: int

class GraphEntity(BaseModel):
    """Represents a Node in the Knowledge Graph"""
    entity: str = Field(..., description="The exact text of the entity")
    type: str = Field(..., description="The category/type of the entity (e.g., Equipment, Fault)")
    confidence: float = Field(..., description="Extraction confidence score (0.0 to 1.0)")
    source_chunk: str = Field(..., description="The chunk ID where this entity was found")
    document_id: str = Field(..., description="The parent document ID")
    offset: Offset = Field(..., description="Character offsets within the source chunk")
    
class GraphRelationship(BaseModel):
    """Represents an Edge/Relationship between two Nodes"""
    source: str = Field(..., description="The source entity name")
    relationship: str = Field(..., description="The relationship type (e.g., LOCATED_IN)")
    target: str = Field(..., description="The target entity name")
    confidence: float = Field(..., description="Relationship extraction confidence score")
    
class GraphExtractionResult(BaseModel):
    """Payload of all extracted nodes and edges from a single document"""
    document_id: str
    entities: List[GraphEntity] = []
    relationships: List[GraphRelationship] = []
    
class GraphQueryResponse(BaseModel):
    """Schema for returning graph search queries to the frontend"""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    statistics: Dict[str, Any]
