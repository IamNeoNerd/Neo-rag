# Execution Plan: Enhance the Agentic Router with a Code Analysis Tool

**Objective**: Create a new tool that can analyze the codebase and integrate it into our agentic router.

---

### **Phase 1: Code Analysis Tool**

1.  **Create a New Service**:
    *   Create `backend/app/services/code_analysis_service.py`.
    *   This service will contain the logic for analyzing the codebase.

2.  **Implement Code Analysis Function**:
    *   In `code_analysis_service.py`, create a function `analyze_code(query: str) -> str`.
    *   This function will take a natural language query about the code.
    *   It will use a combination of file system operations (`os.walk`) and an LLM to find relevant code snippets and generate a summary.
    *   (Initial Implementation) To start, this function can simply retrieve the full content of a file specified in the query (e.g., "analyze `retrieval_service.py`").

---

### **Phase 2: Tool Integration**

1.  **Update `backend/app/services/retrieval_service.py`**:
    *   Import the new `code_analysis_service`.
    *   Create a new tool, `code_analysis_tool`, with a clear description of its purpose (e.g., "Use this tool for questions about the codebase, such as how a specific function works or what a file contains.").
    *   Add this new tool to the list of tools available to the agentic router.

---

### **Phase 3: Testing**

1.  **Create a New Test File**:
    *   Create `tests/services/test_code_analysis_service.py`.

2.  **Write Unit Tests**:
    *   Write a unit test for `analyze_code`:
        *   Mock the file system operations to return predefined code content.
        *   Mock the LLM call to simulate the code summarization.
        *   Assert that the function returns the expected analysis.
    *   Update the tests for `_route_query` in `tests/services/test_retrieval_service.py` to include a test case where the router correctly chooses the `code_analysis_tool`.

---

### **Success Criteria**

*   The `code_analysis_service.py` and its corresponding test file are created.
*   The agentic router in `retrieval_service.py` is updated with the new tool.
*   The router can successfully delegate code-related queries to the `code_analysis_tool`.
*   All unit tests, including the new tests for the code analysis service, pass.