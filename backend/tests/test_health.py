from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Verify that the health check endpoint returns 200 and the correct structure."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "System is fully operational"
    
    payload = data["data"]
    assert payload["status"] == "healthy"
    assert "version" in payload
    assert "environment" in payload
    assert "service" in payload
