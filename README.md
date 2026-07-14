# IndusMindAI – Industrial Knowledge Intelligence Platform

An AI-powered Industrial Knowledge Intelligence Platform designed to ingest heterogeneous industrial documents, extract knowledge, build an industrial knowledge graph, enable intelligent RAG, and orchestrate multiple specialized AI agents for maintenance, compliance, and systems integration.

## Project Overview

IndusMindAI serves as a single source of truth for complex industrial documentation, allowing engineers and operators to seamlessly query, troubleshoot, and interact with machine manuals, SOPs, and inspection reports through intuitive AI conversation.

## Architecture

The project utilizes a modern multi-agent RAG (Retrieval-Augmented Generation) microservices architecture:
- **Backend Infrastructure**: Built on **FastAPI** to serve robust, typed endpoints.
- **Frontend Interface**: A dynamic **React** dashboard.
- **Knowledge Base**: **ChromaDB** for vector semantic search, and **Neo4j** for relational knowledge graph representations of equipment hierarchies.
- **Agent Orchestration**: **LangGraph** coordinates a `SupervisorAgent` that routes tasks to `KnowledgeAgent`, `MaintenanceAgent`, and `ComplianceAgent`.

## Technologies

- **Python 3.12** / FastAPI / Pydantic
- **React** (Frontend Framework)
- **LangChain** / **LangGraph** (AI Orchestration)
- **ChromaDB** (Vector Database)
- **Neo4j** (Graph Database)
- **Google Gemini 2.5 Flash** (Reasoning Engine)
- **SentenceTransformers** (Local Embeddings)

## Setup & Execution

### 1. Backend Startup

To initialize the virtual environment and start the API:

```powershell
# Activate Environment
cd backend
..\.venv\Scripts\Activate.ps1

# Run API Server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Available Routes
- **Interactive API Docs (Swagger)**: `http://127.0.0.1:8000/docs`
- **System Health Check**: `http://127.0.0.1:8000/api/v1/health`

### 3. Frontend (Coming in Future Stages)
*Frontend setup will be detailed as the React environment is developed.*
