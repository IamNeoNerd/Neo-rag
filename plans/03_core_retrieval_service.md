# Execution Plan: Core Retrieval Service

**Objective**: Implement the core data retrieval pipeline, including hybrid search (vector + graph) and answer synthesis.

---

### **Phase 1: Service Scaffolding**

1.  **Create Files**:
    *   `backend/app/services/retrieval_service.py`
    *   `tests/services/test_retrieval_service.py`

---

### **Phase 2: Retrieval Logic**

1.  **`backend/app/services/retrieval_service.py`**:
    *   Import necessary modules: `embedding_service`, `neon_db`, `neo4j_db`, and LLM clients from `langchain`.
    *   Implement `_vector_search(query: str, top_k: int) -> List[dict]`:
        1.  Generates an embedding for the user's query.
        2.  Connects to the Neon database.
        3.  Performs a similarity search on the `documents` table.
        4.  Returns the top `k` matching documents.
    *   Implement `_graph_search(query: str) -> List[dict]`:
        *   (Placeholder) This function will contain a placeholder for the future Neo4j graph search logic. It should return an empty list for now.
    *   Implement `_synthesize_answer(query: str, context: List[dict]) -> str`:
        1.  Initializes a chat model (e.g., `ChatOpenAI`).
        2.  Creates a prompt template that instructs the model to answer the user's query based on the provided context.
        3.  Invokes the model with the formatted prompt and returns the synthesized answer.
    *   Implement `hybrid_retrieval(query: str, top_k: int = 5) -> dict`:
        1.  **Pass 1**:
            *   Calls `_vector_search` to get initial documents.
            *   Calls `_graph_search` to get initial graph results.
            *   Merges the results into a combined context.
        2.  **Pass 2**:
            *   (Placeholder) For now, this pass will simply use the context from Pass 1.
        3.  **Synthesis**:
            *   Calls `_synthesize_answer` with the final context to generate the answer.
        4.  Returns a dictionary containing the vector results, graph results, and the synthesized answer.

---

### **Phase 3: API Integration**

1.  **`backend/app/main.py`**:
    *   Import `retrieval_service` and the `RetrievalRequest`, `RetrievalResponse` models.
    *   Create a new endpoint `POST /retrieve`:
        *   Accepts a `RetrievalRequest` body.
        *   Calls `retrieval_service.hybrid_retrieval` with the provided query.
        *   Returns a `RetrievalResponse` with the results.

---

### **Phase 4: Testing**

1.  **`tests/services/test_retrieval_service.py`**:
    *   Write unit tests for `_vector_search`:
        *   Mock the `embedding_service` and the Neon database connection.
        *   Verify that the correct similarity search query is executed.
    *   Write unit tests for `_synthesize_answer`:
        *   Mock the chat model to return a predefined answer.
        *   Verify that the prompt is formatted correctly.
    *   Write unit tests for `hybrid_retrieval`:
        *   Mock all underlying functions (`_vector_search`, `_graph_search`, `_synthesize_answer`).
        *   Verify that the two-pass orchestration logic is executed correctly.

---

### **Success Criteria**

*   The new service and test files are created.
*   The `POST /retrieve` endpoint is available and functional.
*   Sending a query to the `/retrieve` endpoint successfully performs a vector search, synthesizes an answer, and returns the results.
*   All unit tests for the retrieval service pass.