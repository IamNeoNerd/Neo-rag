import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider, useConfig } from './context/ConfigContext';
import Layout from './components/layout/Layout';
import SetupWizard from './components/onboarding/SetupWizard';
import QueryPage from './pages/QueryPage';
import IngestPage from './pages/IngestPage';
import SettingsPage from './pages/SettingsPage';
import HealthPage from './pages/HealthPage';
import './index.css';

function AppRoutes() {
  const { isConfigured, isLoading } = useConfig();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-300">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  // If not configured, show setup wizard
  if (!isConfigured) {
    return (
      <Routes>
        <Route path="/setup" element={<SetupWizard />} />
        <Route path="*" element={<Navigate to="/setup" replace />} />
      </Routes>
    );
  }

  // Main app routes
  return (
    <Layout>
      <Routes>
        <Route path="/query" element={<QueryPage />} />
        <Route path="/ingest" element={<IngestPage />} />
        <Route path="/settings" element={<SettingsPage />} />
        <Route path="/health" element={<HealthPage />} />
        <Route path="/" element={<Navigate to="/query" replace />} />
        <Route path="*" element={<Navigate to="/query" replace />} />
      </Routes>
    </Layout>
  );
}

function App() {
  return (
    <BrowserRouter>
      <ConfigProvider>
        <AppRoutes />
      </ConfigProvider>
    </BrowserRouter>
  );
}

export default App;
