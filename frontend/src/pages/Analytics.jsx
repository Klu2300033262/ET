import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';
import { BarChart2, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { getSystemMetrics } from '../services/api';

export default function Analytics() {
  const { data: metricsData, isLoading, error, refetch } = useQuery({
    queryKey: ['systemMetrics'],
    queryFn: getSystemMetrics,
    refetchInterval: 5000,
  });

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-accent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-900/20 border border-red-500/50 rounded-lg text-red-200 text-center max-w-lg mx-auto mt-10">
        <h3 className="text-lg font-semibold flex items-center justify-center"><AlertCircle className="mr-2" /> Error Loading Analytics</h3>
        <p className="mt-2">Failed to retrieve analytics metrics from backend.</p>
        <button onClick={() => refetch()} className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors inline-flex items-center">
          <RefreshCw className="w-4 h-4 mr-2" /> Retry
        </button>
      </div>
    );
  }

  const metrics = metricsData?.data || {};

  // Chart 1: Ingestion Pipeline Breakdown
  const ingestionData = [
    { name: 'Documents', count: metrics.documents || 0 },
    { name: 'Processed', count: metrics.processed_documents || 0 },
    { name: 'Chunks', count: metrics.chunks || 0 },
    { name: 'Vectors Stored', count: metrics.vectors || 0 }
  ];

  // Chart 2: Traffic Comparison
  const trafficData = [
    { name: 'AI Assistant Queries', value: metrics.ai_requests || 0 },
    { name: 'Vector searches', value: metrics.search_requests || 0 }
  ];

  // Chart 3: Knowledge Graph Composition
  const graphData = [
    { name: 'Nodes', value: metrics.graph_nodes || 0 },
    { name: 'Relationships', value: metrics.graph_relationships || 0 }
  ];

  const PIE_COLORS = ['#3b82f6', '#10b981'];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><BarChart2 className="mr-3 text-brand-accent" /> System Analytics</h1>
        <p className="text-sm text-slate-400 mt-1">Live usage metrics, resource growth, and system traffic telemetry.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Ingestion metrics bar chart */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-md font-semibold text-slate-200 mb-4">Ingestion & Vectorization Growth</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ingestionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f1f5f9' }} />
                <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} name="Count" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Traffic usage pie chart */}
        <div className="glass-panel p-6 rounded-xl">
          <h3 className="text-md font-semibold text-slate-200 mb-4">API Search & AI Traffic</h3>
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={trafficData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {trafficData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f1f5f9' }} />
                <Legend verticalAlign="bottom" height={36} formatter={(value, entry) => <span className="text-xs text-slate-300">{value}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Knowledge graph metrics bar chart */}
        <div className="glass-panel p-6 rounded-xl lg:col-span-2">
          <h3 className="text-md font-semibold text-slate-200 mb-4">Knowledge Graph Entity & Relationship Distribution</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={graphData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#1e293b', color: '#f1f5f9' }} />
                <Bar dataKey="value" fill="#10b981" radius={[4, 4, 0, 0]} name="Graph Metrics" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
