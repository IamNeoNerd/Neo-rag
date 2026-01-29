# Execution Plan: Neo4j Integration and Graph Service

**Objective**: Integrate the Neo4j database and create a dedicated service to manage graph-based operations.

---

### **Phase 1: Dependency Management**

1.  **Update `requirements.txt`**:
    *   Add `langchain-community`.

---

### **Phase 2: Service Scaffolding**

1.  **Create Files**:
    *   `backend/app/services/graph_service.py`
    *   `tests/services/test_graph_service.py`

---

### **Phase 3: Graph Service Implementation**

1.  **`backend/app/services/graph_service.py`**:
    *   Import `GraphDatabase` from `neo4j` and `os`, `load_dotenv`.
    *   Implement `get_neo4j_driver()`:
        *   This function will be responsible for creating and returning a Neo4j driver instance.
        *   It should read the connection details (`URI`, `USERNAME`, `PASSWORD`) from environment variables.
        *   Include error handling for missing credentials or connection failures.
    *   (Self-correction) We will reuse the existing `neo4j_db.py` for the driver connection and import it into the `graph_service.py` to avoid code duplication.

---

### **Phase 4: Refactoring**

1.  **`backend/app/services/retrieval_service.py`**:
    *   Update the `_graph_search` function to import and use the new `graph_service.py` (though it will still be a placeholder).

---

### **Phase 5: Testing**

1.  **`tests/services/test_graph_service.py`**:
    *   Write a unit test for the `get_neo4j_driver` function.
    *   Use `unittest.mock` to patch the `GraphDatabase.driver` and verify that it is called with the correct credentials.

---

### **Success Criteria**

*   The new dependency is added and installed.
*   The `graph_service.py` and its corresponding test file are created.
*   The graph service can successfully establish a connection to the Neo4j database (verified through tests).
*   All unit tests for the graph service pass.