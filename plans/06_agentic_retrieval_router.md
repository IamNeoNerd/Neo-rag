# Execution Plan: Agentic Retrieval Router

**Objective**: Implement an intelligent router that analyzes user queries and selects the optimal retrieval strategy (vector, graph, or hybrid).

---

### **Phase 1: Scaffolding**

1.  **Update `backend/app/services/retrieval_service.py`**:
    *   Add a new function signature for `_route_query(query: str) -> dict`.

2.  **Update `tests/services/test_retrieval_service.py`**:
    *   Add a new test class or test method for `_route_query`.

---

### **Phase 2: Router Implementation**

1.  **`backend/app/services/retrieval_service.py`**:
    *   Import necessary modules from `langchain` for creating tools and agents.
    *   In the `_route_query` function:
        1.  Define two tools: `vector_search` and `graph_search`. Each tool should have a clear description of when it should be used.
        2.  Initialize a `ChatOpenAI` model that supports function-calling/tool-use.
        3.  Create a prompt template that instructs the model to act as a router and choose the best tool for the user's query.
        4.  Create an agent or chain that binds the tools and the prompt to the model.
        5.  Invoke the agent with the user's query.
        6.  Process the agent's output to extract the chosen tool and the corresponding query, returning it as a dictionary.

---

### **Phase 3: Testing**

1.  **`tests/services/test_retrieval_service.py`**:
    *   Write unit tests for `_route_query`:
        *   Mock the `ChatOpenAI` model and the tool-calling agent.
        *   Create several test cases with different types of queries (e.g., a question about relationships, a request for a summary).
        *   For each test case, assert that the router correctly chooses the appropriate tool (`vector_search` or `graph_search`).

---

### **Success Criteria**

*   The `_route_query` function is implemented and integrated.
*   The function can successfully (in a mocked test environment) route different types of queries to the correct retrieval tool.
*   All unit tests for the agentic router pass.