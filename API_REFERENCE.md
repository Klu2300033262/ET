# API Reference Documentation

IndusMind AI exposes a set of REST endpoints grouped under `/api/v1`.

---

## 💬 1. AI Assistant & Chat API
* **Endpoint**: `POST /api/v1/chat/`
* **Request Payload**:
  ```json
  {
    "question": "What is the recommended maintenance procedure for Pump P-101?",
    "session_id": "optional-uuid-here"
  }
  ```
* **Response Payload**:
  ```json
  {
    "answer": "...",
    "confidence": 0.95,
    "sources": ["doc-uuid"],
    "chunks_used": [...],
    "nodes_used": [...],
    "execution_time_ms": 1250,
    "reasoning_trace": [...]
  }
  ```

---

## 🔍 2. Semantic Search API
* **Endpoint**: `POST /api/v1/search`
* **Request Payload**:
  ```json
  {
    "query": "safety valve",
    "top_k": 5,
    "threshold": 0.3
  }
  ```
* **Response Payload**:
  ```json
  {
    "success": true,
    "data": {
      "results": [
        {
          "chunk_id": "...",
          "content": "...",
          "similarity_score": 0.85,
          "metadata": {...}
        }
      ]
    }
  }
  ```

---

## 🗂 3. Document Lifecycle APIs
* **Upload**: `POST /api/v1/documents/upload`
* **List**: `GET /api/v1/documents/`
* **Details**: `GET /api/v1/documents/{document_id}`
* **Download Raw**: `GET /api/v1/documents/{document_id}/download`
* **Get Extracted Text**: `GET /api/v1/documents/{document_id}/text`
* **Delete**: `DELETE /api/v1/documents/{document_id}`

---

## 📊 4. System Telemetry APIs
* **Health Check**: `GET /api/v1/health` (Reports Neo4j, Gemini, Chroma status)
* **Metrics**: `GET /api/v1/system/metrics` (Node/edge counts, upload count)
* **Routes**: `GET /api/v1/system/routes`
* **Logs**: `GET /api/v1/system/logs`
