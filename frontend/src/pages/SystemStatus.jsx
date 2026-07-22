import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSystemStatus, getSystemLogs, getSystemRoutes } from '../services/api';
import { Activity, Server, Database, BrainCircuit, Bot, Terminal, Compass, AlertCircle, RefreshCw } from 'lucide-react';

export default function SystemStatus() {
  const [activeTab, setActiveTab] = useState('services');

  // Queries
  const { data: statusData, isLoading: isStatusLoading, error: statusError, refetch: refetchStatus } = useQuery({
    queryKey: ['systemStatusFull'],
    queryFn: getSystemStatus,
    refetchInterval: 5000,
  });

  const { data: logsData, isLoading: isLogsLoading } = useQuery({
    queryKey: ['systemLogs'],
    queryFn: () => getSystemLogs(50),
    enabled: activeTab === 'logs',
    refetchInterval: 5000,
  });

  const { data: routesData, isLoading: isRoutesLoading } = useQuery({
    queryKey: ['systemRoutes'],
    queryFn: getSystemRoutes,
    enabled: activeTab === 'routes',
  });

  if (isStatusLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-accent"></div>
      </div>
    );
  }

  if (statusError) {
    return (
      <div className="p-6 bg-red-900/20 border border-red-500/50 rounded-lg text-red-200 text-center max-w-lg mx-auto mt-10">
        <h3 className="text-lg font-semibold flex items-center justify-center"><AlertCircle className="mr-2" /> Connection Error</h3>
        <p className="mt-2">Failed to retrieve microservices status from the core backend.</p>
        <button onClick={() => refetchStatus()} className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors inline-flex items-center">
          <RefreshCw className="w-4 h-4 mr-2" /> Retry Connection
        </button>
      </div>
    );
  }

  const stats = statusData?.data || {};

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><Activity className="mr-3 text-brand-accent" /> System Status</h1>
        <p className="text-sm text-slate-400 mt-1">Real-time health statistics, application logs, and route registries.</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-industrial-800">
        <nav className="flex space-x-6">
          <button
            onClick={() => setActiveTab('services')}
            className={`border-b-2 py-3 px-1 text-sm font-medium transition-colors ${
              activeTab === 'services' ? 'border-brand-accent text-brand-accent' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            Subsystems Health
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`border-b-2 py-3 px-1 text-sm font-medium transition-colors ${
              activeTab === 'logs' ? 'border-brand-accent text-brand-accent' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            App Logs
          </button>
          <button
            onClick={() => setActiveTab('routes')}
            className={`border-b-2 py-3 px-1 text-sm font-medium transition-colors ${
              activeTab === 'routes' ? 'border-brand-accent text-brand-accent' : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            API Route Table
          </button>
        </nav>
      </div>

      {/* Subsystems Health Tab */}
      {activeTab === 'services' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ServicePanel name="FastAPI Core Backend" status={stats.backend} icon={Server} description="Handles REST routing and orchestration." />
          <ServicePanel name="ChromaDB Vector Store" status={stats.chromadb} icon={Database} description="Semantic search embeddings." />
          <ServicePanel name="Neo4j AuraDB" status={stats.neo4j} icon={Database} description="Industrial Knowledge Graph DB." />
          <ServicePanel name="Gemini 2.5 LLM" status={stats.gemini} icon={BrainCircuit} description="Advanced reasoning engine." />
          <ServicePanel name="LangGraph Orchestrator" status={stats.langgraph} icon={Bot} description="Multi-agent decision routing." />
        </div>
      )}

      {/* App Logs Tab */}
      {activeTab === 'logs' && (
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-md font-semibold text-slate-200 flex items-center"><Terminal className="w-5 h-5 mr-2 text-brand-accent" /> Tail log logs/app.log</h3>
          {isLogsLoading ? (
            <div className="text-slate-400 py-10 text-center text-sm">Loading application logs...</div>
          ) : (
            <pre className="bg-industrial-950 border border-industrial-800 rounded-lg p-4 font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto whitespace-pre-wrap max-h-[500px]">
              {logsData?.data?.logs?.join('\n') || 'No logs available.'}
            </pre>
          )}
        </div>
      )}

      {/* API Route Table Tab */}
      {activeTab === 'routes' && (
        <div className="glass-panel p-5 rounded-xl space-y-4">
          <h3 className="text-md font-semibold text-slate-200 flex items-center"><Compass className="w-5 h-5 mr-2 text-brand-primary" /> Registered API Routes</h3>
          {isRoutesLoading ? (
            <div className="text-slate-400 py-10 text-center text-sm">Loading routes...</div>
          ) : (
            <div className="border border-industrial-800 rounded-lg overflow-hidden">
              <table className="min-w-full divide-y divide-industrial-800 text-xs">
                <thead className="bg-industrial-900/60">
                  <tr>
                    <th className="px-5 py-3 text-left font-semibold text-slate-400 uppercase tracking-wider">Path</th>
                    <th className="px-5 py-3 text-left font-semibold text-slate-400 uppercase tracking-wider">Name</th>
                    <th className="px-5 py-3 text-left font-semibold text-slate-400 uppercase tracking-wider">Methods</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-industrial-800 bg-industrial-950/20">
                  {routesData?.data?.routes?.map((route, idx) => (
                    <tr key={idx} className="hover:bg-industrial-800/10">
                      <td className="px-5 py-3 font-mono text-brand-accent font-semibold">{route.path}</td>
                      <td className="px-5 py-3 text-slate-300">{route.name}</td>
                      <td className="px-5 py-3 font-mono text-slate-400">{route.methods?.join(', ')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ServicePanel({ name, status, icon: Icon, description }) {
  const isOnline = status === 'healthy' || status === 'connected';
  
  return (
    <div className="glass-panel p-6 rounded-xl flex items-start space-x-4">
      <div className={`p-4 rounded-lg ${isOnline ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
        <Icon className="w-8 h-8" />
      </div>
      <div className="flex-1">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-slate-200">{name}</h3>
          <span className={`text-xs font-bold uppercase tracking-wide px-2.5 py-1 rounded border ${isOnline ? 'bg-green-500/20 text-green-400 border-green-500/20' : 'bg-red-500/20 text-red-400 border-red-500/20'}`}>
            {status || 'Unknown'}
          </span>
        </div>
        <p className="text-sm text-slate-400 mt-2">{description}</p>
      </div>
    </div>
  );
}
