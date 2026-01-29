import React, { useState } from 'react';
import { Save, Loader2, Eye, EyeOff, CheckCircle, AlertCircle } from 'lucide-react';
import { useConfig } from '../context/ConfigContext';
import { testConnection } from '../services/api';
import { LLM_PROVIDERS, EMBEDDING_PROVIDERS } from '../types';
import type { LLMProvider, EmbeddingProvider } from '../types';

type SettingsTab = 'llm' | 'embedding' | 'database';

export default function SettingsPage() {
    const { config, updateLocalConfig } = useConfig();
    const [activeTab, setActiveTab] = useState<SettingsTab>('llm');
    const [isLoading, setIsLoading] = useState(false);
    const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
    const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({});
    const [saved, setSaved] = useState(false);

    // Form state (initialize from config)
    const [llmProvider, setLlmProvider] = useState<LLMProvider>(config?.llm?.provider || 'openai');
    const [llmApiKey, setLlmApiKey] = useState(config?.llm?.apiKey || '');
    const [llmModel, setLlmModel] = useState(config?.llm?.model || 'gpt-4-turbo');

    const [embProvider, setEmbProvider] = useState<EmbeddingProvider>(config?.embedding?.provider || 'openai');
    const [embApiKey, setEmbApiKey] = useState(config?.embedding?.apiKey || '');
    const [embModel, setEmbModel] = useState(config?.embedding?.model || 'text-embedding-3-small');

    const [neonUrl, setNeonUrl] = useState(config?.database?.neon?.connectionString || '');
    const [neo4jUri, setNeo4jUri] = useState(config?.database?.neo4j?.uri || '');
    const [neo4jUser, setNeo4jUser] = useState(config?.database?.neo4j?.username || 'neo4j');
    const [neo4jPass, setNeo4jPass] = useState(config?.database?.neo4j?.password || '');

    const tabs = [
        { id: 'llm' as const, label: 'LLM Provider' },
        { id: 'embedding' as const, label: 'Embedding' },
        { id: 'database' as const, label: 'Databases' },
    ];

    const handleTest = async (type: string, testConfig: any) => {
        setIsLoading(true);
        try {
            const result = await testConnection(type as any, testConfig);
            setTestResults(prev => ({ ...prev, [type]: result }));
        } catch (error: any) {
            setTestResults(prev => ({
                ...prev,
                [type]: { success: false, message: error.message || 'Test failed' }
            }));
        }
        setIsLoading(false);
    };

    const handleSave = () => {
        updateLocalConfig({
            llm: { provider: llmProvider, apiKey: llmApiKey, model: llmModel },
            embedding: { provider: embProvider, apiKey: embApiKey, model: embModel },
            database: {
                neon: { connectionString: neonUrl },
                neo4j: { uri: neo4jUri, username: neo4jUser, password: neo4jPass },
            },
            isConfigured: true,
        });
        setSaved(true);
        setTimeout(() => setSaved(false), 2000);
    };

    const selectedLlmProvider = LLM_PROVIDERS.find(p => p.id === llmProvider);
    const selectedEmbProvider = EMBEDDING_PROVIDERS.find(p => p.id === embProvider);

    const toggleShowKey = (key: string) => {
        setShowKeys(prev => ({ ...prev, [key]: !prev[key] }));
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-2">Settings</h1>
                    <p className="text-gray-400">Configure your providers and connections</p>
                </div>
                <button
                    onClick={handleSave}
                    className="btn-primary flex items-center gap-2"
                >
                    {saved ? <CheckCircle size={16} /> : <Save size={16} />}
                    {saved ? 'Saved!' : 'Save All'}
                </button>
            </div>

            {/* Tabs */}
            <div className="flex gap-2 border-b border-gray-700">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-4 py-2 font-medium transition-colors border-b-2 -mb-px ${activeTab === tab.id
                                ? 'border-primary-500 text-primary-400'
                                : 'border-transparent text-gray-400 hover:text-white'
                            }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* LLM Tab */}
            {activeTab === 'llm' && (
                <div className="card space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Provider</label>
                        <select
                            value={llmProvider}
                            onChange={(e) => {
                                setLlmProvider(e.target.value as LLMProvider);
                                const provider = LLM_PROVIDERS.find(p => p.id === e.target.value);
                                if (provider?.models.length) setLlmModel(provider.models[0]);
                            }}
                            className="input-field"
                        >
                            {LLM_PROVIDERS.map(p => (
                                <option key={p.id} value={p.id}>{p.name}</option>
                            ))}
                        </select>
                    </div>

                    {selectedLlmProvider?.requiresApiKey && (
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">API Key</label>
                            <div className="flex gap-2">
                                <div className="relative flex-1">
                                    <input
                                        type={showKeys.llm ? 'text' : 'password'}
                                        value={llmApiKey}
                                        onChange={(e) => setLlmApiKey(e.target.value)}
                                        placeholder="sk-..."
                                        className="input-field pr-10"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => toggleShowKey('llm')}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                                    >
                                        {showKeys.llm ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                                <button
                                    onClick={() => handleTest('llm', { provider: llmProvider, apiKey: llmApiKey, model: llmModel })}
                                    disabled={isLoading || !llmApiKey}
                                    className="btn-secondary"
                                >
                                    {isLoading ? <Loader2 className="animate-spin" size={16} /> : 'Test'}
                                </button>
                            </div>
                            {testResults.llm && (
                                <p className={`text-sm mt-2 flex items-center gap-1 ${testResults.llm.success ? 'text-green-400' : 'text-red-400'}`}>
                                    {testResults.llm.success ? <CheckCircle size={14} /> : <AlertCircle size={14} />}
                                    {testResults.llm.message}
                                </p>
                            )}
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Model</label>
                        <select value={llmModel} onChange={(e) => setLlmModel(e.target.value)} className="input-field">
                            {selectedLlmProvider?.models.map(m => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                        </select>
                    </div>
                </div>
            )}

            {/* Embedding Tab */}
            {activeTab === 'embedding' && (
                <div className="card space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Provider</label>
                        <select
                            value={embProvider}
                            onChange={(e) => {
                                setEmbProvider(e.target.value as EmbeddingProvider);
                                const provider = EMBEDDING_PROVIDERS.find(p => p.id === e.target.value);
                                if (provider?.models.length) setEmbModel(provider.models[0]);
                            }}
                            className="input-field"
                        >
                            {EMBEDDING_PROVIDERS.map(p => (
                                <option key={p.id} value={p.id}>{p.name}</option>
                            ))}
                        </select>
                    </div>

                    {selectedEmbProvider?.requiresApiKey && (
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-2">API Key</label>
                            <div className="flex gap-2">
                                <div className="relative flex-1">
                                    <input
                                        type={showKeys.emb ? 'text' : 'password'}
                                        value={embApiKey}
                                        onChange={(e) => setEmbApiKey(e.target.value)}
                                        className="input-field pr-10"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => toggleShowKey('emb')}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white"
                                    >
                                        {showKeys.emb ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                                <button
                                    onClick={() => handleTest('embedding', { provider: embProvider, apiKey: embApiKey, model: embModel })}
                                    disabled={isLoading || !embApiKey}
                                    className="btn-secondary"
                                >
                                    Test
                                </button>
                            </div>
                        </div>
                    )}

                    <div>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Model</label>
                        <select value={embModel} onChange={(e) => setEmbModel(e.target.value)} className="input-field">
                            {selectedEmbProvider?.models.map(m => (
                                <option key={m} value={m}>{m}</option>
                            ))}
                        </select>
                    </div>

                    <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg flex items-start gap-2">
                        <AlertCircle size={16} className="text-yellow-400 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-yellow-300">
                            Changing the embedding model will require re-ingesting all documents.
                        </p>
                    </div>
                </div>
            )}

            {/* Database Tab */}
            {activeTab === 'database' && (
                <div className="card space-y-6">
                    <div>
                        <h3 className="text-lg font-medium text-white mb-4">Vector Database (Neon PostgreSQL)</h3>
                        <label className="block text-sm font-medium text-gray-300 mb-2">Connection String</label>
                        <div className="flex gap-2">
                            <input
                                type={showKeys.neon ? 'text' : 'password'}
                                value={neonUrl}
                                onChange={(e) => setNeonUrl(e.target.value)}
                                placeholder="postgresql://user:pass@host/db"
                                className="input-field flex-1"
                            />
                            <button
                                type="button"
                                onClick={() => toggleShowKey('neon')}
                                className="btn-secondary"
                            >
                                {showKeys.neon ? <EyeOff size={16} /> : <Eye size={16} />}
                            </button>
                            <button
                                onClick={() => handleTest('neon', { connectionString: neonUrl })}
                                disabled={isLoading || !neonUrl}
                                className="btn-secondary"
                            >
                                Test
                            </button>
                        </div>
                        {testResults.neon && (
                            <p className={`text-sm mt-2 ${testResults.neon.success ? 'text-green-400' : 'text-red-400'}`}>
                                {testResults.neon.message}
                            </p>
                        )}
                    </div>

                    <hr className="border-gray-700" />

                    <div>
                        <h3 className="text-lg font-medium text-white mb-4">Graph Database (Neo4j)</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">URI</label>
                                <input
                                    type="text"
                                    value={neo4jUri}
                                    onChange={(e) => setNeo4jUri(e.target.value)}
                                    placeholder="neo4j+s://xxxxx.databases.neo4j.io"
                                    className="input-field"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Username</label>
                                    <input
                                        type="text"
                                        value={neo4jUser}
                                        onChange={(e) => setNeo4jUser(e.target.value)}
                                        className="input-field"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
                                    <input
                                        type="password"
                                        value={neo4jPass}
                                        onChange={(e) => setNeo4jPass(e.target.value)}
                                        className="input-field"
                                    />
                                </div>
                            </div>
                            <button
                                onClick={() => handleTest('neo4j', { uri: neo4jUri, username: neo4jUser, password: neo4jPass })}
                                disabled={isLoading || !neo4jUri}
                                className="btn-secondary"
                            >
                                Test Neo4j Connection
                            </button>
                            {testResults.neo4j && (
                                <p className={`text-sm ${testResults.neo4j.success ? 'text-green-400' : 'text-red-400'}`}>
                                    {testResults.neo4j.message}
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
