# Execution Plan: Graph-Based Retrieval and Cypher Generation

**Objective**: Implement the logic to convert natural language queries into Cypher queries and retrieve data from the Neo4j knowledge graph.

---

### **Phase 1: Scaffolding**

1.  **Update `backend/app/services/graph_service.py`**:
    *   Add a new function signature for `query_graph(query: str) -> List[dict]`.

2.  **Update `tests/services/test_graph_service.py`**:
    *   Add a new test class or test method for `query_graph`.

---

### **Phase 2: Cypher Generation Chain**

1.  **`backend/app/services/graph_service.py`**:
    *   Import `GraphCypherQAChain` from `langchain.chains`.
    *   Import `ChatOpenAI` from `langchain_openai`.
    *   Import `Neo4jGraph` from `langchain_community.graphs`.
    *   In the `query_graph` function:
        1.  Initialize a `Neo4jGraph` instance with the connection details from our existing `neo4j_db` module.
        2.  Initialize a `ChatOpenAI` instance.
        3.  Create a `GraphCypherQAChain` from the graph and the chat model.
        4.  Invoke the chain with the user's query.
        5.  Extract the `result` from the chain's response and return it.

---

### **Phase 3: Refactoring**

1.  **`backend/app/services/retrieval_service.py`**:
    *   Update the `_graph_search` function to call the new `graph_service.query_graph` function.

---

### **Phase 4: Testing**

1.  **`tests/services/test_graph_service.py`**:
    *   Write a unit test for `query_graph`:
        *   Patch `Neo4jGraph` and `ChatOpenAI`.
        *   Mock the `GraphCypherQAChain.from_llm` to return a mock chain.
        *   Mock the `invoke` method of the chain to return a predefined result.
        *   Assert that the function returns the expected result.

---

### **Success Criteria**

*   The `query_graph` function is implemented and integrated.
*   The function can successfully (in a mocked test environment) convert a natural language query into a Cypher query and return a result.
*   All unit tests for the graph service pass.