import React from 'react';
import { RefreshCw, Database, Cpu, PlugZap, Activity } from 'lucide-react';
import { useConfig } from '../context/ConfigContext';
import type { ServiceStatus, ConnectionStatus } from '../types';

export default function HealthPage() {
    const { health, refreshHealth } = useConfig();
    const [isRefreshing, setIsRefreshing] = React.useState(false);

    const handleRefresh = async () => {
        setIsRefreshing(true);
        await refreshHealth();
        setTimeout(() => setIsRefreshing(false), 500);
    };

    const services = [
        {
            key: 'neon',
            label: 'Neon PostgreSQL',
            icon: Database,
            description: 'Vector storage and embeddings',
            data: health?.neon
        },
        {
            key: 'neo4j',
            label: 'Neo4j Aura',
            icon: Activity,
            description: 'Knowledge graph storage',
            data: health?.neo4j
        },
        {
            key: 'llm',
            label: 'LLM Provider',
            icon: Cpu,
            description: 'Chat and completion',
            data: health?.llm
        },
        {
            key: 'embedding',
            label: 'Embedding Provider',
            icon: PlugZap,
            description: 'Text embeddings',
            data: health?.embedding
        },
    ];

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-white mb-2">System Health</h1>
                    <p className="text-gray-400">Monitor the status of all connected services</p>
                </div>
                <button
                    onClick={handleRefresh}
                    className="btn-secondary flex items-center gap-2"
                >
                    <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
                    Refresh
                </button>
            </div>

            {/* Service Cards */}
            <div className="grid gap-4 md:grid-cols-2">
                {services.map((service) => (
                    <ServiceCard
                        key={service.key}
                        label={service.label}
                        description={service.description}
                        Icon={service.icon}
                        status={service.data}
                    />
                ))}
            </div>

            {/* Pool Statistics */}
            {health?.neon && (
                <div className="card">
                    <h2 className="text-lg font-semibold text-white mb-4">Connection Pool</h2>
                    <div className="grid grid-cols-3 gap-4">
                        <PoolStat label="Active" value="3" color="text-yellow-400" />
                        <PoolStat label="Available" value="7" color="text-green-400" />
                        <PoolStat label="Max" value="10" color="text-gray-400" />
                    </div>
                    <div className="mt-4 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-green-500 to-yellow-500" style={{ width: '30%' }} />
                    </div>
                </div>
            )}
        </div>
    );
}

function ServiceCard({
    label,
    description,
    Icon,
    status
}: {
    label: string;
    description: string;
    Icon: React.ElementType;
    status?: ServiceStatus;
}) {
    // Map various backend status values to UI config
    const statusConfig: Record<string, { color: string; bgColor: string; text: string }> = {
        connected: { color: 'text-green-400', bgColor: 'bg-green-500/20', text: 'Connected' },
        active: { color: 'text-green-400', bgColor: 'bg-green-500/20', text: 'Connected' },
        configured: { color: 'text-green-400', bgColor: 'bg-green-500/20', text: 'Configured' },
        not_configured: { color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', text: 'Not Configured' },
        disconnected: { color: 'text-red-400', bgColor: 'bg-red-500/20', text: 'Disconnected' },
        checking: { color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', text: 'Checking...' },
        error: { color: 'text-red-400', bgColor: 'bg-red-500/20', text: 'Error' },
        no_key: { color: 'text-yellow-400', bgColor: 'bg-yellow-500/20', text: 'No API Key' },
    };

    const currentStatus = status?.status || 'checking';
    const config = statusConfig[currentStatus] || statusConfig.checking;

    return (
        <div className="card flex items-start gap-4">
            <div className={`p-3 rounded-lg ${config.bgColor}`}>
                <Icon size={24} className={config.color} />
            </div>
            <div className="flex-1">
                <div className="flex items-center justify-between">
                    <h3 className="font-medium text-white">{label}</h3>
                    <span className={`text-xs px-2 py-1 rounded-full ${config.bgColor} ${config.color}`}>
                        {config.text}
                    </span>
                </div>
                <p className="text-sm text-gray-500 mt-1">{description}</p>
                {status?.details && (
                    <p className="text-xs text-gray-400 mt-2">{status.details}</p>
                )}
                {status?.usage && (
                    <div className="mt-2">
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                            <span>Usage</span>
                            <span>{status.usage.used} / {status.usage.limit}</span>
                        </div>
                        <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
                            <div
                                className={`h-full ${status.usage.used / status.usage.limit > 0.8 ? 'bg-yellow-500' : 'bg-primary-500'}`}
                                style={{ width: `${(status.usage.used / status.usage.limit) * 100}%` }}
                            />
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function PoolStat({ label, value, color }: { label: string; value: string; color: string }) {
    return (
        <div className="text-center">
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-sm text-gray-500">{label}</p>
        </div>
    );
}
