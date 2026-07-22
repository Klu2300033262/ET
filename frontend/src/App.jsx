import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import DocumentUpload from './pages/DocumentUpload';
import ProcessedDocuments from './pages/ProcessedDocuments';
import SemanticSearch from './pages/SemanticSearch';
import AIAssistant from './pages/AIAssistant';
import KnowledgeGraph from './pages/KnowledgeGraph';
import MaintenanceIntelligence from './pages/MaintenanceIntelligence';
import ComplianceIntelligence from './pages/ComplianceIntelligence';
import Analytics from './pages/Analytics';
import SystemStatus from './pages/SystemStatus';
import DocumentDetails from './pages/DocumentDetails';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<DocumentUpload />} />
            <Route path="/documents" element={<ProcessedDocuments />} />
            <Route path="/documents/:documentId" element={<DocumentDetails />} />
            <Route path="/search" element={<SemanticSearch />} />
            <Route path="/chat" element={<AIAssistant />} />
            <Route path="/graph" element={<KnowledgeGraph />} />
            <Route path="/maintenance" element={<MaintenanceIntelligence />} />
            <Route path="/compliance" element={<ComplianceIntelligence />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/status" element={<SystemStatus />} />
          </Routes>
        </MainLayout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
