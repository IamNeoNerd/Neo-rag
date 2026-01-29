# Project Instructions

## Overview
This is a **mobile-first**, **client-heavy** AI retrieval application with optional data push.  
Core tech:
- **Frontend**: Web/Mobile hybrid (React Native or Flutter)
- **Backend**: Minimal — used for authentication & credential storage only
- **Databases**:
  - Vector Store: **Neon** (Postgres + pgvector)
  - Graph Store: **Neo4j AuraDB**
- **LLM Providers**: User-configurable (OpenAI, Anthropic, etc.), with API key/base URL setup in UI.

## High-Level Goals
- Enable **non-coders** to connect models & databases via a simple backend UI.
- Provide **hybrid retrieval** (vector + graph).
- Allow users to **tweak model behavior** by editing the retrieval prompts.
- Store **API credentials securely** with backend verification.

## Coding Style
- **Indentation**: 2 spaces for JS/TS, 4 spaces for Python.
- **Naming**: snake_case for Python, camelCase for JS/TS.
- **Components**: Functional components only (React).
- **Error Handling**: Explicit error boundaries and status codes.

## Testing
- Unit test each agent logic path.
- Mock DB calls in tests.
- Ensure test coverage >80% for core retrieval logic.

## Documentation Standards
- All functions: docstrings with params, returns, example usage.
- All endpoints: OpenAPI/Swagger doc generation.
- Workflow diagrams updated in `/docs`.

## Context Files
- See `AGENT_WORKFLOWS.md` for orchestration logic.
- See `SCHEMA_GUIDELINES.md` for data ingestion rules.
- See `CREDENTIALS_SECURITY.md` for API key handling rules.