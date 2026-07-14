import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getSystemStatus } from '../services/api';
import { Activity, Server, Database, BrainCircuit, Bot } from 'lucide-react';

export default function SystemStatus() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['systemStatusFull'],
    queryFn: getSystemStatus,
    refetchInterval: 5000,
  });

  if (isLoading) return <div className="text-center mt-20 text-slate-400">Loading system status...</div>;
  if (error) return <div className="text-center mt-20 text-red-400">Error connecting to backend API.</div>;

  const stats = data?.data || {};

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><Activity className="mr-3 text-brand-accent" /> System Status</h1>
        <p className="text-sm text-slate-400 mt-1">Detailed telemetry for all microservices in the IndusMind platform.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ServicePanel name="FastAPI Core Backend" status={stats.backend} icon={Server} description="Handles REST routing and orchestration." />
        <ServicePanel name="ChromaDB Vector Store" status={stats.chromadb} icon={Database} description="Semantic search embeddings." />
        <ServicePanel name="Neo4j AuraDB" status={stats.neo4j} icon={Database} description="Industrial Knowledge Graph DB." />
        <ServicePanel name="Gemini 2.5 LLM" status={stats.gemini} icon={BrainCircuit} description="Advanced reasoning engine." />
        <ServicePanel name="LangGraph Orchestrator" status={stats.langgraph} icon={Bot} description="Multi-agent decision routing." />
      </div>
    </div>
  );
}

function ServicePanel({ name, status, icon: Icon, description }) {
  const isOnline = status === 'healthy' || status === 'connected';
  
  return (
    <div className="glass-panel p-6 rounded-xl flex items-start space-x-4">
      <div className={`p-4 rounded-lg ${isOnline ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
        <Icon className="w-8 h-8" />
      </div>
      <div className="flex-1">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-semibold text-slate-200">{name}</h3>
          <span className={`text-xs font-bold uppercase tracking-wide px-2 py-1 rounded ${isOnline ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
            {status || 'Unknown'}
          </span>
        </div>
        <p className="text-sm text-slate-400 mt-2">{description}</p>
      </div>
    </div>
  );
}
