---
description: Start the development servers for backend and frontend
---

# Dev Server Workflow

This workflow starts both the backend (FastAPI) and frontend (React) development servers.

## Prerequisites
- Python environment with `requirements.txt` installed
- Node.js with frontend dependencies installed (`npm install` in `frontend/`)
- `.env` file configured with required credentials

## Steps

### 1. Start Backend Server
// turbo
```bash
cd d:\P-Projects\Neo-rag
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend will be available at `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

### 2. Start Frontend Server (in separate terminal)
// turbo
```bash
cd d:\P-Projects\Neo-rag\frontend
npm start
```

The frontend will be available at `http://localhost:3000`

## Verification
1. Check backend health: `curl http://127.0.0.1:8000/health`
2. Verify frontend loads in browser at `http://localhost:3000`
