# Context Attachment Guide

When coding with an AI assistant (Cursor, Cline, Roo code), attach relevant context files for accuracy.

## Best Practices
- Attach **only** the files needed for the task to avoid noise.
- For workflows: Attach `AGENT_WORKFLOWS.md`.
- For data ingestion: Attach `SCHEMA_GUIDELINES.md`.
- For auth & API keys: Attach `CREDENTIALS_SECURITY.md`.

## Example
If you ask AI to implement the retrieval agent:
```
#context AGENT_WORKFLOWS.md
Implement retrieval_agent.py according to the retrieval flow described.
```

---

## Do Not
- Dump the entire repo unless necessary.
- Forget to attach schema rules when coding ingestion logic.