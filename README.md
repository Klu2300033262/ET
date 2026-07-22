# IndusMind AI - Industrial Knowledge Intelligence Platform

IndusMind AI is an enterprise-grade, multi-agent RAG (Retrieval-Augmented Generation) and Knowledge Graph platform designed to ingest complex industrial manuals, extract entities, track their processing lifecycle, and provide explainable AI reasoning about maintenance, safety, and compliance.

---

## 🚀 Technology Stack
- **Frontend**: React (Vite), React Flow, TailwindCSS, React Query (@tanstack/react-query), Recharts.
- **Backend**: FastAPI (Python), LangGraph, LangChain, spaCy.
- **Databases**: ChromaDB (Vector DB), Neo4j Community Edition (Graph DB).
- **LLM Engine**: Google Gemini API (`gemini-1.5-pro` with dynamic fallback).

---

## 📂 Folder Structure
```text
c:/ET/
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints (chat, search, status, metrics, documents)
│   │   ├── config/       # Settings, environment, and constants
│   │   ├── models/       # Pydantic schemas (AgentState, ChatRequest, GraphEntity)
│   │   ├── services/     # OCR, VectorStore, Neo4j, LangGraph Orchestration
│   │   └── main.py       # FastAPI Entrypoint
│   └── tests/            # Automated PyTest suites
├── frontend/
│   ├── src/
│   │   ├── components/   # Shared UI elements
│   │   ├── layouts/      # Main Dashboard layout
│   │   ├── pages/        # Dashboard, AI Assistant, Graph, DocumentDetails, Analytics
│   │   └── services/     # api.js Centralized HTTP Client
│   ├── package.json
│   └── vite.config.js
└── data/                 # Raw PDFs and processed metadata, text, and chunks
```

---

## 🛠 Installation & Setup

### 1. Prerequisites
- **Python**: v3.10+
- **NodeJS**: v18+
- **Docker**: For running Neo4j container.

### 2. Backend Installation
```bash
# Navigate to backend and setup Virtual Environment
cd backend
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Frontend Installation
```bash
cd ../frontend
npm install
```

### 4. Database Setup (Docker)
Ensure your Docker engine is active. Start the community Neo4j instance:
```bash
docker run -d --name indusmind-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.21.0-community
```

---

## ⚙ Environment Variables (`.env`)
Create a `.env` file in the root workspace:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_LLM_MODEL=gemini-1.5-pro
```

---

## 🏃 Running the Application

### 1. Start FastAPI Backend
```bash
cd backend
.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be interactive at: `http://127.0.0.1:8000/docs`

### 2. Start Frontend Dev Server
```bash
cd frontend
npm run dev
```
Open your browser at: `http://localhost:5174/`

---

## 🔍 Key Features & Capabilities
1. **Explainable Agent Provance**: Every AI query lists confidence scores, execution times, LangGraph traces, and inline citations.
2. **Dynamic Ingestion Routing**: Differentiates native PDFs from scanned documents, automatically triggering Tesseract OCR where required.
3. **Visual Network Topologies**: Explores graph relationships using a zoomable, searchable React Flow map.
4. **Subsystem Analytics**: Visualizes vector chunks, ingestion metrics, and API request history in dynamic charts.
