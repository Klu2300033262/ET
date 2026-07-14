from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging
from backend.app.services.graph_builder import graph_builder
from backend.app.services.graph_query_service import graph_query
from backend.app.models.base import BaseResponse

logger = logging.getLogger("indusmind-ai")
router = APIRouter()

class CustomGraphQuery(BaseModel):
    query: str = Field(..., description="A safe, read-only Cypher query")
    parameters: dict = Field(default_factory=dict)

@router.post("/build/{document_id}", response_model=BaseResponse, summary="Build Knowledge Graph from Document")
async def build_graph(document_id: str):
    """Triggers the Stage 6 NLP extraction pipeline to map chunks into Neo4j."""
    try:
        result = graph_builder.build_graph_from_document(document_id)
        return BaseResponse(
            success=True,
            message="Graph extraction and insertion complete.",
            data={"entities_found": len(result.entities), "relationships_found": len(result.relationships)}
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Graph Build Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An error occurred while building the graph.")

@router.post("/query", response_model=BaseResponse, summary="Execute Custom Graph Query")
async def execute_query(request: CustomGraphQuery):
    """Executes a custom query and returns frontend-ready visualization JSON."""
    try:
        # Basic security check - prevent write operations from this endpoint
        if "MERGE " in request.query.upper() or "SET " in request.query.upper() or "DELETE " in request.query.upper() or "CREATE " in request.query.upper():
            raise HTTPException(status_code=403, detail="Only READ queries (MATCH/RETURN) are allowed from the frontend API.")
            
        result = graph_query.execute_custom_query(request.query, request.parameters)
        return BaseResponse(success=True, message="Query executed.", data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics", response_model=BaseResponse, summary="Get Graph Volume Stats")
async def get_statistics():
    """Returns total nodes and relationships in the AuraDB cluster."""
    try:
        stats = graph_query.get_database_statistics()
        return BaseResponse(success=True, message="Statistics retrieved.", data=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/node/{id}", response_model=BaseResponse, summary="Find Connected Graph Components")
async def get_node_connections(id: str):
    """Retrieves the 2-hop topological neighborhood around a specific entity name."""
    try:
        result = graph_query.find_connected_components(id)
        return BaseResponse(success=True, message=f"Retrieved connections for {id}", data=result.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
