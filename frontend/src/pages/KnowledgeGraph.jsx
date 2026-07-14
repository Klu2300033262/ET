import React from 'react';
import ReactFlow, { Background, Controls } from 'reactflow';
import 'reactflow/dist/style.css';
import { Network } from 'lucide-react';

export default function KnowledgeGraph() {
  // Hardcoded stub for React Flow to render correctly
  const initialNodes = [
    { id: '1', position: { x: 250, y: 100 }, data: { label: 'Pump P-101' }, style: { background: '#1e293b', color: '#fff', border: '1px solid #0ea5e9', borderRadius: '8px', padding: '10px' } },
    { id: '2', position: { x: 100, y: 250 }, data: { label: 'Valve A-12' }, style: { background: '#1e293b', color: '#fff', border: '1px solid #64748b', borderRadius: '8px', padding: '10px' } },
    { id: '3', position: { x: 400, y: 250 }, data: { label: 'Cooling System' }, style: { background: '#1e293b', color: '#fff', border: '1px solid #64748b', borderRadius: '8px', padding: '10px' } },
  ];
  
  const initialEdges = [
    { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: '#0ea5e9' } },
    { id: 'e1-3', source: '1', target: '3', animated: true, style: { stroke: '#0ea5e9' } },
  ];

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><Network className="mr-3 text-brand-accent" /> Knowledge Graph</h1>
        <p className="text-sm text-slate-400 mt-1">Explore entity relationships extracted across documents.</p>
      </div>

      <div className="flex-1 glass-panel rounded-xl overflow-hidden border border-industrial-800">
        <ReactFlow nodes={initialNodes} edges={initialEdges} fitView>
          <Background color="#334155" gap={16} />
          <Controls className="bg-industrial-800 fill-slate-200 border-industrial-700" />
        </ReactFlow>
      </div>
    </div>
  );
}
