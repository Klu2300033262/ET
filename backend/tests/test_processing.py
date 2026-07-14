import os
import json
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

@pytest.fixture
def mock_document_data(tmp_path):
    """Generates mock text and metadata files representing Stage 3 output."""
    doc_id = "test-doc-123"
    
    # Mock OS paths by overriding the service paths
    # For a robust test, we temporarily set the CWD or patch the paths.
    # In this simple test, we will actually just write directly to the real data folder.
    # A robust CI/CD pipeline would mock the constants.
    
    os.makedirs("data/processed/text", exist_ok=True)
    os.makedirs("data/processed/metadata", exist_ok=True)
    
    text_path = os.path.join("data", "processed", "text", f"{doc_id}.txt")
    metadata_path = os.path.join("data", "processed", "metadata", f"{doc_id}.json")
    
    mock_text = "This is a test document.\n\n" * 100  # Will be > 1000 chars, forcing chunks
    mock_text += "Equipment ID: Valve_A12\n"
    
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(mock_text)
        
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump({
            "document_id": doc_id,
            "filename": "test.pdf",
            "source_document": "test.pdf"
        }, f)
        
    yield doc_id
    
    # Cleanup
    if os.path.exists(text_path): os.remove(text_path)
    if os.path.exists(metadata_path): os.remove(metadata_path)

def test_process_document_success(mock_document_data):
    """Tests the full chunking and cleaning pipeline."""
    doc_id = mock_document_data
    
    response = client.post(f"/api/v1/documents/{doc_id}/process")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "statistics" in data["data"]
    assert data["data"]["statistics"]["Total Chunks"] > 1
    
    # Verify outputs exist
    chunk_json_path = os.path.join("data", "processed", "chunks", doc_id, "chunks.json")
    assert os.path.exists(chunk_json_path)
    
    with open(chunk_json_path, "r", encoding="utf-8") as f:
        payload = json.load(f)
        assert "document_metadata" in payload
        assert "Total Words" in payload["document_metadata"] # NLP stats check
        assert len(payload["chunks"]) == data["data"]["statistics"]["Total Chunks"]
        
    # Cleanup chunk dir
    import shutil
    shutil.rmtree(os.path.join("data", "processed", "chunks", doc_id))

def test_process_document_not_found():
    """Tests 404 behavior for unknown documents."""
    response = client.post("/api/v1/documents/missing-doc-999/process")
    assert response.status_code == 404
