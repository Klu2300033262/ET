import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_chat_routing_maintenance():
    """Verifies the Rule-Based Router correctly triggers the Maintenance Agent."""
    payload = {
        "question": "What is the maintenance history for the broken pump?",
        "conversation_id": "test-session-1"
    }
    
    response = client.post("/api/v1/chat/", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "MaintenanceAgent" in data["agents_used"]
    assert "SearchAgent" in data["agents_used"]
    # Ensure graph is NOT called if no exact ID or topology trigger was provided
    assert "GraphAgent" not in data["agents_used"]

def test_chat_routing_compliance():
    """Verifies the Rule-Based Router correctly triggers the Compliance Agent."""
    payload = {
        "question": "What are the safety rules for the boiler?",
        "conversation_id": "test-session-2"
    }
    
    response = client.post("/api/v1/chat/", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "ComplianceAgent" in data["agents_used"]
    assert "SearchAgent" in data["agents_used"]

def test_chat_routing_graph():
    """Verifies the Rule-Based Router triggers the Graph Agent on IDs."""
    payload = {
        "question": "What is connected to Valve A-12?",
        "conversation_id": "test-session-3"
    }
    
    response = client.post("/api/v1/chat/", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "GraphAgent" in data["agents_used"]

def test_chat_response_structure():
    """Verifies the rich explainability payload is fully populated."""
    payload = {
        "question": "Show me the manual.",
        "conversation_id": "test-session-4"
    }
    
    response = client.post("/api/v1/chat/", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "answer" in data
    assert "summary" in data
    assert "reasoning_trace" in data
    assert "execution_time_ms" in data
    assert "confidence" in data
    assert type(data["confidence"]) == float
