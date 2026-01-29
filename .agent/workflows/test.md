---
description: Run the full test suite with coverage reporting
---

# Test Workflow

This workflow runs all project tests with coverage reporting.

## Prerequisites
- Python environment with test dependencies installed
- `pytest` and `pytest-cov` available

## Steps

### 1. Run All Tests with Coverage
// turbo
```bash
cd d:\P-Projects\Neo-rag
pytest --cov=backend/app --cov-report=term-missing -v
```

### 2. Run Specific Test Categories

#### API Tests Only
```bash
pytest tests/api/ -v
```

#### Service Tests Only
```bash
pytest tests/services/ -v
```

#### Database Tests Only
```bash
pytest tests/database/ -v
```

### 3. Run Single Test File
```bash
pytest tests/services/test_query_service.py -v
```

## Coverage Requirements
- Target: >80% for `backend/app/services/`
- All new features must include tests
- Mock all external calls (LLM, databases)

## Troubleshooting
- If tests fail to find modules: `set PYTHONPATH=.` before running
- For async test issues: ensure `pytest-asyncio` is installed
