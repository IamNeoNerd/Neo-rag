import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { AppConfig, HealthStatus, ServiceStatus } from '../types';
import { getHealth, getConfig } from '../services/api';

interface ConfigContextType {
    config: AppConfig | null;
    health: HealthStatus | null;
    isLoading: boolean;
    isConfigured: boolean;
    refreshHealth: () => Promise<void>;
    updateLocalConfig: (newConfig: Partial<AppConfig>) => void;
    getApiKey: (provider: 'llm' | 'embedding') => string | undefined;
}

const defaultConfig: AppConfig = {
    llm: {
        provider: 'openai',
        apiKey: '',
        model: 'gpt-4-turbo',
    },
    embedding: {
        provider: 'openai',
        apiKey: '',
        model: 'text-embedding-3-small',
    },
    database: {
        neon: { connectionString: '' },
        neo4j: { uri: '', username: '', password: '' },
    },
    isConfigured: false,
};

const ConfigContext = createContext<ConfigContextType | undefined>(undefined);

export function ConfigProvider({ children }: { children: ReactNode }) {
    const [config, setConfig] = useState<AppConfig | null>(null);
    const [health, setHealth] = useState<HealthStatus | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Load config from localStorage on mount
    useEffect(() => {
        const savedConfig = localStorage.getItem('neo-rag-config');
        if (savedConfig) {
            try {
                setConfig(JSON.parse(savedConfig));
            } catch {
                setConfig(defaultConfig);
            }
        } else {
            setConfig(defaultConfig);
        }
        setIsLoading(false);
    }, []);

    // Save config to localStorage when it changes
    useEffect(() => {
        if (config) {
            localStorage.setItem('neo-rag-config', JSON.stringify(config));
        }
    }, [config]);

    // Refresh health status
    const refreshHealth = async () => {
        try {
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            const healthData: any = await getHealth();
            // Transform backend keys to frontend expected keys
            const transformed: HealthStatus = {
                neon: {
                    name: 'Neon PostgreSQL',
                    status: healthData.neon_database?.status || healthData.neon?.status || 'checking',
                    details: healthData.neon_database?.version || healthData.neon?.details,
                },
                neo4j: {
                    name: 'Neo4j Aura',
                    status: healthData.neo4j_database?.status || healthData.neo4j?.status || 'checking',
                    details: healthData.neo4j_database?.max_pool_size
                        ? `Pool: ${healthData.neo4j_database.max_pool_size}`
                        : healthData.neo4j?.details,
                },
                llm: {
                    name: 'LLM Provider',
                    status: healthData.llm?.status || 'checking',
                    details: healthData.llm?.provider ? `${healthData.llm.provider} - ${healthData.llm.model}` : undefined,
                },
                embedding: {
                    name: 'Embedding Provider',
                    status: healthData.embedding?.status || 'checking',
                    details: healthData.embedding?.provider ? `${healthData.embedding.provider} - ${healthData.embedding.model}` : undefined,
                },
            };
            setHealth(transformed);
        } catch (error) {
            console.error('Failed to fetch health:', error);
            // Set all services as disconnected
            setHealth({
                neon: { name: 'Neon', status: 'disconnected', details: 'Cannot reach backend' },
                neo4j: { name: 'Neo4j', status: 'disconnected', details: 'Cannot reach backend' },
                llm: { name: 'LLM', status: 'disconnected', details: 'Cannot reach backend' },
                embedding: { name: 'Embedding', status: 'disconnected', details: 'Cannot reach backend' },
            });
        }
    };

    // Poll health every 30 seconds
    useEffect(() => {
        refreshHealth();
        const interval = setInterval(refreshHealth, 30000);
        return () => clearInterval(interval);
    }, []);

    const updateLocalConfig = (newConfig: Partial<AppConfig>) => {
        setConfig(prev => prev ? { ...prev, ...newConfig } : { ...defaultConfig, ...newConfig });
    };

    const getApiKey = (provider: 'llm' | 'embedding'): string | undefined => {
        return config?.[provider]?.apiKey;
    };

    const isConfigured = config?.isConfigured ?? false;

    return (
        <ConfigContext.Provider value={{
            config,
            health,
            isLoading,
            isConfigured,
            refreshHealth,
            updateLocalConfig,
            getApiKey,
        }}>
            {children}
        </ConfigContext.Provider>
    );
}

export function useConfig() {
    const context = useContext(ConfigContext);
    if (context === undefined) {
        throw new Error('useConfig must be used within a ConfigProvider');
    }
    return context;
}
