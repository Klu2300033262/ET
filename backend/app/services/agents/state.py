from typing import TypedDict, List, Dict, Any, Optional
import operator
from typing_extensions import Annotated

def reduce_list(left: List[Any], right: List[Any]) -> List[Any]:
    """Helper to append to lists during state updates rather than overwriting."""
    if left is None:
        return right or []
    if right is None:
        return left
    return left + right

def reduce_dict(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to merge dictionaries during state updates."""
    if left is None:
        return right or {}
    if right is None:
        return left
    merged = left.copy()
    merged.update(right)
    return merged

class AgentState(TypedDict):
    """
    The immutable state dictionary passed between all LangGraph nodes.
    Using Annotated reducers ensures parallel agent runs don't overwrite each other's traces.
    """
    # Core Request
    question: str
    document_filter: Optional[str]
    conversation_id: str
    
    # Execution Tracking
    selected_agents: Annotated[List[str], reduce_list]
    reasoning_trace: Annotated[List[str], reduce_list]
    processing_times: Annotated[Dict[str, float], reduce_dict]
    agent_errors: Annotated[List[str], reduce_list]
    
    # Internal Agent Results Aggregation
    retrieved_chunks: Annotated[List[Dict[str, Any]], reduce_list]
    graph_nodes: Annotated[List[Dict[str, Any]], reduce_list]
    maintenance_insights: Optional[str]
    compliance_insights: Optional[str]
    memory_context: Optional[str] # Added for the Memory Service
    
    # Final Output Computed by Knowledge Agent
    final_answer: Optional[str]
    overall_confidence: float
    sources: Annotated[List[str], reduce_list]
