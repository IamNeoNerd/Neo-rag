import React, { useState } from 'react';
import { Send, Loader2, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { useConfig } from '../context/ConfigContext';
import { query as queryApi } from '../services/api';
import type { QueryResponse, SourceCitation } from '../types';

export default function QueryPage() {
    const { getApiKey } = useConfig();
    const [queryText, setQueryText] = useState('');
    const [alpha, setAlpha] = useState(0.5);
    const [isLoading, setIsLoading] = useState(false);
    const [response, setResponse] = useState<QueryResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [showSources, setShowSources] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!queryText.trim()) return;

        setIsLoading(true);
        setError(null);

        try {
            const result = await queryApi(queryText, alpha, getApiKey('llm'));
            setResponse(result);
        } catch (err: any) {
            setError(err.response?.data?.detail || err.message || 'Query failed');
        } finally {
            setIsLoading(false);
        }
    };

    const getConfidenceColor = (confidence: number) => {
        if (confidence >= 0.8) return 'bg-green-500';
        if (confidence >= 0.5) return 'bg-yellow-500';
        return 'bg-red-500';
    };

    const getRoutingBadge = (decision: string) => {
        const colors: Record<string, string> = {
            vector: 'bg-blue-500/20 text-blue-400',
            graph: 'bg-purple-500/20 text-purple-400',
            hybrid: 'bg-green-500/20 text-green-400',
            none: 'bg-gray-500/20 text-gray-400',
        };
        return colors[decision] || colors.none;
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-white mb-2">Query</h1>
                <p className="text-gray-400">Ask questions about your ingested documents</p>
            </div>

            {/* Query Form */}
            <form onSubmit={handleSubmit} className="card space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        Your Question
                    </label>
                    <textarea
                        value={queryText}
                        onChange={(e) => setQueryText(e.target.value)}
                        placeholder="Ask anything about your documents..."
                        className="input-field min-h-[100px] resize-none"
                        rows={3}
                    />
                </div>

                {/* Alpha Slider */}
                <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                        Retrieval Balance: <span className="text-primary-400">{Math.round(alpha * 100)}% Graph</span> / <span className="text-blue-400">{Math.round((1 - alpha) * 100)}% Vector</span>
                    </label>
                    <div className="flex items-center gap-4">
                        <span className="text-xs text-blue-400">Vector</span>
                        <input
                            type="range"
                            min="0"
                            max="1"
                            step="0.1"
                            value={alpha}
                            onChange={(e) => setAlpha(parseFloat(e.target.value))}
                            className="flex-1 h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-primary-500"
                        />
                        <span className="text-xs text-primary-400">Graph</span>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={isLoading || !queryText.trim()}
                    className="btn-primary w-full flex items-center justify-center gap-2"
                >
                    {isLoading ? (
                        <>
                            <Loader2 className="animate-spin" size={16} />
                            Processing...
                        </>
                    ) : (
                        <>
                            <Send size={16} />
                            Submit Query
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

            {/* Response */}
            {response && (
                <div className="card space-y-4">
                    {/* Metadata Bar */}
                    <div className="flex items-center gap-4 pb-4 border-b border-gray-700">
                        {/* Confidence */}
                        <div className="flex items-center gap-2">
                            <span className="text-xs text-gray-500">Confidence</span>
                            <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className={`h-full ${getConfidenceColor(response.confidence)}`}
                                    style={{ width: `${response.confidence * 100}%` }}
                                />
                            </div>
                            <span className="text-xs text-gray-400">{Math.round(response.confidence * 100)}%</span>
                        </div>

                        {/* Routing Decision */}
                        <span className={`text-xs px-2 py-1 rounded-full ${getRoutingBadge(response.routing_decision)}`}>
                            {response.routing_decision.toUpperCase()}
                        </span>

                        {/* Sources Toggle */}
                        <button
                            onClick={() => setShowSources(!showSources)}
                            className="ml-auto flex items-center gap-1 text-xs text-gray-400 hover:text-white"
                        >
                            {response.source_citations?.length || 0} Sources
                            {showSources ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        </button>
                    </div>

                    {/* Answer */}
                    <div className="prose prose-invert max-w-none">
                        <p className="text-gray-200 whitespace-pre-wrap">{response.answer}</p>
                    </div>

                    {/* Sources */}
                    {showSources && response.source_citations && response.source_citations.length > 0 && (
                        <div className="pt-4 border-t border-gray-700 space-y-3">
                            <h3 className="text-sm font-medium text-gray-300">Sources</h3>
                            {response.source_citations.map((citation, index) => (
                                <SourceCard key={index} citation={citation} />
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function SourceCard({ citation }: { citation: SourceCitation }) {
    const typeColors: Record<string, string> = {
        vector_chunk: 'bg-blue-500/20 text-blue-400',
        graph_node: 'bg-purple-500/20 text-purple-400',
    };

    return (
        <div className="p-3 bg-dark-100 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
                <span className={`text-xs px-2 py-0.5 rounded ${typeColors[citation.source_type] || 'bg-gray-500/20 text-gray-400'}`}>
                    {citation.source_type.replace('_', ' ')}
                </span>
                {citation.similarity_score && (
                    <span className="text-xs text-gray-500">
                        {Math.round(citation.similarity_score * 100)}% match
                    </span>
                )}
                <span className="text-xs text-gray-600 ml-auto">{citation.source_id}</span>
            </div>
            <p className="text-sm text-gray-400 line-clamp-2">{citation.content_preview}</p>
        </div>
    );
}
