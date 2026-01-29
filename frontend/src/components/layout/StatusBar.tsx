import React from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, Circle } from 'lucide-react';
import { useConfig } from '../../context/ConfigContext';
import type { ConnectionStatus } from '../../types';

function StatusIndicator({ status, label, usage }: {
    status: ConnectionStatus;
    label: string;
    usage?: { used: number; limit: number };
}) {
    const navigate = useNavigate();

    const statusColors: Record<ConnectionStatus, string> = {
        connected: 'text-green-400',
        disconnected: 'text-red-400',
        checking: 'text-yellow-400 animate-pulse',
        error: 'text-red-400',
        no_key: 'text-yellow-400',
    };

    const statusLabels: Record<ConnectionStatus, string> = {
        connected: '',
        disconnected: 'Disconnected',
        checking: 'Checking...',
        error: 'Error',
        no_key: 'No Key',
    };

    return (
        <button
            onClick={() => navigate('/settings')}
            className="flex items-center gap-1.5 px-2 py-1 rounded hover:bg-dark-100 transition-colors"
        >
            <Circle
                size={8}
                className={`fill-current ${statusColors[status]}`}
            />
            <span className="text-sm text-gray-300">{label}</span>
            {statusLabels[status] && (
                <span className="text-xs text-gray-500">({statusLabels[status]})</span>
            )}
            {usage && (
                <span className={`text-xs ${usage.used / usage.limit > 0.8 ? 'text-yellow-400' : 'text-gray-500'}`}>
                    {usage.used}/{usage.limit}
                </span>
            )}
        </button>
    );
}

export default function StatusBar() {
    const { health, refreshHealth } = useConfig();
    const [isRefreshing, setIsRefreshing] = React.useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        await refreshHealth();
        setTimeout(() => setIsRefreshing(false), 500);
    };

    return (
        <header className="flex items-center justify-between px-4 py-2 bg-dark-200 border-b border-gray-700">
            <div className="flex items-center gap-4 overflow-x-auto">
                <StatusIndicator
                    status={health?.neon?.status || 'checking'}
                    label="Neon"
                />
                <StatusIndicator
                    status={health?.neo4j?.status || 'checking'}
                    label="Neo4j"
                />
                <StatusIndicator
                    status={health?.llm?.status || 'no_key'}
                    label="LLM"
                    usage={health?.llm?.usage}
                />
                <StatusIndicator
                    status={health?.embedding?.status || 'no_key'}
                    label="Embedding"
                />
            </div>

            <button
                onClick={handleRefresh}
                className="p-2 text-gray-400 hover:text-white rounded-lg hover:bg-dark-100 transition-colors"
                title="Refresh status"
            >
                <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
            </button>
        </header>
    );
}
