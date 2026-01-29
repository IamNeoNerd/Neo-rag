---
description: Standard process for implementing a new feature
---

# New Feature Workflow

This workflow defines the standard process for implementing new features in Neo-rag.

## Phase 1: Planning

### 1. Create Feature Plan
Create a new plan document in `plans/` following the naming convention:
```
plans/XX_feature_name.md
```
Where XX is the next sequence number.

### 2. Plan Template
The plan should include:
- **Goal**: What problem does this solve?
- **Approach**: How will it be implemented?
- **Files to Modify**: List all files that will change
- **New Files**: List any new files to create
- **Testing Strategy**: How will changes be verified?
- **Rollback Plan**: How to undo if issues arise?

### 3. Get Approval
Request user approval of the plan before proceeding to implementation.

## Phase 2: Implementation

### 4. Create Feature Branch
```bash
git checkout -b feat/<feature-name>
```

### 5. Implement Changes
- Follow the plan step by step
- Make atomic commits after each logical unit
- Run tests frequently

### 6. Update Documentation
- Update `docs/AGENT_WORKFLOWS.md` if runtime behavior changes
- Update `README.md` if user-facing features change
- Add docstrings to all new functions

## Phase 3: Verification

### 7. Run Full Test Suite
// turbo
```bash
pytest --cov=backend/app -v
```

### 8. Manual Testing
Test the feature end-to-end through the API or frontend.

### 9. Code Review
Request user review of changes before merging.

## Phase 4: Completion

### 10. Merge and Update
```bash
git checkout main
git merge feat/<feature-name>
git push origin main
```

### 11. Update task.md
Mark the feature as complete in the task tracking document.
