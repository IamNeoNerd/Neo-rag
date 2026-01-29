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

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- Neon & Neo4j accounts

### 1. Clone & Setup Backend
```bash
git clone https://github.com/iamneonerd/Neo-rag.git
cd neo-rag/backend
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### 2. Start Frontend
```bash
cd ../frontend
npm install
npm start
```

### 3. Launch
Open **http://localhost:3000** and follow the **Setup Wizard** to configure your databases and LLM keys.

---

## 🔮 Roadmap

- **Phase 1-5 (Complete)**: Core RAG, Hybrid Search, Full UI, Config Management.
- **Phase 6 (Upcoming)**: Multi-tenancy, JWT Authentication, and Advanced Graph Visualization.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License.