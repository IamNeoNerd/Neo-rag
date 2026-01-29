# Development Workflow

This document outlines the standard process for developing new features in the Neo-rag project. Following this workflow ensures consistency, quality, and alignment with our architectural principles.

```mermaid
graph TD
    A[1. Feature Idea] --> B{Create Feature Request};
    B --> C["templates/feature_request.md"];
    C --> D{Generate Execution Plan};
    D -- reads --> E["CLAUDE.md"];
    D -- reads --> F["docs/architecture.md"];
    D -- reads --> G[examples/];
    D --> H["plans/feature_name.md"];
    H --> I{Review & Approve Plan};
    I -- Approved --> J{Switch to Code Mode};
    J --> K[Implement Feature];
    K --> L{Review Code};
    L -- Approved --> M[Merge & Complete];

    subgraph User
        A; B; I; L; M;
    end

    subgraph Roo [AI Assistant]
        D; J; K;
    end
```

## Workflow Steps

1.  **Feature Request**: The user defines a new feature by filling out a `feature_request.md` template. This template prompts for a clear description, references to examples, and any other critical context.

2.  **Plan Generation**: The AI assistant (Roo) reads the feature request, `CLAUDE.md` rules, the project architecture, and the code in the `examples/` directory. It then generates a detailed, step-by-step execution plan and saves it in a new `plans/` directory.

3.  **Plan Approval**: The user reviews the execution plan. This is a critical step to align on the approach before any code is written.

4.  **Implementation**: Once the plan is approved, the user and AI switch to **Code Mode**, and the AI executes the plan to build the feature.

5.  **Code Review**: The user reviews the final code to ensure it meets all requirements.