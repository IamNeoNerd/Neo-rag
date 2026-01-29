# Execution Plan: Core Ingestion Service

**Objective**: Implement the core data ingestion pipeline, including text chunking, embedding generation, and storage in the vector database.

---

### **Phase 1: Service Scaffolding**

1.  **Create Files**:
    *   `backend/app/services/embedding_service.py`
    *   `backend/app/services/ingestion_service.py`
    *   `tests/services/`
    *   `tests/services/test_ingestion_service.py`

2.  **Update `requirements.txt`**:
    *   Add `langchain` and `tiktoken`.

---

### **Phase 2: Embedding Service**

1.  **`backend/app/services/embedding_service.py`**:
    *   Import `OpenAIEmbeddings` from `langchain_openai`.
    *   Create a function `get_openai_embeddings()` that initializes and returns an `OpenAIEmbeddings` instance.
    *   Add similar functions for other providers (e.g., Cohere) as placeholders.

---

### **Phase 3: Ingestion Service**

1.  **`backend/app/services/ingestion_service.py`**:
    *   Import `RecursiveCharacterTextSplitter` from `langchain.text_splitter`.
    *   Import the embedding service and database connection modules.
    *   Implement `chunk_text(text: str) -> List[str]`:
        *   Uses `RecursiveCharacterTextSplitter` to split the input text into manageable chunks.
    *   Implement `ingest_text(text: str, metadata: dict)`:
        1.  Calls `chunk_text` to split the text.
        2.  Uses the `embedding_service` to generate embeddings for each chunk.
        3.  Connects to the Neon database.
        4.  Iterates through the chunks and embeddings, inserting them into the `documents` table.
        5.  (Placeholder) Add a comment indicating where entity/relationship extraction for Neo4j will occur.
        6.  Returns the number of chunks successfully ingested.

---

### **Phase 4: API Integration**

1.  **`backend/app/main.py`**:
    *   Import `ingestion_service` and the `IngestDataRequest` model.
    *   Create a new endpoint `POST /ingest`:
        *   Accepts an `IngestDataRequest` body.
        *   Calls `ingestion_service.ingest_text` with the provided data.
        *   Returns a confirmation message with the number of ingested chunks.

---

### **Phase 5: Testing**

1.  **`tests/services/test_ingestion_service.py`**:
    *   Write unit tests for `chunk_text` to ensure it splits text correctly.
    *   Write unit tests for `ingest_text`:
        *   Mock the `embedding_service` to return dummy embeddings.
        *   Mock the Neon database connection and cursor to verify that the correct `INSERT` statements are executed.
        *   Assert that the function returns the correct number of ingested chunks.

---

### **Success Criteria**

*   The new services and test files are created.
*   `pip install -r requirements.txt` runs without errors.
*   The `POST /ingest` endpoint is available and functional.
*   Sending text to the `/ingest` endpoint results in the text being chunked, "embedded" (mocked in tests), and "stored" (mocked in tests).
*   All unit tests for the ingestion service pass.