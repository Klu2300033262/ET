import os
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.vector_store import vector_store

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_embedding_model():
    """Mocks the sentence-transformer to avoid heavy downloads during tests."""
    with patch("backend.app.services.embedding_service.EmbeddingService.generate_embeddings_batch") as mock_batch:
        # bge-small outputs 384-dimensional vectors
        mock_batch.return_value = [[0.1] * 384, [0.2] * 384]
        
        with patch("backend.app.services.embedding_service.EmbeddingService.generate_embedding") as mock_single:
            mock_single.return_value = [0.15] * 384
            yield

@pytest.fixture
def mock_chunks_data(tmp_path):
    """Generates mock Stage 4 output."""
    doc_id = "test-embed-123"
    chunk_dir = os.path.join("data", "processed", "chunks", doc_id)
    os.makedirs(chunk_dir, exist_ok=True)
    
    chunks_json_path = os.path.join(chunk_dir, "chunks.json")
    
    payload = {
        "document_metadata": {
            "document_id": doc_id,
            "filename": "engine.pdf"
        },
        "chunks": [
            {
                "chunk_id": f"{doc_id}-chunk-1",
                "chunk_number": 1,
                "start_offset": 0,
                "content": "The engine operates at high temperatures."
            },
            {
                "chunk_id": f"{doc_id}-chunk-2",
                "chunk_number": 2,
                "start_offset": 50,
                "content": "Valve A12 must be checked weekly."
            }
        ]
    }
    
    with open(chunks_json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f)
        
    yield doc_id
    
    # Cleanup vector store and files
    vector_store.collection.delete(where={"document_id": doc_id})
    import shutil
    shutil.rmtree(chunk_dir)

def test_embed_document(mock_chunks_data):
    """Tests the embedding ingestion endpoint and the Chroma caching."""
    doc_id = mock_chunks_data
    
    # First ingestion (should succeed)
    response = client.post(f"/api/v1/documents/{doc_id}/embed")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["status"] == "EMBEDDED"
    
    # Second ingestion (should hit cache)
    response2 = client.post(f"/api/v1/documents/{doc_id}/embed")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["data"]["status"] == "CACHED"

def test_semantic_search(mock_chunks_data):
    """Tests the semantic retrieval endpoint."""
    doc_id = mock_chunks_data
    
    # Ingest first
    client.post(f"/api/v1/documents/{doc_id}/embed")
    
    # Search
    search_payload = {
        "query": "temperature engine",
        "top_k": 2
    }
    
    response = client.post("/api/v1/search", json=search_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # The mocks return dummy vectors, so similarities will just be random mathematically,
    # but the API contract (returning chunks, scores, metadata) should hold.
    results = data["data"]["results"]
    assert isinstance(results, list)
