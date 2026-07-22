import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getGraphQuery } from '../services/api';
import { Wrench, AlertTriangle, PenTool, CheckCircle, Info, RefreshCw } from 'lucide-react';

export default function MaintenanceIntelligence() {
  const { data: graphData, isLoading, error, refetch } = useQuery({
    queryKey: ['maintenanceGraph'],
    queryFn: () => getGraphQuery("MATCH (n:IndustrialNode) WHERE n.type CONTAINS 'Equipment' OR n.type CONTAINS 'Procedure' RETURN n LIMIT 50"),
  });

  const nodes = graphData?.data?.nodes || [];

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-accent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><Wrench className="mr-3 text-brand-accent" /> Maintenance Intelligence</h1>
        <p className="text-sm text-slate-400 mt-1">Aggregated historical failure data and predictive root cause analysis.</p>
      </div>

      {error ? (
        <div className="p-5 bg-red-950/20 border border-red-500/40 rounded-xl text-red-200 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <span>Failed to load graph nodes. Neo4j may be offline.</span>
          </div>
          <button onClick={() => refetch()} className="px-3.5 py-1.5 bg-red-800 hover:bg-red-700 text-white rounded-lg text-xs transition-colors flex items-center">
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Retry
          </button>
        </div>
      ) : nodes.length === 0 ? (
        <div className="glass-panel p-10 rounded-xl text-center space-y-4">
          <CheckCircle className="w-12 h-12 text-emerald-400 mx-auto" />
          <div>
            <h3 className="text-md font-semibold text-slate-200">No Historical Failures or Incidents Found</h3>
            <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
              No equipment nodes are currently indexed in the Neo4j Knowledge Graph. Upload a document containing maintenance records and run **Build Knowledge Graph** to populate this intelligence.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid gap-6">
          {nodes.map((node, idx) => (
            <div key={idx} className="glass-panel p-6 rounded-xl border-l-4 border-amber-500 space-y-4">
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-semibold text-amber-400 flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2" /> {node.name || 'Unknown Asset'} ({node.type})
                </h3>
              </div>
              <div className="bg-industrial-950/40 p-4 rounded-lg border border-industrial-800 space-y-2">
                <p className="text-xs text-slate-400 font-semibold uppercase flex items-center"><Info className="w-3.5 h-3.5 mr-1.5" /> Indexed Properties</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs font-mono">
                  {Object.entries(node.properties || {}).map(([k, v]) => (
                    <div key={k} className="flex justify-between border-b border-industrial-800 pb-1">
                      <span className="text-slate-500">{k}</span>
                      <span className="text-slate-300 truncate max-w-xs">{String(v)}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
