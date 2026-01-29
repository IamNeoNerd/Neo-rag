# Roo Rules: The Definitive Guide for Project Development

This document contains the complete and authoritative set of rules for this project. These rules override all other instructions and are designed to ensure consistency, quality, and alignment with our architectural goals.

---

## 1. Core Principles

These are the non-negotiable foundations of our development process.

1.  **Docs are Law**: All development must strictly adhere to the project documentation. The primary sources of truth are `docs/architecture.md` and this `roorules.md` file.
2.  **No Guessing**: If a requirement is unclear or missing, **stop work immediately**. Output `"MISSING SPEC"` and request clarification from the project lead. Do not make assumptions.
3.  **No Drift**: Do not deviate from the approved architecture, technology stack, or workflows without explicit, documented approval in `docs/CHANGE_LOG.md`.
4.  **Simplicity First**: Do not over-engineer. Implement the simplest solution that meets the requirements.

---

## 2. Project Structure & Naming Conventions

A consistent structure is essential for maintainability.

### 2.1. Folder Structure

-   `docs/`: All project documentation (`.md` files).
-   `backend/app/`: All backend Python source code.
    -   `database/`: Database connection and query logic.
    -   `models/`: Pydantic data models.
    -   `services/`: Core business logic (ingestion, retrieval, etc.).
-   `frontend/`: All frontend code (React Native/Flutter).
-   `references/`: External reference materials and examples.

### 2.2. Naming Conventions

-   **Python**:
    -   `snake_case` for variables, functions, and filenames.
    -   `CamelCase` for classes.
-   **JavaScript/TypeScript**:
    -   `camelCase` for variables, functions, and filenames.
    -   `PascalCase` for components and classes.

---

## 3. Code Quality & Style

Write clean, maintainable, and robust code.

-   **Typing**: Use static typing for all code (Python type hints, TypeScript).
-   **Indentation**: 4 spaces for Python, 2 spaces for JS/TS.
-   **Function Design**: Functions should be small, single-purpose, and have clear inputs and outputs.
-   **Error Handling**:
    -   Catch all `async` calls and external API requests in `try...except` blocks.
    -   Provide meaningful, specific error messages. No silent failures.
-   **Comments**:
    -   Every function must have a docstring explaining its purpose, parameters, and return value.
    -   Comment any complex or non-obvious logic.

---

## 4. Development Workflow & Tooling

Follow this workflow for all development tasks.

1.  **Plan First**: Use the **Sequential Thinking** MCP server to break down complex tasks into smaller, logical steps before writing code.
2.  **Stay Updated**: Use the **Context7** MCP server to get the latest information on libraries and technologies.
3.  **Retain Knowledge**: Use the **Neo4j** MCP server to build a knowledge graph of project requirements and decisions.
4.  **Commit Atomically**: Commits should be small, focused, and represent a single logical change. Use the format `[Module] Action - Detail` (e.g., `[Service] Implemented retrieval pass 1`).
5.  **Version Control**: Push to GitHub after each significant, user-verified feature is complete.

---

## 5. Security

Security is not an afterthought.

-   **Sanitize Inputs**: Sanitize all user-provided data to prevent injection attacks (SQL, Cypher, Prompt Injection).
-   **No Hardcoded Secrets**: Never hardcode API keys or other credentials. Use environment variables managed by the backend.
-   **Secure Credential Storage**: All API keys must be stored encrypted at rest (AES-256).
-   **No Client-Side Secrets**: The frontend must never store or cache any API keys or secrets.

---

## 6. Documentation

If it's not documented, it doesn't exist.

-   **API Docs**: Automatically generate and maintain OpenAPI/Swagger documentation for all backend endpoints.
-   **Workflow Diagrams**: Keep all Mermaid diagrams in the `docs/` folder up-to-date with any architectural changes.
-   **Change Log**: Any changes to the tech stack, core workflows, or schemas must be documented in `docs/CHANGE_LOG.md`.