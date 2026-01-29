# Contributing to Neo-rag

Thank you for your interest in contributing to Neo-rag! We welcome contributions from the community to help make this the best Open Source Hybrid RAG system.

## 🛠️ Development Environment Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### 1. Backend Setup (FastAPI)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```
Update `.env` with your development keys.

Run the development server:
```bash
uvicorn app.main:app --reload
```
API Docs will be available at: http://localhost:8000/docs

### 2. Frontend Setup (React)

```bash
cd frontend
npm install
npm start
```
The app will run at http://localhost:3000.

---

## 🏗️ Project Structure

```
Neo-rag/
├── backend/
│   ├── app/
│   │   ├── database/    # Neon & Neo4j connectors
│   │   ├── services/    # Core logic (Ingest, Query, RAG)
│   │   ├── routers/     # API endpoints
│   │   ├── models/      # Pydantic models
│   │   └── utils/       # Helpers (Retry, Logging)
│   └── tests/           # Pytest suite
├── frontend/
│   ├── src/
│   │   ├── components/  # UI Components
│   │   ├── context/     # Config & State
│   │   ├── pages/       # Route pages
│   │   └── services/    # API client
└── docs/                # Project documentation
```

---

## 🧪 Testing

We aim for high test coverage. Please run tests before submitting a PR.

**Backend Tests:**
```bash
cd backend
pytest
```

**Frontend Tests:**
```bash
cd frontend
npm test
```

---

## 📝 Pull Request Guidelines

1. **Fork the repository** and create your feature branch (`git checkout -b feature/amazing-feature`).
2. **Commit your changes** (`git commit -m 'feat: Add some amazing feature'`).
   - Use [Conventional Commits](https://www.conventionalcommits.org/) format.
3. **Push to the branch** (`git push origin feature/amazing-feature`).
4. **Open a Pull Request**.

### Code Style
- **Python**: Follow PEP 8. We recommend using `ruff` or `black`.
- **TypeScript**: Follow the existing ESLint configuration.

## 🐛 Reporting Bugs
Please check the [Issues](https://github.com/iamneonerd/neo-rag/issues) page to see if the bug has already been reported. If not, open a new issue with a reproduction path.

Happy Coding! 🚀
