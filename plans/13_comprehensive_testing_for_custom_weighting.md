# Plan: Comprehensive Testing for Custom Weighting

**Epic:** Hybrid Retrieval
**Feature:** Add comprehensive unit and integration tests for the custom weighting (`alpha` parameter) feature.

## 1. Goal

The goal is to ensure the custom weighting feature is robust, reliable, and handles both valid and invalid inputs correctly, as per our project's high standards for testing.

## 2. Architecture

This feature will not introduce new architecture, but will add to our existing test suite.

```mermaid
graph TD
    A[Test Suite] --> B{Unit Tests};
    A --> C{Integration Tests};
    B --> D(QueryService);
    C --> E[/api/v1/query];
```

## 3. Step-by-Step Plan

| Step | File(s) to Modify | Description | Validation |
| :--- | :--- | :--- | :--- |
| 1 | `tests/services/test_query_service.py` | Enhance the existing unit test to be a parameterized test that covers multiple `alpha` values (0.0, 0.25, 0.5, 0.75, 1.0), asserting that the correct weighting instruction is passed to the synthesis prompt in each case. | `pytest tests/services/test_query_service.py` passes. |
| 2 | `tests/api/test_query_endpoint.py` | Create a new integration test file for the query endpoint. | File exists. |
| 3 | `tests/api/test_query_endpoint.py` | Implement integration tests using FastAPI's `TestClient`. These tests will make real HTTP requests to the in-memory test application. | `pytest tests/api/test_query_endpoint.py` passes. |
| 4 | `tests/api/test_query_endpoint.py` | Add a test case for a valid request with a custom `alpha` value, mocking the `QueryService` to ensure the endpoint passes the value correctly. | Test passes. |
| 5 | `tests/api/test_query_endpoint.py` | Add a test case for a request with an out-of-range `alpha` value (e.g., 1.1), and assert that the API returns a `422 Unprocessable Entity` status code. | Test passes. |
| 6 | `tests/api/test_query_endpoint.py` | Add a test case for a request with a non-float `alpha` value (e.g., "abc"), and assert that the API returns a `422 Unprocessable Entity` status code. | Test passes. |

## 4. Success Criteria

- The `QueryService` unit tests are enhanced to cover a range of `alpha` values.
- New integration tests for the `/api/v1/query` endpoint are implemented.
- The integration tests validate both successful requests and error handling for invalid `alpha` values.
- All existing and new tests pass.