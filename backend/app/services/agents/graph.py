import logging
from typing import List
from langgraph.graph import StateGraph, START, END

from backend.app.services.agents.state import AgentState
from backend.app.services.agents.nodes import (
    rule_based_router_node,
    memory_service_node,
    search_agent_node,
    graph_agent_node,
    maintenance_agent_node,
    compliance_agent_node,
    knowledge_agent_node
)

logger = logging.getLogger("indusmind-ai")

# 1. Initialize the Graph
builder = StateGraph(AgentState)

# 2. Add all Nodes
builder.add_node("Router", rule_based_router_node)
builder.add_node("MemoryService", memory_service_node)
builder.add_node("SearchAgent", search_agent_node)
builder.add_node("GraphAgent", graph_agent_node)
builder.add_node("MaintenanceAgent", maintenance_agent_node)
builder.add_node("ComplianceAgent", compliance_agent_node)
builder.add_node("KnowledgeAgent", knowledge_agent_node)

# 3. Define the routing function
def route_from_supervisor(state: AgentState) -> List[str]:
    """Returns the list of agent nodes the router selected to run in parallel."""
    return state.get("selected_agents", ["SearchAgent"])

# 4. Wire the Edges
# The journey always starts at the Router
builder.add_edge(START, "Router")

# From Router, conditionally branch to the selected expert agents
builder.add_conditional_edges(
    "Router",
    route_from_supervisor,
    {
        "MemoryService": "MemoryService",
        "SearchAgent": "SearchAgent",
        "GraphAgent": "GraphAgent",
        "MaintenanceAgent": "MaintenanceAgent",
        "ComplianceAgent": "ComplianceAgent"
    }
)

# All expert agents funnel their context directly into the isolated Knowledge Agent
builder.add_edge("MemoryService", "KnowledgeAgent")
builder.add_edge("SearchAgent", "KnowledgeAgent")
builder.add_edge("GraphAgent", "KnowledgeAgent")
builder.add_edge("MaintenanceAgent", "KnowledgeAgent")
builder.add_edge("ComplianceAgent", "KnowledgeAgent")

# The Knowledge Agent provides the final output and ends the chain
builder.add_edge("KnowledgeAgent", END)

# 5. Compile the highly-structured graph
indusmind_graph = builder.compile()
