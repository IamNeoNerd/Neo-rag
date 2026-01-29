import React from 'react';
import { NavLink } from 'react-router-dom';
import { Search, FileInput, Settings, Activity, HelpCircle } from 'lucide-react';
import { useConfig } from '../../context/ConfigContext';
import StatusBar from './StatusBar';

interface LayoutProps {
    children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
    const { isConfigured } = useConfig();

    const navItems = [
        { to: '/query', icon: Search, label: 'Query' },
        { to: '/ingest', icon: FileInput, label: 'Ingest' },
        { to: '/settings', icon: Settings, label: 'Settings' },
        { to: '/health', icon: Activity, label: 'Health' },
    ];

    return (
        <div className="min-h-screen flex flex-col lg:flex-row">
            {/* Desktop Sidebar */}
            <aside className="hidden lg:flex flex-col w-64 bg-dark-200 border-r border-gray-700">
                <div className="p-4 border-b border-gray-700">
                    <h1 className="text-2xl font-bold text-primary-400">Neo-rag</h1>
                    <p className="text-xs text-gray-500 mt-1">Hybrid RAG System</p>
                </div>

                <nav className="flex-1 p-4">
                    <ul className="space-y-2">
                        {navItems.map(({ to, icon: Icon, label }) => (
                            <li key={to}>
                                <NavLink
                                    to={to}
                                    className={({ isActive }) =>
                                        `flex items-center gap-3 px-4 py-2.5 rounded-lg transition-colors ${isActive
                                            ? 'bg-primary-600 text-white'
                                            : 'text-gray-400 hover:text-white hover:bg-dark-100'
                                        }`
                                    }
                                >
                                    <Icon size={20} />
                                    <span>{label}</span>
                                </NavLink>
                            </li>
                        ))}
                    </ul>
                </nav>

                <div className="p-4 border-t border-gray-700">
                    <a
                        href="https://github.com/your-repo/neo-rag"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 text-gray-500 hover:text-gray-300 text-sm"
                    >
                        <HelpCircle size={16} />
                        Documentation
                    </a>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col">
                {/* Status Bar */}
                <StatusBar />

                {/* Page Content */}
                <div className="flex-1 overflow-auto p-4 lg:p-6 bg-dark-300">
                    {children}
                </div>
            </main>

            {/* Mobile Bottom Nav */}
            <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-dark-200 border-t border-gray-700 safe-area-pb">
                <ul className="flex justify-around py-2">
                    {navItems.map(({ to, icon: Icon, label }) => (
                        <li key={to}>
                            <NavLink
                                to={to}
                                className={({ isActive }) =>
                                    `flex flex-col items-center gap-1 px-4 py-2 ${isActive ? 'text-primary-400' : 'text-gray-500'
                                    }`
                                }
                            >
                                <Icon size={20} />
                                <span className="text-xs">{label}</span>
                            </NavLink>
                        </li>
                    ))}
                </ul>
            </nav>
        </div>
    );
}
