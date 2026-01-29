# Execution Plan: Refactor Retrieval Logic to Use Agentic Router

**Objective**: Refactor the main `hybrid_retrieval` function to use the new agentic router for selecting the retrieval strategy.

---

### **Phase 1: Refactoring**

1.  **Update `backend/app/services/retrieval_service.py`**:
    *   Modify the `hybrid_retrieval` function:
        1.  Remove the existing direct calls to `_vector_search` and `_graph_search`.
        2.  Add a call to the `_route_query` function to get the retrieval plan.
        3.  Add a conditional block (e.g., `if/elif/else`) to check the `tool` returned by the router.
        4.  If the tool is `vector_search`, call `_vector_search`.
        5.  If the tool is `graph_search`, call `_graph_search`.
        6.  Pass the results from the chosen tool to the `_synthesize_answer` function.
        7.  Update the return dictionary to reflect the new single-source retrieval.

---

### **Phase 2: Testing**

1.  **Update `tests/services/test_retrieval_service.py`**:
    *   Modify the `test_hybrid_retrieval` test case:
        1.  Add a patch for the `_route_query` function.
        2.  Create two test scenarios:
            *   One where `_route_query` returns `{'tool': 'vector_search', ...}`. Assert that `_vector_search` is called and `_graph_search` is not.
            *   One where `_route_query` returns `{'tool': 'graph_search', ...}`. Assert that `_graph_search` is called and `_vector_search` is not.

---

### **Success Criteria**

*   The `hybrid_retrieval` function is successfully refactored to use the agentic router.
*   The end-to-end retrieval process is functional, with the router correctly dispatching to the appropriate retrieval function.
*   All unit tests for the retrieval service, including the updated tests for `hybrid_retrieval`, pass.