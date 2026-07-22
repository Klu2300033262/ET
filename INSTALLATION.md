# Setup & Installation Guide

This document describes how to set up the local environment and launch the backend and frontend modules of IndusMind AI.

---

## 💻 1. Prerequisites
- **Python**: v3.10+
- **NodeJS**: v18+
- **Docker**: Active daemon for starting Neo4j

---

## 🐍 2. Backend Setup
1. **Initialize Virtual Env**:
   ```bash
   cd backend
   python -m venv .venv
   .venv\Scripts\activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_sm
   ```
3. **Configure Settings**:
   Create a `.env` file in the project root:
   ```env
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=password
   GEMINI_API_KEY=YOUR_GEMINI_API_KEY
   GEMINI_LLM_MODEL=gemini-pro-latest
   GEMINI_FALLBACK_MODEL=gemini-flash-latest
   ```

---

## 🐳 3. Database Services
Launch the local Neo4j Docker container:
```bash
docker run -d --name indusmind-neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.21.0-community
```

---

## ⚡ 4. Start Servers

### Start FastAPI Backend
```bash
cd backend
.venv\Scripts\uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Start React Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5174/` to use the platform dashboard.
