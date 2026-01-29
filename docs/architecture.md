# Neo-rag v2.0 Architecture

This document outlines the high-level architecture of Neo-rag v2.0, detailing the interaction between the Frontend, Backend services, and the Dual-Database storage layer.

## System Overview

Neo-rag uses a **Hybrid Retrieval-Augmented Generation (RAG)** approach. It routes queries through both a Vector Database (for semantic understanding) and a Knowledge Graph (for structured relationships), fusing the results to provide contextually rich answers.

### Architecture Diagram

```mermaid
graph TB
    subgraph Client["🖥️ Client Layer (Frontend)"]
        UI[React SPA]
        Store[Context API Store]
        Router[React Router]
        
        UI -->|User Action| Router
        UI -->|State Updates| Store
        Store -->|API Calls| API[FastAPI Backend]
    end

    subgraph Backend["⚙️ Backend Layer (FastAPI)"]
        API
        
        subgraph Controllers["Routers"]
            Q_EP[Query Endpoint]
            I_EP[Ingest Endpoint]
            C_EP[Config Endpoint]
            H_EP[Health Endpoint]
        end

        subgraph Services["Core Services"]
            QS[Query Service]
            IS[Ingestion Service]
            RS[Retrieval Service]
            GES[Graph Extraction Service]
            CS[Chunking Service]
        end

        subgraph Models["Model Interface"]
            LLM_C[LLM Client]
            EMB_C[Embedding Client]
        end

        API --> Q_EP
        API --> I_EP
        API --> C_EP
        API --> H_EP

        Q_EP --> QS
        I_EP --> IS

        QS -->|1. Rewrite Query| LLM_C
        QS -->|2. Parallel Search| RS
        
        RS -->|Vector Search| EMB_C
        RS -->|Graph Traversal| NeoDriver[Neo4j Driver]
        
        RS -->|3. Hybrid Fusion| QS
        QS -->|4. Generate Answer| LLM_C
        
        IS -->|1. Parse| CS
        IS -->|2. Embed Chunks| EMB_C
        IS -->|3. Extract Entities| GES
        GES -->|Use LLM| LLM_C
    end

    subgraph Data["💾 Data Layer"]
        subgraph VectorDB["Neon PostgreSQL"]
            PG_V[pgvector Table]
            PG_M[Metadata Table]
        end
        
        subgraph GraphDB["Neo4j Aura"]
            Nodes[(Entities)]
            Edges((Relationships))
        end
    end

    subgraph External["☁️ Model Providers"]
        OpenAI
        Anthropic
        Gemini
    end

    %% Data Connections
    Services -->|Store/Retrieve Vectors| VectorDB
    Services -->|Store/Retrieve Graph| GraphDB
    
    %% Model Connections
    LLM_C -->|API| External
    EMB_C -->|API| External

    classDef client fill:#333,stroke:#ff0000,stroke-width:2px,color:#ffcccc;
    classDef service fill:#333,stroke:#ff0000,stroke-width:2px,color:#ffcccc;
    classDef data fill:#333,stroke:#ff0000,stroke-width:2px,color:#ffcccc;
    classDef external fill:#333,stroke:#ff0000,stroke-width:2px,color:#ffcccc;
    linkStyle default stroke:#ff0000,stroke-width:2px;
    
    class UI,Store,Router client;
    class QS,IS,RS,GES,CS service;
    class VectorDB,GraphDB,NeoDriver data;
    class OpenAI,Anthropic,Gemini external;
```

## Component Details

### 1. Frontend (Client)
Built with **React 19** and **Tailwind CSS**.
- **Context API**: Manages global state (Configuration, Health Status).
- **Setup Wizard**: Guides initial configuration and validates credentials.
- **Visual Feedback**: Real-time status indicators and "Pool Stats".

### 2. Backend Services
- **QueryService**: Orchestrates the RAG pipeline. It handles query rewriting, calls the Retrieval Service, and formats the final prompt.
- **RetrievalService**: The heart of the hybrid system. It executes:
  - **Vector Search** (Consine Similarity) in Neon.
  - **Graph Search** (Cypher) in Neo4j.
  - **Hybrid Fusion**: Merges results based on the configured `alpha` (weight).
- **IngestionService**: Processes uploaded files.
  - **Semantic Chunking**: Splits text based on meaning rather than just character count.
  - **Graph Extraction**: Uses LLMs to identify entities (Person, Place, Concept) and relations.

### 3. Data Storage
- **Neon PostgreSQL**: Stores text chunks and their embeddings using `pgvector`. Ideal for "fuzzy" semantic matching.
- **Neo4j Aura**: Stores the structured Knowledge Graph. Ideal for explicit connections and multi-hop reasoning.

## Data Flow: The Lifecycle of a Query

1. **User Input**: User asks "How does Semantic Chunking work?"
2. ** embedding**: The query is converted to a vector.
3. **Parallel Retrieval**:
   - **Vector**: Finds distinct text chunks about "chunking".
   - **Graph**: Finds the "Semantic Chunking" node and traverses to "Ingestion Service".
4. **Fusion**: The top results from both are combined.
5. **Generation**: The LLM receives the context and generates:
   > "Semantic Chunking is a process handled by the Ingestion Service that..."
