import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSystemMetrics, getSystemStatus, getProcessedDocuments } from '../services/api';
import { 
  Activity, 
  Database, 
  FileText, 
  Network, 
  Server, 
  Hexagon, 
  Heart, 
  AlertTriangle,
  MessageSquare,
  Search,
  Sparkles
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const { data: metricsData, isLoading: isMetricsLoading, error: metricsError } = useQuery({
    queryKey: ['systemMetrics'],
    queryFn: getSystemMetrics,
    refetchInterval: 5000,
  });

  const { data: statusData, isLoading: isStatusLoading } = useQuery({
    queryKey: ['systemStatus'],
    queryFn: getSystemStatus,
    refetchInterval: 5000,
  });

  const { data: docsData } = useQuery({
    queryKey: ['processedDocs'],
    queryFn: getProcessedDocuments,
    refetchInterval: 5000,
  });

  if (isMetricsLoading || isStatusLoading) {
    return (
      <div className="flex h-full items-center justify-center min-h-[300px]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-accent"></div>
      </div>
    );
  }

  if (metricsError) {
    return (
      <div className="p-6 bg-red-900/20 border border-red-500/50 rounded-lg text-red-200">
        <h3 className="text-lg font-semibold flex items-center"><Activity className="mr-2 animate-pulse" /> Connection Error</h3>
        <p className="text-sm mt-1">Failed to connect to IndusMind Backend. Ensure the FastAPI server is running.</p>
      </div>
    );
  }

  const metrics = metricsData?.data || {};
  const status = statusData?.data || {};
  const docs = docsData?.data || [];

  // Determine overall health
  const isHealthy = status.backend === 'healthy' && status.chromadb === 'connected' && status.neo4j === 'connected' && status.gemini === 'connected';
  const isDegraded = status.backend === 'healthy' && (status.chromadb !== 'connected' || status.neo4j !== 'connected' || status.gemini !== 'connected');

  const cards = [
    { name: 'Total Documents', value: metrics.documents ?? 0, icon: FileText, color: 'text-blue-400' },
    { name: 'Vector Chunks', value: metrics.vectors ?? 0, icon: Database, color: 'text-purple-400' },
    { name: 'Graph Nodes', value: metrics.graph_nodes ?? 0, icon: Hexagon, color: 'text-emerald-400' },
    { name: 'Graph Relationships', value: metrics.graph_relationships ?? 0, icon: Network, color: 'text-amber-400' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Intelligence Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">Live overview of the industrial knowledge base.</p>
        </div>
        
        {/* System Health Badge */}
        <div className={`px-4 py-2 rounded-xl flex items-center space-x-2 border ${
          isHealthy 
            ? 'bg-green-500/10 text-green-400 border-green-500/20' 
            : isDegraded 
              ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' 
              : 'bg-red-500/10 text-red-400 border-red-500/20'
        }`}>
          <Heart className="w-4 h-4" />
          <span className="text-xs font-semibold uppercase tracking-wider">
            System: {isHealthy ? 'Healthy' : isDegraded ? 'Degraded' : 'Offline'}
          </span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => (
          <div key={card.name} className="glass-panel p-6 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{card.name}</p>
              <p className="text-3xl font-bold text-slate-100 mt-2">{card.value}</p>
            </div>
            <div className={`p-4 rounded-xl bg-industrial-950/40 ${card.color}`}>
              <card.icon className="w-8 h-8" />
            </div>
          </div>
        ))}
      </div>

      {/* Auxiliary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-5 rounded-xl flex items-center space-x-4">
          <MessageSquare className="w-8 h-8 text-brand-primary" />
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wider">AI Queries</p>
            <p className="text-xl font-bold text-slate-200">{metrics.ai_requests ?? 0}</p>
          </div>
        </div>
        <div className="glass-panel p-5 rounded-xl flex items-center space-x-4">
          <Search className="w-8 h-8 text-brand-accent" />
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wider">Vector Searches</p>
            <p className="text-xl font-bold text-slate-200">{metrics.search_requests ?? 0}</p>
          </div>
        </div>
        <div className="glass-panel p-5 rounded-xl flex items-center space-x-4">
          <Sparkles className="w-8 h-8 text-emerald-400" />
          <div>
            <p className="text-xs text-slate-400 uppercase tracking-wider">Avg AI Confidence</p>
            <p className="text-xl font-bold text-slate-200">
              {metrics.avg_confidence ? `${(metrics.avg_confidence * 100).toFixed(0)}%` : '0%'}
            </p>
          </div>
        </div>
      </div>

      {/* Subsystems Health Grid */}
      <div className="mt-6">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Core Subsystems Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <StatusIndicator name="FastAPI Backend" status={status.backend} />
          <StatusIndicator name="ChromaDB Vectors" status={status.chromadb} />
          <StatusIndicator name="Neo4j AuraDB" status={status.neo4j} />
          <StatusIndicator name="Gemini LLM" status={status.gemini} />
          <StatusIndicator name="LangGraph Flow" status={status.langgraph} />
        </div>
      </div>

      {/* Recent Uploads */}
      <div className="mt-8">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Recent Ingestion Queue</h2>
        <div className="glass-panel overflow-hidden rounded-xl border border-industrial-800">
          {docs.length === 0 ? (
            <div className="p-6 text-slate-400 italic text-center text-sm">No processed documents in list.</div>
          ) : (
            <ul className="divide-y divide-industrial-800">
              {docs.slice(0, 5).map((doc, idx) => (
                <li key={idx} className="px-6 py-4 flex items-center justify-between hover:bg-industrial-800/20 transition-colors">
                  <Link to={`/documents/${doc.document_id}`} className="flex items-center space-x-3 hover:underline">
                    <FileText className="w-5 h-5 text-brand-primary" />
                    <span className="text-sm font-medium text-slate-200">{doc.filename || 'Unknown'}</span>
                  </Link>
                  <div className="flex items-center space-x-6 text-xs text-slate-400">
                    <span className="flex items-center"><Database className="w-3.5 h-3.5 mr-1 text-purple-400" /> {doc.total_chunks || 0} chunks</span>
                    <span>{doc.processed_at ? new Date(doc.processed_at).toLocaleDateString() : ''}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}

function StatusIndicator({ name, status }) {
  const isOnline = status === 'healthy' || status === 'connected';
  return (
    <div className="glass-panel p-4 rounded-xl flex items-center justify-between text-xs">
      <div className="flex items-center space-x-2">
        <Server className="w-4 h-4 text-slate-400" />
        <span className="font-semibold text-slate-200">{name}</span>
      </div>
      <div className="flex items-center">
        <span className={`w-2 h-2 rounded-full mr-2 ${isOnline ? 'bg-green-500 shadow-[0_0_5px_rgba(34,197,94,0.6)]' : 'bg-red-500 shadow-[0_0_5px_rgba(239,68,68,0.6)]'}`}></span>
        <span className="text-slate-400 capitalize">{status || 'Offline'}</span>
      </div>
    </div>
  );
}
