import os
import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

@pytest.fixture
def mock_graph_data(tmp_path):
    """Generates mock Stage 4 output containing industrial heuristics."""
    doc_id = "test-graph-123"
    chunk_dir = os.path.join("data", "processed", "chunks", doc_id)
    os.makedirs(chunk_dir, exist_ok=True)
    
    chunks_json_path = os.path.join(chunk_dir, "chunks.json")
    
    # We include spaCy friendly text (names/orgs) and Industrial Regex (Valve A-12)
    payload = {
        "document_metadata": {
            "document_id": doc_id,
            "filename": "manual.pdf"
        },
        "chunks": [
            {
                "chunk_id": f"{doc_id}-chunk-1",
                "chunk_number": 1,
                "start_offset": 0,
                "content": "The Pump P-101 is located in the Engineering Sector. John Doe reported that the compressor failed due to overheat."
            }
        ]
    }
    
    with open(chunks_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
        
    yield doc_id
    
    # Cleanup
    import shutil
    shutil.rmtree(chunk_dir)

def test_graph_extraction_pipeline(mock_graph_data):
    """Verifies the multi-tier extractor and relationship inference without needing Neo4j online."""
    doc_id = mock_graph_data
    
    response = client.post(f"/api/v1/graph/build/{doc_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    
    # We expect multiple entities:
    # "P-101" (Regex)
    # "Pump" (Keyword)
    # "Engineering" (spaCy / Keyword)
    # "John Doe" (spaCy PERSON)
    # "Compressor" (Keyword)
    # "overheat" (Keyword/Fault)
    
    # The exact number depends on spaCy vs Regex overlaps, but it should definitely find entities
    assert data["data"]["entities_found"] >= 3
    
    # We expect relationships based on proximity:
    # P-101 LOCATED_IN Engineering
    # Compressor HAS_FAILURE overheat
    assert data["data"]["relationships_found"] >= 1

def test_graph_statistics():
    """Tests the graceful degradation of the statistics endpoint if DB is offline."""
    response = client.get("/api/v1/graph/statistics")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data["data"]
    assert "relationships" in data["data"]

def test_missing_document_graph_build():
    """Tests 404 handling."""
    response = client.post("/api/v1/graph/build/missing-doc-999")
    assert response.status_code == 404
