import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState } from 'reactflow';
import 'reactflow/dist/style.css';
import { 
  Network, 
  Info, 
  X, 
  Search, 
  Filter, 
  BarChart3, 
  HelpCircle, 
  Database,
  Grid,
  AlertTriangle
} from 'lucide-react';
import dagre from 'dagre';
import { useQuery } from '@tanstack/react-query';
import { getGraphQuery, getSystemMetrics, getSystemStatus } from '../services/api';

const getLayoutedElements = (nodes, edges, direction = 'LR') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));
  
  const nodeWidth = 180;
  const nodeHeight = 44;
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });
  dagre.layout(dagreGraph);

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: 'left',
      sourcePosition: 'right',
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  return { nodes: newNodes, edges };
};

export default function KnowledgeGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState('All');

  // Queries
  const { data: statusData } = useQuery({
    queryKey: ['systemStatus'],
    queryFn: getSystemStatus,
  });

  const { data: metricsData } = useQuery({
    queryKey: ['systemMetrics'],
    queryFn: getSystemMetrics,
  });

  const { data: graphData, isLoading: isGraphLoading, error: graphError } = useQuery({
    queryKey: ['graphData'],
    queryFn: () => getGraphQuery('MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100'),
    refetchInterval: false,
    staleTime: Infinity,
  });

  // Calculate unique types and filter items
  const entityTypes = useMemo(() => {
    if (!graphData?.data?.nodes) return [];
    const types = new Set(graphData.data.nodes.map(n => n.type || n.category || 'Entity'));
    return ['All', ...Array.from(types)];
  }, [graphData]);

  useEffect(() => {
    if (graphData?.data?.nodes) {
      // Filter first
      let rawNodes = graphData.data.nodes;
      let rawEdges = graphData.data.edges || [];

      if (searchQuery.trim()) {
        const query = searchQuery.toLowerCase();
        rawNodes = rawNodes.filter(n => n.name?.toLowerCase().includes(query) || n.label?.toLowerCase().includes(query));
        const activeIds = new Set(rawNodes.map(n => n.id));
        rawEdges = rawEdges.filter(e => activeIds.has(e.source) && activeIds.has(e.target));
      }

      if (selectedType !== 'All') {
        rawNodes = rawNodes.filter(n => (n.type || n.category) === selectedType);
        const activeIds = new Set(rawNodes.map(n => n.id));
        rawEdges = rawEdges.filter(e => activeIds.has(e.source) && activeIds.has(e.target));
      }

      const formattedNodes = rawNodes.map(n => ({
        id: n.id,
        data: { label: n.name || n.label, ...n },
        style: { 
          background: '#0f172a', 
          color: '#f8fafc', 
          border: '1.5px solid #2563eb', 
          borderRadius: '8px', 
          padding: '8px 12px',
          fontSize: '12px',
          fontWeight: '500',
          boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
        }
      }));
      
      const formattedEdges = rawEdges.map(e => ({
        id: e.id || `${e.source}-${e.target}`,
        source: e.source,
        target: e.target,
        animated: true,
        label: e.type || e.label || '',
        style: { stroke: '#475569', strokeWidth: 1.5 },
        labelStyle: { fill: '#94a3b8', fontWeight: 600, fontSize: '10px' },
        labelBgStyle: { fill: '#0f172a' }
      }));

      const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
        formattedNodes,
        formattedEdges,
        'LR'
      );
      
      setNodes(layoutedNodes);
      setEdges(layoutedEdges);
    }
  }, [graphData, searchQuery, selectedType, setNodes, setEdges]);

  const onNodeClick = (event, node) => {
    setSelectedNode(node);
  };

  const neo4jOffline = statusData?.data?.neo4j !== 'connected';
  const hasNoNodes = nodes.length === 0;

  return (
    <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center"><Network className="mr-3 text-brand-accent" /> Knowledge Graph</h1>
          <p className="text-sm text-slate-400 mt-1">Explore entity topologies and engineering relationships.</p>
        </div>
      </div>

      <div className="flex-1 flex gap-6 min-h-0">
        {/* Left Side Controller Panel */}
        <div className="w-80 space-y-5 flex flex-col justify-start">
          {/* Node Search & Category filter */}
          <div className="glass-panel p-4 rounded-xl space-y-4">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center">
              <Filter className="w-3.5 h-3.5 mr-1.5 text-brand-accent" /> Filters
            </h3>
            
            <div className="relative">
              <input 
                type="text"
                placeholder="Search node name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full text-xs bg-industrial-950 border border-industrial-800 focus:border-brand-primary/50 text-slate-200 rounded-lg pl-8 pr-3 py-2 focus:outline-none"
              />
              <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-slate-500" />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] text-slate-500 font-semibold uppercase">Filter Entity Type</label>
              <select 
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                className="w-full text-xs bg-industrial-950 border border-industrial-800 text-slate-300 rounded-lg p-2 focus:outline-none focus:border-brand-primary"
              >
                {entityTypes.map(t => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Graph Statistics */}
          <div className="glass-panel p-4 rounded-xl space-y-3">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center">
              <BarChart3 className="w-3.5 h-3.5 mr-1.5 text-brand-primary" /> Graph Statistics
            </h3>
            <div className="grid grid-cols-2 gap-3 text-center">
              <div className="bg-industrial-950/40 p-2.5 rounded-lg border border-industrial-850">
                <span className="block text-[10px] text-slate-500 font-semibold uppercase">Total Nodes</span>
                <span className="text-lg font-bold text-slate-200">{metricsData?.data?.graph_nodes || 0}</span>
              </div>
              <div className="bg-industrial-950/40 p-2.5 rounded-lg border border-industrial-850">
                <span className="block text-[10px] text-slate-500 font-semibold uppercase">Edges</span>
                <span className="text-lg font-bold text-slate-200">{metricsData?.data?.graph_relationships || 0}</span>
              </div>
            </div>
          </div>

          {/* Legend */}
          <div className="glass-panel p-4 rounded-xl space-y-2">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Legend</h3>
            <div className="space-y-1.5 text-xs text-slate-300">
              <div className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded bg-blue-600"></span>
                <span>Industrial Node Entity</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="h-0.5 w-4 bg-slate-500"></span>
                <span>Extract Relationship (animated)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side Graph Canvas */}
        <div className="flex-1 glass-panel rounded-xl overflow-hidden border border-industrial-800 relative bg-industrial-950/20">
          {isGraphLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-industrial-950/80 z-30">
              <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-accent"></div>
            </div>
          )}

          {neo4jOffline ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center space-y-4 z-20">
              <AlertTriangle className="w-12 h-12 text-red-500" />
              <div>
                <h3 className="text-lg font-bold text-slate-200">Neo4j Database Offline</h3>
                <p className="text-sm text-slate-400 mt-1 max-w-sm">
                  The Knowledge Graph requires a connection to the Neo4j database. Ensure the docker container is up.
                </p>
              </div>
            </div>
          ) : hasNoNodes && !isGraphLoading ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center space-y-4 z-20">
              <HelpCircle className="w-12 h-12 text-brand-primary" />
              <div>
                <h3 className="text-lg font-bold text-slate-200">No Knowledge Graph Data Found</h3>
                <p className="text-sm text-slate-400 mt-1 max-w-sm">
                  The graph database is currently empty. Build the Knowledge Graph on a processed document to extract topology relationships.
                </p>
                <Link 
                  to="/processed-docs"
                  className="mt-4 px-4 py-2 bg-brand-primary hover:bg-brand-primary/90 text-white text-xs font-semibold rounded-lg shadow-lg transition-colors inline-block"
                >
                  Go to Processed Documents
                </Link>
              </div>
            </div>
          ) : (
            <ReactFlow 
              nodes={nodes} 
              edges={edges} 
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              fitView
              attributionPosition="bottom-right"
            >
              <Background color="#334155" gap={16} />
              <Controls className="bg-industrial-800 fill-slate-200 border-industrial-700" />
              <MiniMap style={{ background: '#090d16', border: '1px solid #1e293b' }} nodeColor="#2563eb" maskColor="rgba(2, 6, 23, 0.7)" />
            </ReactFlow>
          )}

          {/* Metadata Sidebar Panel */}
          {selectedNode && (
            <div className="absolute top-4 right-4 w-80 glass-panel rounded-xl border border-industrial-700 shadow-2xl p-5 bg-industrial-900/95 z-20">
              <div className="flex items-center justify-between border-b border-industrial-700 pb-3 mb-3">
                <h3 className="text-sm font-semibold text-slate-100 flex items-center">
                  <Info className="w-4 h-4 mr-2 text-brand-primary" /> Node Properties
                </h3>
                <button onClick={() => setSelectedNode(null)} className="text-slate-400 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="space-y-3 text-xs">
                <div>
                  <span className="block font-semibold uppercase text-slate-500">Name</span>
                  <span className="text-sm text-slate-200">{selectedNode.data.name || selectedNode.data.label}</span>
                </div>
                <div>
                  <span className="block font-semibold uppercase text-slate-500">Type</span>
                  <span className="inline-block mt-1 px-2.5 py-0.5 font-semibold rounded bg-purple-500/10 text-purple-300 border border-purple-500/20">
                    {selectedNode.data.type || selectedNode.data.category || 'Entity'}
                  </span>
                </div>
                
                {selectedNode.data.properties && Object.keys(selectedNode.data.properties).length > 0 && (
                  <div className="pt-3 border-t border-industrial-800/50">
                    <span className="block font-semibold uppercase text-slate-500 mb-2">Metadata Properties</span>
                    <div className="bg-industrial-950/50 rounded p-2.5 max-h-[300px] overflow-y-auto space-y-2 font-mono">
                      {Object.entries(selectedNode.data.properties).map(([key, val]) => (
                        <div key={key} className="flex flex-col">
                          <span className="text-slate-500">{key}</span>
                          <span className="text-slate-200 break-all">{String(val)}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
