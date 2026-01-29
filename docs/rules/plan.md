# Project Plan: Hybrid RAG Application

## Phase 1: Backend Setup and Core Data Ingestion (Completed)
- **Goal**: Establish the foundational backend infrastructure and enable basic data ingestion into vector and graph stores.
- **Steps**:
    1.  **Environment Setup**:
        -   Create `requirements.txt` with necessary Python libraries (FastAPI, Uvicorn, python-dotenv, langchain, neo4j, psycopg2-binary, pgvector, openai, anthropic, cohere).
        -   Install dependencies using `pip install -r requirements.txt`.
    2.  **Backend Application Structure**:
        -   Create `backend/app/` directory.
        -   Initialize FastAPI application in `backend/app/main.py`.
        -   Create `.env.example` for environment variables (API keys, DB URIs).
    3.  **Database Connection Logic**:
        -   Create `backend/app/database/` directory.
        -   Implement `neon_db.py` for PostgreSQL (Neon) connection and `documents` table creation.
        -   Implement `neo4j_db.py` for Neo4j (AuraDB) connection and basic node/relationship creation.
    4.  **Data Models**:
        -   Create `backend/app/models/` directory.
        -   Define Pydantic models in `data_models.py` for `Document`, `GraphEntity`, `GraphRelationship`, `IngestDataRequest`, `RetrievalRequest`, `RetrievalResponse`.
    5.  **Core Services**:
        -   Create `backend/app/services/` directory.
        -   Implement `embedding_service.py` for generating embeddings using OpenAI/Cohere.
        -   Implement `ingestion_service.py` for text chunking, embedding, and storing data in Neon and Neo4j. (Includes placeholder for entity/relationship extraction).
    6.  **File Organization Adherence**:
        -   Move all existing `.md` files to `docs/`.
        -   Create `frontend/` directory.
        -   Update `.clinerules/project_rules.md` to reflect the current project structure and guidelines.

## Phase 2: Retrieval Agent Implementation (Current Focus)
- **Goal**: Develop the hybrid retrieval mechanism, combining vector and graph search results to provide comprehensive answers.
- **Steps**:
    1.  **Retrieval Service Development**:
        -   Create `backend/app/services/retrieval_service.py`.
        -   Implement `_vector_search` for querying Neon.
        -   Implement `_graph_search` for querying Neo4j (placeholder for Cypher generation).
        -   Implement `_synthesize_answer` using LLMs (OpenAI, Anthropic, Cohere) to generate final answers from combined context.
        -   Implement `hybrid_retrieval` with a two-pass approach as described in `AGENT_WORKFLOWS.md`.
    2.  **API Integration**:
        -   Add `/ingest` and `/retrieve` endpoints to `backend/app/main.py` to expose ingestion and retrieval functionalities.
    3.  **Testing**:
        -   Add unit tests for `retrieval_service.py` (mocking DB and LLM calls).
        -   Ensure test coverage >80% for core retrieval logic.

## Phase 3: Frontend Development
- **Goal**: Build a mobile-first client application for user interaction, data ingestion, and retrieval display.
- **Steps**:
    1.  **Framework Selection**: Choose between React Native or Flutter.
    2.  **UI/UX Design**: Implement user interface for:
        -   API key/DB connection configuration.
        -   Document upload/text ingestion.
        -   Query input and retrieval results display.
        -   Side panel for Pass 1 & 2 breakdown.
    3.  **Backend Integration**: Connect frontend to backend API endpoints (`/config`, `/ingest`, `/retrieve`).
    4.  **Mobile-First Principles**: Ensure responsive design and optimal performance on mobile devices.

## Phase 4: Advanced Features & Refinements
- **Goal**: Enhance the application with advanced functionalities and improve robustness.
- **Steps**:
    1.  **Dynamic Schema Management**: Implement real-time schema editing for AuraDB.
    2.  **LLM Prompt Customization**: Allow users to tweak retrieval prompts via the UI.
    3.  **Confidence-Based Retrieval**: Implement logic to skip Pass 2 if Pass 1 results are highly confident.
    4.  **Custom Weighting**: Allow users to adjust weighting between vector and graph results.
    5.  **Error Handling & Logging**: Enhance comprehensive error handling and logging across the application.
    6.  **Deployment**: Prepare backend and frontend for deployment.

## Documentation Updates
- Continuously update all relevant documentation files in `docs/` throughout the development process.
- Generate OpenAPI/Swagger documentation for all backend endpoints.
