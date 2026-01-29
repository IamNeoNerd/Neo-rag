# AI Coding Rules

This document outlines specific guidelines for AI assistants (like Cline) when contributing to this project. Adherence to these rules ensures code quality, consistency, and alignment with project goals.

## 1. Reference Only Project Docs

-   All design, architecture, and implementation details **must** be taken from the designated project documentation files.
-   **Mandatory Reference Files**:
    -   `/docs/plan.md`
    -   `/docs/architecture.md`
    -   `/docs/hybrid_agent_workflow.md`
    -   `/docs/schema_guidelines.md`
    -   `/docs/data_ingestion_rules.md`
    -   `/docs/ai_coding_rules.md` (this file)
-   **Prohibition**: Do **not** fabricate features, endpoints, or database schemas. All new additions must be explicitly derived from or align with these reference documents.

## 2. Coding Style Adherence

-   **Indentation**:
    -   Python: 4 spaces.
    -   JavaScript/TypeScript: 2 spaces.
-   **Naming Conventions**:
    -   Python: `snake_case` for variables, functions, and files. `CamelCase` for classes.
    -   JavaScript/TypeScript: `camelCase` for variables, functions, and files. `PascalCase` for components and classes.
-   **React Components (if applicable)**: Only functional components should be used.
-   **Error Handling**: Implement explicit error boundaries and appropriate HTTP status codes for API responses.

## 3. LLM Interaction Guidelines

-   **Context7 Usage**: Utilize the Context7 MCP server for obtaining updated information about tech stacks, libraries, and features. This ensures access to the latest and most accurate external knowledge.
-   **Sequential Thinking**: Employ the Sequential Thinking MCP server to plan and execute development tasks. For complex features, outline steps and thought processes before generating detailed code. This promotes structured problem-solving.
-   **Neo4j Memory**: Use the Neo4j MCP server to create a graph database of processes, requirements, and key project information. This helps maintain project alignment, retain important context, and prevent hallucination by providing a structured knowledge base.
-   **GitHub Integration**: Push the project to GitHub after each major phase is verified and completed by the user. This ensures version control and collaborative progress tracking.

## 4. Testing Standards

-   **Unit Testing**: Write unit tests for each agent logic path (e.g., `ingestion_service`, `retrieval_service`).
-   **Mocking**: Mock database calls and external API (LLM) interactions in tests to ensure isolated and fast testing.
-   **Coverage**: Strive for high test coverage (>80%) for core business logic (e.g., retrieval, ingestion).

## 5. Documentation Standards

-   **Function Docstrings**: All functions and methods must include comprehensive docstrings detailing:
    -   Purpose/Description.
    -   Parameters (`params`).
    -   Return values (`returns`).
    -   Example usage (`examples`).
-   **API Documentation**: Generate OpenAPI/Swagger documentation for all backend API endpoints.
-   **Workflow Diagrams**: Ensure workflow diagrams in `/docs` (e.g., `mermaid.md`, `hybrid_agent_workflow.md`) are kept up-to-date.

### 5.1. API Reference Standards

All API documentation, whether in code comments or generated docs, must adhere to the following structure for each endpoint:

1.  **Summary**: A concise, one-sentence description of the endpoint's function.
2.  **Parameters**: A detailed list of all path, query, and header parameters. Each parameter must include:
    -   `name`: The parameter name.
    -   `type`: The data type (e.g., `string`, `integer`).
    -   `required`: A boolean (`true`/`false`).
    -   `description`: A clear explanation of the parameter's purpose and any constraints.
3.  **Request Body**: An example of the request body schema, including data types and example values.
4.  **Responses**:
    -   A list of all possible HTTP status codes the endpoint can return.
    -   For each status code, provide a clear description of its meaning in the context of the request.
    -   Include an example of the response body for each successful (`2xx`) and error (`4xx`, `5xx`) response.
5.  **Permissions**: A clear statement specifying the authentication and authorization required to access the endpoint (e.g., "Requires admin-level token").

## 6. Security Best Practices

-   **Credential Handling**: Adhere strictly to `CREDENTIALS_SECURITY.md` for handling API keys and sensitive information. Never hardcode credentials or expose them in logs/frontend.
-   **Input Validation**: Validate all inputs to prevent injection attacks and ensure data integrity.

## 7. General Development Principles

-   **Mobile-First**: Prioritize mobile-first development in frontend design and implementation.
-   **Hybrid Retrieval**: Ensure the core hybrid retrieval mechanism (vector + graph) is correctly implemented and optimized.
-   **User Configurability**: Design the system to allow users to tweak model behavior (e.g., retrieval prompts) where specified.
