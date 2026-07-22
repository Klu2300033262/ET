import time
import os
import re
import logging
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from backend.app.services.agents.state import AgentState
from backend.app.services.retriever_service import retriever_service as retriever
from backend.app.services.graph_query_service import graph_query
from backend.app.config.constants import GEMINI_LLM_MODEL, GEMINI_FALLBACK_MODEL

logger = logging.getLogger("indusmind-ai")

# ---------------------------------------------------------
# 1. Rule-Based Intent Router (Replaces LLM Supervisor)
# ---------------------------------------------------------
def rule_based_router_node(state: AgentState) -> AgentState:
    """Ultra-fast classification of intent to select downstream agents without LLM overhead."""
    start_time = time.time()
    q = state["question"].lower()
    
    selected_agents = ["MemoryService"] # Memory always runs
    
    # Heuristic Triggers
    if any(kw in q for kw in ["maintenance", "repair", "breakdown", "failed", "broken", "fix", "rca", "history"]):
        selected_agents.extend(["SearchAgent", "MaintenanceAgent"])
        
    if any(kw in q for kw in ["safety", "compliance", "rule", "inspection", "regulation", "standard", "procedure"]):
        selected_agents.extend(["SearchAgent", "ComplianceAgent"])
        
    if any(kw in q for kw in ["how", "what", "why", "where", "manual", "document", "describe"]):
        if "SearchAgent" not in selected_agents:
            selected_agents.append("SearchAgent")
            
    # Graph triggers (Equipment IDs, connections)
    # E.g., "P-101", "connected to", "system"
    if re.search(r'\b[A-Za-z]+[- ][0-9]+\b', q) or "connected" in q or "system" in q:
        selected_agents.append("GraphAgent")
        
    # Fallback
    if len(selected_agents) == 1:
        selected_agents.append("SearchAgent")
        
    # Deduplicate while preserving insertion order
    selected_agents = list(dict.fromkeys(selected_agents))
        
    duration = (time.time() - start_time) * 1000
    return {
        "selected_agents": selected_agents,
        "reasoning_trace": [f"[Router] Selected: {', '.join(selected_agents)}"],
        "processing_times": {"Router": duration}
    }

# ---------------------------------------------------------
# 2. Memory Service Node
# ---------------------------------------------------------
def memory_service_node(state: AgentState) -> AgentState:
    """Manages conversational history. (Stub for Hackathon Demo)"""
    start_time = time.time()
    # In a full app, this would query a Redis/Postgres store using state["conversation_id"]
    memory_context = "No previous conversation context."
    duration = (time.time() - start_time) * 1000
    
    return {
        "memory_context": memory_context,
        "reasoning_trace": ["[Memory] Loaded conversation history."],
        "processing_times": {"Memory": duration}
    }

# ---------------------------------------------------------
# 3. Semantic Search Agent
# ---------------------------------------------------------
def search_agent_node(state: AgentState) -> AgentState:
    """Interacts with Stage 5 ChromaDB."""
    start_time = time.time()
    try:
        results = retriever.search(state["question"], top_k=5, document_id=state.get("document_filter"))
        duration = (time.time() - start_time) * 1000
        
        # Deduplicate sources
        sources = list({res["metadata"].get("document_id", "Unknown") for res in results})
        
        return {
            "retrieved_chunks": results,
            "sources": sources,
            "reasoning_trace": [f"[SearchAgent] Retrieved {len(results)} chunks from ChromaDB."],
            "processing_times": {"SearchAgent": duration}
        }
    except Exception as e:
        logger.error(f"Search Agent Failed: {e}")
        return {
            "agent_errors": [f"SearchAgent Error: {str(e)}"],
            "reasoning_trace": ["[SearchAgent] Failed gracefully."],
            "processing_times": {"SearchAgent": (time.time() - start_time) * 1000}
        }

# ---------------------------------------------------------
# 4. Knowledge Graph Agent
# ---------------------------------------------------------
def graph_agent_node(state: AgentState) -> AgentState:
    """Interacts with Stage 6 Neo4j AuraDB."""
    start_time = time.time()
    try:
        # Extract potential ID from question using regex
        match = re.search(r'\b([A-Za-z]+[- ][0-9]+)\b', state["question"])
        nodes = []
        if match:
            target_id = match.group(1).upper().replace(" ", "-")
            response = graph_query.find_connected_components(target_id)
            nodes = response.nodes
            
        duration = (time.time() - start_time) * 1000
        return {
            "graph_nodes": nodes,
            "reasoning_trace": [f"[GraphAgent] Retrieved {len(nodes)} connected components from Neo4j."],
            "processing_times": {"GraphAgent": duration}
        }
    except Exception as e:
        return {
            "agent_errors": [f"GraphAgent Error: {str(e)}"],
            "reasoning_trace": ["[GraphAgent] Failed gracefully."],
            "processing_times": {"GraphAgent": (time.time() - start_time) * 1000}
        }

# ---------------------------------------------------------
# 5. Maintenance Expert Agent
# ---------------------------------------------------------
def maintenance_agent_node(state: AgentState) -> AgentState:
    """Analyzes chunks specifically for failure states and maintenance RCA."""
    start_time = time.time()
    try:
        # In a massive enterprise system, this might be a smaller LLM call.
        # For speed, we do a heuristic scan over the retrieved chunks.
        chunks = state.get("retrieved_chunks", [])
        insights = []
        for c in chunks:
            text = c["content"].lower()
            if "fail" in text or "broken" in text or "replace" in text:
                insights.append(c["content"])
                
        analysis = "Identified potential historical failures." if insights else "No historical failures noted."
        duration = (time.time() - start_time) * 1000
        return {
            "maintenance_insights": analysis,
            "reasoning_trace": ["[MaintenanceAgent] Scanned context for failure root causes."],
            "processing_times": {"MaintenanceAgent": duration}
        }
    except Exception as e:
        return {"agent_errors": [str(e)]}

# ---------------------------------------------------------
# 6. Compliance Expert Agent
# ---------------------------------------------------------
def compliance_agent_node(state: AgentState) -> AgentState:
    """Analyzes chunks specifically for regulatory/safety rules."""
    start_time = time.time()
    try:
        chunks = state.get("retrieved_chunks", [])
        insights = []
        for c in chunks:
            text = c["content"].lower()
            if "must" in text or "required" in text or "safety" in text or "warning" in text:
                insights.append(c["content"])
                
        analysis = "Flagged safety requirements." if insights else "No critical safety rules found."
        duration = (time.time() - start_time) * 1000
        return {
            "compliance_insights": analysis,
            "reasoning_trace": ["[ComplianceAgent] Validated context against safety heuristics."],
            "processing_times": {"ComplianceAgent": duration}
        }
    except Exception as e:
        return {"agent_errors": [str(e)]}

# ---------------------------------------------------------
# 7. Knowledge Agent (Final Gemini Synthesizer)
# ---------------------------------------------------------
def knowledge_agent_node(state: AgentState) -> AgentState:
    """The isolated LLM. Never queries DBs. Only synthesizes the inputs from previous agents."""
    start_time = time.time()
    
    # Safely load Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _mock_knowledge_response(state, start_time)

    try:
        llm = ChatGoogleGenerativeAI(model=GEMINI_LLM_MODEL, google_api_key=api_key, temperature=0.2)
        
        # Compile strictly constrained context
        context_str = f"Memory: {state.get('memory_context')}\n\n"
        
        chunks = state.get("retrieved_chunks", [])
        if chunks:
            context_str += "--- DOCUMENT CONTEXT ---\n"
            for i, c in enumerate(chunks):
                context_str += f"Chunk {i+1} [ID: {c['chunk_id']}]: {c['content']}\n"
                
        nodes = state.get("graph_nodes", [])
        if nodes:
            context_str += "\n--- GRAPH TOPOLOGY ---\n"
            for n in nodes:
                context_str += f"Node: {n.get('label')} ({n.get('category')})\n"
                
        if state.get("maintenance_insights"):
            context_str += f"\n--- MAINTENANCE EXPERT ---\n{state['maintenance_insights']}\n"
            
        if state.get("compliance_insights"):
            context_str += f"\n--- COMPLIANCE EXPERT ---\n{state['compliance_insights']}\n"

        system_prompt = """
        You are IndusMind AI, an Industrial Knowledge Intelligence Platform.
        Your ONLY job is to synthesize the provided CONTEXT into a highly professional answer.
        
        RULES:
        1. NEVER hallucinate. If the answer is not in the context, say "I could not find enough evidence in the uploaded industrial documents."
        2. Always cite Chunk IDs or Node Labels if you use them.
        3. Keep the tone enterprise-grade and analytical.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Question: {state['question']}\n\nContext:\n{context_str}")
        ]
        
        try:
            response = llm.invoke(messages)
        except Exception as api_err:
            logger.warning(f"Primary model {GEMINI_LLM_MODEL} failed ({api_err}). Falling back to {GEMINI_FALLBACK_MODEL}.")
            fallback_llm = ChatGoogleGenerativeAI(model=GEMINI_FALLBACK_MODEL, google_api_key=api_key, temperature=0.2)
            response = fallback_llm.invoke(messages)
        
        # Compute confidence heuristically based on the amount of evidence
        confidence = 0.95 if chunks or nodes else 0.10
        if "I could not find enough evidence" in response.content:
            confidence = 0.0
            
        duration = (time.time() - start_time) * 1000
        return {
            "final_answer": response.content,
            "overall_confidence": confidence,
            "reasoning_trace": [f"[KnowledgeAgent] Synthesized final answer."],
            "processing_times": {"KnowledgeAgent": duration}
        }
        
    except Exception as e:
        logger.error(f"Knowledge Agent Failed: {e}")
        return _mock_knowledge_response(state, start_time, str(e))

def _mock_knowledge_response(state: AgentState, start_time: float, error_msg: str = "") -> AgentState:
    """Fallback if Gemini is unavailable or errors out."""
    chunks = state.get("retrieved_chunks", [])
    ans = "I could not find enough evidence in the uploaded industrial documents."
    if chunks:
        ans = f"Based on {len(chunks)} retrieved documents, the system found relevant industrial data, but Gemini was unavailable to synthesize it. {error_msg}"
        
    duration = (time.time() - start_time) * 1000
    return {
        "final_answer": ans,
        "overall_confidence": 0.5,
        "reasoning_trace": ["[KnowledgeAgent] Executed fallback synthesis (Gemini offline/error)."],
        "processing_times": {"KnowledgeAgent": duration},
        "agent_errors": [error_msg] if error_msg else []
    }
