// Provider types for LLM and Embedding services

export type LLMProvider =
    | 'openai'
    | 'anthropic'
    | 'google'
    | 'groq'
    | 'ollama'
    | 'openai-compatible';

export type EmbeddingProvider =
    | 'openai'
    | 'cohere'
    | 'voyage'
    | 'huggingface'
    | 'ollama';

export type ConnectionStatus = 'connected' | 'disconnected' | 'checking' | 'error' | 'no_key';

// Provider configuration interfaces
export interface LLMConfig {
    provider: LLMProvider;
    apiKey: string;
    model: string;
    baseUrl?: string;
    temperature?: number;
    maxTokens?: number;
}

export interface EmbeddingConfig {
    provider: EmbeddingProvider;
    apiKey: string;
    model: string;
    baseUrl?: string;
}

export interface NeonConfig {
    connectionString: string;
}

export interface Neo4jConfig {
    uri: string;
    username: string;
    password: string;
}

export interface DatabaseConfig {
    neon: NeonConfig;
    neo4j: Neo4jConfig;
}

// Full application config
export interface AppConfig {
    llm: LLMConfig;
    embedding: EmbeddingConfig;
    database: DatabaseConfig;
    isConfigured: boolean;
}

// Service status interfaces
export interface ServiceStatus {
    name: string;
    status: ConnectionStatus;
    details?: string;
    usage?: {
        used: number;
        limit: number;
    };
}

export interface HealthStatus {
    neon: ServiceStatus;
    neo4j: ServiceStatus;
    llm: ServiceStatus;
    embedding: ServiceStatus;
}

// API Response types
export interface SourceCitation {
    source_id: string;
    source_type: 'vector_chunk' | 'graph_node';
    content_preview: string;
    similarity_score?: number;
}

export interface QueryResponse {
    answer: string;
    graph_context: string;
    vector_context: string;
    sources: string[];
    source_citations: SourceCitation[];
    confidence: number;
    routing_decision: 'vector' | 'graph' | 'hybrid' | 'none';
}

export interface IngestResponse {
    message: string;
    chunks_stored: number;
    strategy_used: string;
    chunk_count: number;
    avg_chunk_size: number;
    graph_nodes: number;
}

// Provider option types for dropdowns
export interface ProviderOption {
    id: string;
    name: string;
    models: string[];
    requiresApiKey: boolean;
    baseUrlEditable?: boolean;
}

export const LLM_PROVIDERS: ProviderOption[] = [
    { id: 'openai', name: 'OpenAI', models: ['gpt-4-turbo', 'gpt-4o', 'gpt-3.5-turbo'], requiresApiKey: true },
    { id: 'anthropic', name: 'Anthropic', models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'], requiresApiKey: true },
    { id: 'google', name: 'Google Gemini', models: ['gemini-pro', 'gemini-1.5-pro'], requiresApiKey: true },
    { id: 'groq', name: 'Groq', models: ['llama3-70b-8192', 'mixtral-8x7b-32768'], requiresApiKey: true },
    { id: 'ollama', name: 'Ollama (Local)', models: ['llama3', 'codellama', 'mistral'], requiresApiKey: false, baseUrlEditable: true },
    { id: 'openai-compatible', name: 'OpenAI Compatible', models: [], requiresApiKey: true, baseUrlEditable: true },
];

export const EMBEDDING_PROVIDERS: ProviderOption[] = [
    { id: 'openai', name: 'OpenAI', models: ['text-embedding-3-small', 'text-embedding-3-large'], requiresApiKey: true },
    { id: 'cohere', name: 'Cohere', models: ['embed-english-v3.0', 'embed-multilingual-v3.0'], requiresApiKey: true },
    { id: 'voyage', name: 'Voyage AI', models: ['voyage-large-2', 'voyage-code-2'], requiresApiKey: true },
    { id: 'huggingface', name: 'HuggingFace', models: ['sentence-transformers/*'], requiresApiKey: true },
    { id: 'ollama', name: 'Ollama (Local)', models: ['nomic-embed-text', 'all-minilm'], requiresApiKey: false, baseUrlEditable: true },
];
