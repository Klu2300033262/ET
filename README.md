# IndusMindAI – Industrial Knowledge Intelligence Platform

IndusMindAI is a professional Industrial Knowledge Intelligence Platform designed to ingest heterogeneous industrial documents (SOPs, manuals, blueprints, scanned records), extract multi-entity relationships, build an actionable Knowledge Graph via Neo4j, and facilitate semantic Search & Reasoning using hybrid GraphRAG. It incorporates specialized LangGraph agents for maintenance planning and regulatory compliance.

## High-Level System Architecture

Refer to [implementation_plan.md](file:///C:/Users/valli/.gemini/antigravity-ide/brain/a9dd4b41-03cb-426c-8457-bf5a43142fc7/implementation_plan.md) for full flowcharts and architectural module layouts.

1. **Multimodal Document Ingestion Pipeline**: Ingests files (PDFs, images) and parses layout hierarchies.
2. **Knowledge Extraction & Graph Creation**: LLM-guided schema extraction storing entities and relationships into Neo4j Graph DB alongside dense embeddings.
3. **Multi-Agent Orchestrator**: LangGraph-based routing for hybrid GraphRAG querying, maintenance plans, and compliance audits.
4. **Interactive Dashboard**: Modern glassmorphic React UI with Cytoscape-powered relationship navigation.

## Repository Setup & Directory Structure

```
C:\ET\
├── backend/            # FastAPI Backend application
└── frontend/           # React + Vite + TypeScript application
```

## Quick Start Setup

### Prerequisites
* Python 3.12
* Node.js v18+
* Neo4j instance running (Local or Aura DB)

### Environment Configuration
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Populate the required keys in `.env` (Gemini API key, Neo4j connection parameters).

### Backend Virtual Environment Setup
1. Create Python virtual environment:
   ```bash
   python -m venv .venv
   ```
2. Activate Virtual Environment:
   * **Windows PowerShell**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   * **Windows Command Prompt / Git Bash**:
     ```bash
     source .venv/Scripts/activate
     ```
3. Install Python dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### Frontend Dependencies Setup
Install node modules:
```bash
npm install
```

---

## Executing Applications

### Running FastAPI Backend
From the root workspace, with the virtual environment activated, run:
```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

### Running Vite React Frontend
From the root workspace:
```bash
npm run dev
```

---

## Verification
Execute the verification sanity check scripts:
```bash
python verify_backend.py
```
This tests core dependency imports and credentials loading.
