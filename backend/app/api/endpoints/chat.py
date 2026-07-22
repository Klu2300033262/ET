import time
import logging
from fastapi import APIRouter, HTTPException
from backend.app.models.chat import ChatRequest, ChatResponse
from backend.app.services.agents.graph import indusmind_graph
from backend.app.services.metrics_service import metrics_service

logger = logging.getLogger("indusmind-ai")
router = APIRouter()

@router.post("/", response_model=ChatResponse, summary="Submit a query to the Multi-Agent System")
async def chat_endpoint(request: ChatRequest):
    """
    Invokes the LangGraph Supervisor to orchestrate Search, Graph, Maintenance, and Compliance agents.
    Returns a highly explainable payload with full context provenance and confidence bounding.
    """
    overall_start = time.time()
    logger.info(f"LangGraph execution triggered for query: '{request.question}'")
    
    # Initialize the strict AgentState payload
    initial_state = {
        "question": request.question,
        "document_filter": request.document_filter,
        "conversation_id": request.conversation_id,
        "selected_agents": [],
        "reasoning_trace": [],
        "processing_times": {},
        "agent_errors": [],
        "retrieved_chunks": [],
        "graph_nodes": [],
        "maintenance_insights": None,
        "compliance_insights": None,
        "memory_context": None,
        "final_answer": None,
        "overall_confidence": 0.0,
        "sources": []
    }
    
    try:
        # Execute the compiled LangGraph
        # This streams the state through the rule-based router -> parallel worker agents -> Knowledge LLM
        final_state = indusmind_graph.invoke(initial_state)
        
        execution_time_ms = int((time.time() - overall_start) * 1000)
        logger.info(f"LangGraph execution completed in {execution_time_ms}ms")
        
        # Determine brief summary (first sentence of answer)
        answer = final_state.get("final_answer", "Error resolving answer.")
        summary = answer.split(".")[0] + "." if "." in answer else answer
        
        confidence = final_state.get("overall_confidence", 0.0)
        metrics_service.record_chat(confidence)
        
        return ChatResponse(
            answer=answer,
            summary=summary,
            agents_used=final_state.get("selected_agents", []),
            retrieved_chunks=final_state.get("retrieved_chunks", []),
            graph_nodes=final_state.get("graph_nodes", []),
            maintenance_analysis=final_state.get("maintenance_insights"),
            compliance_analysis=final_state.get("compliance_insights"),
            confidence=confidence,
            execution_time_ms=execution_time_ms,
            reasoning_trace=final_state.get("reasoning_trace", []),
            sources=list(set(final_state.get("sources", []))) # Deduplicate final sources
        )
        
    except Exception as e:
        logger.error(f"LangGraph Workflow Error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="The Multi-Agent orchestration failed.")
