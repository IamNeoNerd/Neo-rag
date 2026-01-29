import React, { useState } from 'react';
import { Upload, FileText, Loader2, CheckCircle } from 'lucide-react';
import { useConfig } from '../context/ConfigContext';
import { ingest } from '../services/api';
import type { IngestResponse } from '../types';

const CHUNKING_STRATEGIES = [
    { id: 'auto', name: 'Auto Detect', description: 'Automatically selects based on content' },
    { id: 'recursive', name: 'Recursive', description: 'Standard paragraph/sentence splitting' },
    { id: 'semantic', name: 'Semantic', description: 'Uses embeddings to find natural breakpoints' },
    { id: 'markdown', name: 'Markdown', description: 'Respects markdown structure' },
    { id: 'code', name: 'Code', description: 'Language-aware code splitting' },
];

export default function IngestPage() {
    const { getApiKey } = useConfig();
    const [text, setText] = useState('');
    const [strategy, setStrategy] = useState('auto');
    const [chunkSize, setChunkSize] = useState(1000);
    const [chunkOverlap, setChunkOverlap] = useState(200);
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState<IngestResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [showAdvanced, setShowAdvanced] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!text.trim()) return;

        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await ingest(
                text,
                {},
                strategy,
                chunkSize,
                chunkOverlap,
                getApiKey('llm')
            );
            setResult(response);
            setText(''); // Clear on success
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Ingestion failed');
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            setText(event.target?.result as string);
        };
        reader.readAsText(file);
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white mb-2">Ingest Documents</h1>
                <p className="text-gray-400">Add documents to your knowledge base</p>
            </div>

            <form onSubmit={handleSubmit} className="card space-y-6">
                {/* File Upload */}
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        Upload File
                    </label>
                    <label className="flex items-center justify-center gap-2 p-4 border-2 border-dashed border-gray-600 rounded-lg cursor-pointer hover:border-primary-500 transition-colors">
                        <Upload size={20} className="text-gray-400" />
                        <span className="text-gray-400">Click to upload or drag and drop</span>
                        <input
                            type="file"
                            accept=".txt,.md,.py,.js,.ts,.json"
                            onChange={handleFileUpload}
                            className="hidden"
                        />
                    </label>
                </div>

                {/* Text Input */}
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        Or Paste Text
                    </label>
                    <textarea
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Paste your document content here..."
                        className="input-field min-h-[200px] resize-none font-mono text-sm"
                        rows={10}
                    />
                    <p className="text-xs text-gray-500 mt-1">
                        {text.length} characters
                    </p>
                </div>

                {/* Chunking Strategy */}
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        Chunking Strategy
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                        {CHUNKING_STRATEGIES.map((s) => (
                            <button
                                key={s.id}
                                type="button"
                                onClick={() => setStrategy(s.id)}
                                className={`p-3 rounded-lg border text-left transition-all ${strategy === s.id
                                        ? 'border-primary-500 bg-primary-500/10'
                                        : 'border-gray-600 hover:border-gray-500'
                                    }`}
                            >
                                <p className={`text-sm font-medium ${strategy === s.id ? 'text-primary-400' : 'text-gray-300'}`}>
                                    {s.name}
                                </p>
                                <p className="text-xs text-gray-500 mt-1">{s.description}</p>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Advanced Options */}
                <div>
                    <button
                        type="button"
                        onClick={() => setShowAdvanced(!showAdvanced)}
                        className="text-sm text-gray-400 hover:text-white"
                    >
                        {showAdvanced ? '▼' : '▶'} Advanced Options
                    </button>

                    {showAdvanced && (
                        <div className="mt-4 grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Chunk Size
                                </label>
                                <input
                                    type="number"
                                    value={chunkSize}
                                    onChange={(e) => setChunkSize(parseInt(e.target.value))}
                                    min={100}
                                    max={5000}
                                    className="input-field"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-300 mb-2">
                                    Chunk Overlap
                                </label>
                                <input
                                    type="number"
                                    value={chunkOverlap}
                                    onChange={(e) => setChunkOverlap(parseInt(e.target.value))}
                                    min={0}
                                    max={1000}
                                    className="input-field"
                                />
                            </div>
                        </div>
                    )}
                </div>

                <button
                    type="submit"
                    disabled={isLoading || !text.trim()}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                >
                    {isLoading ? (
                        <>
                            <Loader2 className="animate-spin" size={16} />
                            Ingesting...
                        </>
                    ) : (
                        <>
                            <FileText size={16} />
                            Ingest Document
                        </>
                    )}
                </button>
            </form>

            {/* Error */}
            {error && (
                <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400">
                    {error}
                </div>
            )}

            {/* Success Result */}
            {result && (
                <div className="card flex items-start gap-4 bg-green-500/5 border-green-500/30">
                    <CheckCircle className="text-green-400 flex-shrink-0 mt-1" size={24} />
                    <div>
                        <h3 className="font-medium text-green-400 mb-2">Ingestion Successful</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                                <p className="text-gray-500">Strategy</p>
                                <p className="text-white">{result.strategy_used}</p>
                            </div>
                            <div>
                                <p className="text-gray-500">Chunks</p>
                                <p className="text-white">{result.chunk_count}</p>
                            </div>
                            <div>
                                <p className="text-gray-500">Avg Size</p>
                                <p className="text-white">{Math.round(result.avg_chunk_size)} chars</p>
                            </div>
                            <div>
                                <p className="text-gray-500">Graph Nodes</p>
                                <p className="text-white">{result.graph_nodes}</p>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
