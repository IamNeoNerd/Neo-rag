import axios from 'axios';
import type {
    AppConfig,
    HealthStatus,
    QueryResponse,
    IngestResponse,
    LLMConfig,
    EmbeddingConfig,
    DatabaseConfig
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Health & Status
export async function getHealth(): Promise<HealthStatus> {
    const response = await api.get('/health');
    return response.data;
}

export async function getRateLimitStatus(): Promise<any> {
    const response = await api.get('/rate-limit-status');
    return response.data;
}

// Configuration
export async function getConfig(): Promise<AppConfig> {
    const response = await api.get('/api/v1/config');
    return response.data;
}

export async function updateConfig(config: Partial<AppConfig>): Promise<void> {
    await api.put('/api/v1/config', config);
}

export async function testConnection(type: 'neon' | 'neo4j' | 'llm' | 'embedding', config: any): Promise<{ success: boolean; message: string }> {
    const response = await api.post('/api/v1/config/test', { type, config });
    return response.data;
}

// Query
export async function query(
    queryText: string,
    alpha: number = 0.5,
    apiKey?: string
): Promise<QueryResponse> {
    const headers: Record<string, string> = {};
    if (apiKey) {
        headers['X-OpenAI-Key'] = apiKey;
    }

    const response = await api.post('/retrieve',
        { query: queryText, alpha },
        { headers }
    );
    return response.data;
}

// Ingestion
export async function ingest(
    text: string,
    metadata?: Record<string, any>,
    chunkingStrategy: string = 'auto',
    chunkSize: number = 1000,
    chunkOverlap: number = 200,
    apiKey?: string
): Promise<IngestResponse> {
    const headers: Record<string, string> = {};
    if (apiKey) {
        headers['X-OpenAI-Key'] = apiKey;
    }

    const response = await api.post('/ingest', {
        text,
        metadata,
        chunking_strategy: chunkingStrategy,
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap,
    }, { headers });

    return response.data;
}

// Validate API Key
export async function validateApiKey(
    provider: string,
    apiKey: string
): Promise<{ valid: boolean; message: string }> {
    const response = await api.post('/api/v1/validate-key', { provider, api_key: apiKey });
    return response.data;
}

export default api;
