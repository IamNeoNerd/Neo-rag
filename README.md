# Neo-rag 2.0: The Ultimate Hybrid RAG & GraphRAG Framework

![Neo-rag 2.0 Banner](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Backend-FastAPI-blue?logo=python)
![React](https://img.shields.io/badge/Frontend-React%2019-blue?logo=react)
![Neon](https://img.shields.io/badge/Vector%20DB-Neon%20Postgres-orange?logo=postgresql)
![Neo4j](https://img.shields.io/badge/Graph%20DB-Neo4j%20Aura-008CC1?logo=neo4j)
![License](https://img.shields.io/badge/License-MIT-green)

**Neo-rag 2.0** is an enterprise-grade **Hybrid Retrieval-Augmented Generation (RAG)** platform. It represents the next generation of RAG by seamlessly fusing the semantic precision of **Vector Search** (VectorRAG) with the deep relational reasoning of **Knowledge Graphs** (GraphRAG).

Designed for developers looking for high-accuracy, transparent, and manageable RAG pipelines, Neo-rag 2.0 sets the standard for tree-based and graph-tree hybrid retrieval systems.

---

## 🚀 Key Features

- **Hybrid Retrieval Engine**: Intelligent routing between Vector Search (semantic similarity) and Graph Search (structured relationships).
- **Dual-Database Architecture**: 
  - **Neon PostgreSQL** (pgvector) for blazing fast vector retrieval.
  - **Neo4j Aura** for knowledge graph deep reasoning.
- **Smart Ingestion**: 
  - **Semantic Chunking**: AI-driven text splitting for better context preservation.
  - **Graph Extraction**: Automatically extracts entities and relationships from unstructured text.
- **Modern User Interface**:
  - **Setup Wizard**: Easy onboarding for first-time users.
  - **Retrieval Balance Slider**: Fine-tune the "Alpha" (Vector vs. Graph) ratio in real-time.
  - **Health Dashboard**: Real-time monitoring of all service connections and pools.
  - **LLM Agnostic**: Support for OpenAI, Anthropic, Gemini, Groq, and local Ollama models.

---

## 📚 Documentation

- [**User Manual**](docs/USER_MANUAL.md): Complete guide on installation, setup, and usage.
- [**Developer Guide**](CONTRIBUTING.md): How to contribute, run tests, and architectural overview.
- [**Architecture**](docs/architecture.md): Deep dive into the system design.

---

## ⚙️ Installation & Setup

Neo-rag 2.0 consists of a **FastAPI Backend** and a **React Frontend**. Follow these steps to get both servers running.

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 18+** (npm or yarn)
- **Neon PostgreSQL** account (for Vector Search)
- **Neo4j Aura** account (for Knowledge Graph)

### 2. Clone the Repository
```bash
git clone https://github.com/iamneonerd/Neo-rag.git
cd Neo-rag
```

### 3. Backend Setup (FastAPI)
The backend handles the RAG logic, database connections, and LLM orchestration.

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment**:
   ```bash
   cp .env.example .env
   ```
   *Edit `.env` with your initial service placeholders if needed, though most config is handled via the UI.*
5. **Start Backend Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   *Backend will be live at http://localhost:8000*

### 4. Frontend Setup (React)
The frontend provides the interactive dashboard and setup wizard.

1. **Navigate to frontend directory**:
   ```bash
   cd ../frontend
   ```
2. **Install packages**:
   ```bash
   npm install
   ```
3. **Start Development Server**:
   ```bash
   npm start
   ```
   *Frontend will open at http://localhost:3000*

### 5. Final Configuration
Once both servers are running:
1. Open **http://localhost:3000** in your browser.
2. The **Setup Wizard** will automatically launch.
3. Enter your Neon, Neo4j, and LLM API keys.
4. Verify connections in the **Health Dashboard**.

---

## 🔮 Roadmap

- **Phase 1-5 (Complete)**: Core RAG, Hybrid Search, Full UI, Config Management.
- **Phase 6 (Upcoming)**: Multi-tenancy, JWT Authentication, and Advanced Graph Visualization.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License.