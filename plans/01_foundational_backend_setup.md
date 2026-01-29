# Execution Plan: Foundational Backend Setup

**Objective**: Create the initial structure for the FastAPI backend, establish database connections, and define core data models.

---

### **Phase 1: Project Structure**

1.  **Create Directories**:
    *   `backend/app/`
    *   `backend/app/database/`
    *   `backend/app/models/`
    *   `backend/app/services/`
    *   `tests/`
    *   `tests/database/`

2.  **Create Initial Files**:
    *   `backend/app/main.py`
    *   `backend/app/database/neon_db.py`
    *   `backend/app/database/neo4j_db.py`
    *   `backend/app/models/data_models.py`
    *   `requirements.txt`
    *   `.env.example`
    *   `tests/database/test_connections.py`

---

### **Phase 2: Dependency Management**

1.  **Populate `requirements.txt`**:
    ```
    fastapi
    uvicorn[standard]
    python-dotenv
    psycopg2-binary
    pgvector
    neo4j
    pydantic
    openai
    anthropic
    cohere
    ```

2.  **Populate `.env.example`**:
    ```
    # LLM Providers
    OPENAI_API_KEY=
    ANTHROPIC_API_KEY=
    COHERE_API_KEY=

    # Databases
    NEON_DATABASE_URL=
    NEO4J_URI=
    NEO4J_USERNAME=
    NEO4J_PASSWORD=
    ```

---

### **Phase 3: Core Implementation**

1.  **`backend/app/models/data_models.py`**:
    *   Define Pydantic models for `Document`, `GraphEntity`, `GraphRelationship`, `IngestDataRequest`, `RetrievalRequest`, and `RetrievalResponse`.

2.  **`backend/app/database/neon_db.py`**:
    *   Implement a function to connect to the Neon PostgreSQL database using credentials from environment variables.
    *   Implement a function to create the `documents` table if it doesn't exist (`id`, `content`, `embedding`, `metadata`).

3.  **`backend/app/database/neo4j_db.py`**:
    *   Implement a function to connect to the Neo4j AuraDB using credentials from environment variables.
    *   Implement a basic connection verification function.

4.  **`backend/app/main.py`**:
    *   Initialize the FastAPI application.
    *   Import and call the database connection functions upon startup.
    *   Create a root endpoint (`/`) that returns a welcome message.
    *   Create a `/health` endpoint that verifies database connections and returns a status.

---

### **Phase 4: Testing**

1.  **`tests/database/test_connections.py`**:
    *   Write Pytest unit tests for the connection logic in `neon_db.py` and `neo4j_db.py`.
    *   Use `unittest.mock` to patch the actual database driver connections and assert that they are called with the correct parameters.

---

### **Success Criteria**

*   The project structure matches the plan.
*   `pip install -r requirements.txt` runs without errors.
*   The FastAPI application starts with `uvicorn backend.app.main:app --reload`.
*   The `/health` endpoint returns a successful response indicating that database connections are active.
*   All unit tests pass.