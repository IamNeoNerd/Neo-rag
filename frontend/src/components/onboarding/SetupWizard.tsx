import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Database,
    Cpu,
    PlugZap,
    CheckCircle,
    ArrowRight,
    ArrowLeft,
    Loader2,
    AlertCircle
} from 'lucide-react';
import { useConfig } from '../../context/ConfigContext';
import { testConnection } from '../../services/api';
import { LLM_PROVIDERS, EMBEDDING_PROVIDERS } from '../../types';
import type { AppConfig, LLMProvider, EmbeddingProvider } from '../../types';

type Step = 'welcome' | 'database' | 'llm' | 'embedding' | 'review';

export default function SetupWizard() {
    const navigate = useNavigate();
    const { updateLocalConfig } = useConfig();
    const [currentStep, setCurrentStep] = useState<Step>('welcome');
    const [isLoading, setIsLoading] = useState(false);
    const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({});

    // Form state
    const [neonUrl, setNeonUrl] = useState('');
    const [neo4jUri, setNeo4jUri] = useState('');
    const [neo4jUser, setNeo4jUser] = useState('neo4j');
    const [neo4jPass, setNeo4jPass] = useState('');
    const [llmProvider, setLlmProvider] = useState<LLMProvider>('openai');
    const [llmApiKey, setLlmApiKey] = useState('');
    const [llmModel, setLlmModel] = useState('gpt-4-turbo');
    const [embProvider, setEmbProvider] = useState<EmbeddingProvider>('openai');
    const [embApiKey, setEmbApiKey] = useState('');
    const [embModel, setEmbModel] = useState('text-embedding-3-small');

    const steps: { id: Step; label: string; icon: React.ReactNode }[] = [
        { id: 'welcome', label: 'Welcome', icon: null },
        { id: 'database', label: 'Databases', icon: <Database size={20} /> },
        { id: 'llm', label: 'LLM', icon: <Cpu size={20} /> },
        { id: 'embedding', label: 'Embedding', icon: <PlugZap size={20} /> },
        { id: 'review', label: 'Review', icon: <CheckCircle size={20} /> },
    ];

    const handleTestConnection = async (type: 'neon' | 'neo4j' | 'llm' | 'embedding') => {
        setIsLoading(true);
        try {
            let config: any = {};
            switch (type) {
                case 'neon':
                    config = { connectionString: neonUrl };
                    break;
                case 'neo4j':
                    config = { uri: neo4jUri, username: neo4jUser, password: neo4jPass };
                    break;
                case 'llm':
                    config = { provider: llmProvider, apiKey: llmApiKey, model: llmModel };
                    break;
                case 'embedding':
                    config = { provider: embProvider, apiKey: embApiKey, model: embModel };
                    break;
            }
            const result = await testConnection(type, config);
            setTestResults(prev => ({ ...prev, [type]: result }));
        } catch (error: any) {
            setTestResults(prev => ({
                ...prev,
                [type]: { success: false, message: error.message || 'Connection failed' }
            }));
        }
        setIsLoading(false);
    };

    const handleComplete = () => {
        const config: AppConfig = {
            llm: { provider: llmProvider, apiKey: llmApiKey, model: llmModel },
            embedding: { provider: embProvider, apiKey: embApiKey, model: embModel },
            database: {
                neon: { connectionString: neonUrl },
                neo4j: { uri: neo4jUri, username: neo4jUser, password: neo4jPass },
            },
            isConfigured: true,
        };
        updateLocalConfig(config);
        navigate('/query');
    };

    const nextStep = () => {
        const stepOrder: Step[] = ['welcome', 'database', 'llm', 'embedding', 'review'];
        const currentIndex = stepOrder.indexOf(currentStep);
        if (currentIndex < stepOrder.length - 1) {
            setCurrentStep(stepOrder[currentIndex + 1]);
        }
    };

    const prevStep = () => {
        const stepOrder: Step[] = ['welcome', 'database', 'llm', 'embedding', 'review'];
        const currentIndex = stepOrder.indexOf(currentStep);
        if (currentIndex > 0) {
            setCurrentStep(stepOrder[currentIndex - 1]);
        }
    };

    const selectedLlmProvider = LLM_PROVIDERS.find(p => p.id === llmProvider);
    const selectedEmbProvider = EMBEDDING_PROVIDERS.find(p => p.id === embProvider);

    return (
        <div className="min-h-screen bg-dark-300 flex items-center justify-center p-4">
            <div className="max-w-2xl w-full">
                {/* Progress Steps */}
                {currentStep !== 'welcome' && (
                    <div className="flex justify-center mb-8">
                        {steps.slice(1).map((step, index) => (
                            <div key={step.id} className="flex items-center">
                                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 
                  ${currentStep === step.id
                                        ? 'border-primary-500 bg-primary-500/20 text-primary-400'
                                        : steps.indexOf(steps.find(s => s.id === currentStep)!) > index + 1
                                            ? 'border-green-500 bg-green-500/20 text-green-400'
                                            : 'border-gray-600 text-gray-500'
                                    }`}>
                                    {step.icon}
                                </div>
                                {index < steps.slice(1).length - 1 && (
                                    <div className={`w-16 h-0.5 mx-2 ${steps.indexOf(steps.find(s => s.id === currentStep)!) > index + 1
                                            ? 'bg-green-500'
                                            : 'bg-gray-600'
                                        }`} />
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Step Content */}
                <div className="card">
                    {currentStep === 'welcome' && (
                        <div className="text-center py-8">
                            <h1 className="text-3xl font-bold text-primary-400 mb-4">Welcome to Neo-rag</h1>
                            <p className="text-gray-400 mb-8 max-w-md mx-auto">
                                Let's set up your hybrid RAG system. You'll need to configure your databases and AI providers.
                            </p>
                            <button onClick={nextStep} className="btn-primary flex items-center gap-2 mx-auto">
                                Get Started <ArrowRight size={16} />
                            </button>
                        </div>
                    )}

                    {currentStep === 'database' && (
                        <div className="space-y-6">
                            <h2 className="text-xl font-semibold text-white">Database Connections</h2>

                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Neon PostgreSQL Connection String
                                    </label>
                                    <div className="flex gap-2">
                                        <input
                                            type="password"
                                            value={neonUrl}
                                            onChange={(e) => setNeonUrl(e.target.value)}
                                            placeholder="postgresql://user:pass@host/db"
                                            className="input-field flex-1"
                                        />
                                        <button
                                            onClick={() => handleTestConnection('neon')}
                                            disabled={isLoading || !neonUrl}
                                            className="btn-secondary whitespace-nowrap"
                                        >
                                            {isLoading ? <Loader2 className="animate-spin" size={16} /> : 'Test'}
                                        </button>
                                    </div>
                                    {testResults.neon && (
                                        <p className={`text-sm mt-2 ${testResults.neon.success ? 'text-green-400' : 'text-red-400'}`}>
                                            {testResults.neon.message}
                                        </p>
                                    )}
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-300 mb-2">
                                        Neo4j URI
                                    </label>
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
                                    onClick={() => handleTestConnection('neo4j')}
                                    disabled={isLoading || !neo4jUri}
                                    className="btn-secondary"
                                >
                                    {isLoading ? <Loader2 className="animate-spin" size={16} /> : 'Test Neo4j Connection'}
                                </button>
                                {testResults.neo4j && (
                                    <p className={`text-sm ${testResults.neo4j.success ? 'text-green-400' : 'text-red-400'}`}>
                                        {testResults.neo4j.message}
                                    </p>
                                )}
                            </div>
                        </div>
                    )}

                    {currentStep === 'llm' && (
                        <div className="space-y-6">
                            <h2 className="text-xl font-semibold text-white">LLM Provider</h2>

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
                                    <input
                                        type="password"
                                        value={llmApiKey}
                                        onChange={(e) => setLlmApiKey(e.target.value)}
                                        placeholder="sk-..."
                                        className="input-field"
                                    />
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

                            <button
                                onClick={() => handleTestConnection('llm')}
                                disabled={isLoading || (selectedLlmProvider?.requiresApiKey && !llmApiKey)}
                                className="btn-secondary"
                            >
                                {isLoading ? <Loader2 className="animate-spin" size={16} /> : 'Test LLM Connection'}
                            </button>
                            {testResults.llm && (
                                <p className={`text-sm ${testResults.llm.success ? 'text-green-400' : 'text-red-400'}`}>
                                    {testResults.llm.message}
                                </p>
                            )}
                        </div>
                    )}

                    {currentStep === 'embedding' && (
                        <div className="space-y-6">
                            <h2 className="text-xl font-semibold text-white">Embedding Provider</h2>

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
                                    <input
                                        type="password"
                                        value={embApiKey}
                                        onChange={(e) => setEmbApiKey(e.target.value)}
                                        placeholder="API Key"
                                        className="input-field"
                                    />
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
                                    Changing the embedding model later will require re-ingesting all documents.
                                </p>
                            </div>
                        </div>
                    )}

                    {currentStep === 'review' && (
                        <div className="space-y-6">
                            <h2 className="text-xl font-semibold text-white">Review Configuration</h2>

                            <div className="space-y-4">
                                <div className="p-4 bg-dark-100 rounded-lg">
                                    <h3 className="font-medium text-gray-300 mb-2">Databases</h3>
                                    <div className="text-sm text-gray-400 space-y-1">
                                        <p>Neon: {neonUrl ? '✅ Configured' : '❌ Not set'}</p>
                                        <p>Neo4j: {neo4jUri ? '✅ Configured' : '❌ Not set'}</p>
                                    </div>
                                </div>

                                <div className="p-4 bg-dark-100 rounded-lg">
                                    <h3 className="font-medium text-gray-300 mb-2">LLM Provider</h3>
                                    <p className="text-sm text-gray-400">{selectedLlmProvider?.name} - {llmModel}</p>
                                </div>

                                <div className="p-4 bg-dark-100 rounded-lg">
                                    <h3 className="font-medium text-gray-300 mb-2">Embedding Provider</h3>
                                    <p className="text-sm text-gray-400">{selectedEmbProvider?.name} - {embModel}</p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Navigation Buttons */}
                    {currentStep !== 'welcome' && (
                        <div className="flex justify-between mt-8 pt-6 border-t border-gray-700">
                            <button onClick={prevStep} className="btn-secondary flex items-center gap-2">
                                <ArrowLeft size={16} /> Back
                            </button>
                            {currentStep === 'review' ? (
                                <button onClick={handleComplete} className="btn-primary flex items-center gap-2">
                                    Complete Setup <CheckCircle size={16} />
                                </button>
                            ) : (
                                <button onClick={nextStep} className="btn-primary flex items-center gap-2">
                                    Next <ArrowRight size={16} />
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
