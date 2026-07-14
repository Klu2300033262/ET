import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSystemStatus } from '../services/api';
import { Activity, Database, FileText, Network, Server, Hexagon } from 'lucide-react';

export default function Dashboard() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['systemStatus'],
    queryFn: getSystemStatus,
    refetchInterval: 10000,
  });

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-accent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-900/20 border border-red-500/50 rounded-lg text-red-200">
        <h3 className="text-lg font-semibold flex items-center"><Activity className="mr-2" /> Connection Error</h3>
        <p>Failed to connect to IndusMind Backend. Ensure the FastAPI server is running.</p>
      </div>
    );
  }

  const stats = data?.data || {};

  const cards = [
    { name: 'Total Documents', value: stats.documents ?? 0, icon: FileText, color: 'text-blue-400' },
    { name: 'Vector Chunks', value: stats.vectors ?? 0, icon: Database, color: 'text-purple-400' },
    { name: 'Graph Nodes', value: stats.nodes ?? 0, icon: Hexagon, color: 'text-emerald-400' },
    { name: 'Graph Relationships', value: stats.relationships ?? 0, icon: Network, color: 'text-amber-400' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Intelligence Dashboard</h1>
        <p className="text-sm text-slate-400 mt-1">Live overview of the industrial knowledge base.</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card) => (
          <div key={card.name} className="glass-panel p-6 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-slate-400">{card.name}</p>
              <p className="text-3xl font-bold text-slate-100 mt-2">{card.value}</p>
            </div>
            <div className={`p-4 rounded-full bg-industrial-800/50 ${card.color}`}>
              <card.icon className="w-8 h-8" />
            </div>
          </div>
        ))}
      </div>

      {/* System Health */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold text-slate-200 mb-4">Core Subsystems</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <StatusCard name="FastAPI Backend" status={stats.backend} />
          <StatusCard name="ChromaDB Vectors" status={stats.chromadb} />
          <StatusCard name="Neo4j AuraDB" status={stats.neo4j} />
          <StatusCard name="Gemini LLM" status={stats.gemini} />
          <StatusCard name="LangGraph Agentic Flow" status={stats.langgraph} />
        </div>
      </div>
    </div>
  );
}

function StatusCard({ name, status }) {
  const isOnline = status === 'healthy' || status === 'connected';
  return (
    <div className="glass-panel p-5 rounded-lg flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <Server className="w-5 h-5 text-slate-400" />
        <span className="font-medium text-slate-200">{name}</span>
      </div>
      <div className="flex items-center">
        <span className={`w-2 h-2 rounded-full mr-2 ${isOnline ? 'bg-green-500 shadow-[0_0_5px_rgba(34,197,94,0.6)]' : 'bg-red-500 shadow-[0_0_5px_rgba(239,68,68,0.6)]'}`}></span>
        <span className="text-sm text-slate-400 capitalize">{status}</span>
      </div>
    </div>
  );
}
