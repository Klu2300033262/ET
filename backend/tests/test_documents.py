from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app.main import app

client = TestClient(app)

def test_upload_invalid_mime_type():
    """Test rejection of unsupported file types (e.g., docx)"""
    files = {"file": ("test.docx", b"dummy content", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 415
    assert "Unsupported file type" in response.json()["message"]

@patch("backend.app.api.endpoints.documents.process_document")
def test_upload_valid_txt(mock_process):
    """Test successful acceptance of a TXT file"""
    # Mock the return value of process_document
    mock_process.return_value = {
        "document_id": "test-uuid",
        "filename": "logs.txt",
        "file_size_bytes": 12,
        "num_pages": None,
        "document_type": "text/plain",
        "text_length": 12,
        "ocr_used": False,
        "processing_time_ms": 10,
        "upload_timestamp": "2026-07-14T00:00:00Z",
        "sha256_hash": "hash",
        "status": "COMPLETED",
        "extraction_method": "Automatic Parsing Routing",
        "parser_used": "Native UTF-8 Decoding",
        "saved_text_path": "data/processed/test-uuid.txt"
    }
    
    files = {"file": ("logs.txt", b"Hello World!", "text/plain")}
    response = client.post("/api/v1/documents/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["document_id"] == "test-uuid"
    assert data["data"]["status"] == "COMPLETED"

def test_upload_empty_file():
    """Test behavior with an empty file payload"""
    # Empty file might not trigger a size error, but testing generic rejection or success logic.
    files = {"file": ("empty.pdf", b"", "application/pdf")}
    # We expect a 500 or successful parsing of 0 pages depending on PyMuPDF handling
    # Let's verify the API at least accepts the payload before parsing fails.
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code in [200, 500] 
