import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, Link } from 'react-router-dom';
import { 
  getProcessedDocuments, 
  embedDocument, 
  buildGraph, 
  deleteDocument,
  downloadOriginalPDF,
  processDocument
} from '../services/api';
import { 
  FileText, 
  Database, 
  Hexagon, 
  Trash2, 
  Download, 
  ChevronRight, 
  Info,
  Check,
  Play,
  Settings,
  Grid,
  FileSpreadsheet,
  AlertCircle,
  RefreshCw,
  Loader2
} from 'lucide-react';

export default function ProcessedDocuments() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [selectedIds, setSelectedIds] = useState([]);
  const [isBulkRunning, setIsBulkRunning] = useState(false);
  const [bulkMessage, setBulkMessage] = useState('');

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['processedDocs'],
    queryFn: getProcessedDocuments,
    refetchInterval: 5000, // Refresh status every 5s
  });

  const docs = data?.data || [];

  // Mutations
  const processMutation = useMutation({
    mutationFn: (id) => processDocument(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['processedDocs'] })
  });

  const embedMutation = useMutation({
    mutationFn: (id) => embedDocument(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['processedDocs'] })
  });

  const graphMutation = useMutation({
    mutationFn: (id) => buildGraph(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['processedDocs'] })
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['processedDocs'] });
      queryClient.invalidateQueries({ queryKey: ['systemMetrics'] });
    }
  });

  // Select handlers
  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(docs.map(d => d.document_id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  // Bulk Actions
  const handleBulkEmbed = async () => {
    setIsBulkRunning(true);
    setBulkMessage('Generating embeddings for selected documents...');
    for (const id of selectedIds) {
      try {
        await embedDocument(id);
      } catch (err) {
        console.error("Bulk embed error for", id, err);
      }
    }
    queryClient.invalidateQueries({ queryKey: ['processedDocs'] });
    setIsBulkRunning(false);
    setSelectedIds([]);
  };

  const handleBulkGraph = async () => {
    setIsBulkRunning(true);
    setBulkMessage('Building Knowledge Graph for selected documents...');
    for (const id of selectedIds) {
      try {
        await buildGraph(id);
      } catch (err) {
        console.error("Bulk graph error for", id, err);
      }
    }
    queryClient.invalidateQueries({ queryKey: ['processedDocs'] });
    setIsBulkRunning(false);
    setSelectedIds([]);
  };

  const handleBulkDelete = async () => {
    if (!window.confirm(`Delete ${selectedIds.length} documents?`)) return;
    setIsBulkRunning(true);
    setBulkMessage('Deleting selected documents...');
    for (const id of selectedIds) {
      try {
        await deleteDocument(id);
      } catch (err) {
        console.error("Bulk delete error for", id, err);
      }
    }
    queryClient.invalidateQueries({ queryKey: ['processedDocs'] });
    queryClient.invalidateQueries({ queryKey: ['systemMetrics'] });
    setIsBulkRunning(false);
    setSelectedIds([]);
  };

  const handleExportCSV = () => {
    const selectedDocs = docs.filter(d => selectedIds.includes(d.document_id));
    if (selectedDocs.length === 0) return;
    
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Document ID,Filename,Size (Bytes),Total Chunks,Status,Embedding Status,Graph Status\n";
    
    selectedDocs.forEach(d => {
      csvContent += `"${d.document_id}","${d.filename}",${d.file_size_bytes || 0},${d.total_chunks || 0},"${d.status}","${d.embedding_status || 'PENDING'}","${d.graph_status || 'PENDING'}"\n`;
    });
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `indusmind_export_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Determine current lifecycle stage
  const getLifecycleStage = (doc) => {
    if (doc.graph_status === 'GRAPH_BUILT' || doc.graph_built) return { label: 'AI Ready', color: 'text-brand-accent bg-brand-accent/10 border-brand-accent/20' };
    if (doc.embedding_status === 'EMBEDDED' || doc.embedded) return { label: 'Embedded', color: 'text-purple-400 bg-purple-500/10 border-purple-500/20' };
    if (doc.total_chunks > 0) return { label: 'Chunked', color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' };
    if (doc.status === 'COMPLETED') return { label: 'Processed', color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' };
    if (doc.status === 'FAILED') return { label: 'Failed', color: 'text-red-400 bg-red-500/10 border-red-500/20' };
    return { label: 'Uploaded', color: 'text-slate-400 bg-slate-500/10 border-slate-500/20' };
  };

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
        <h3 className="text-lg font-semibold flex items-center justify-center"><AlertCircle className="mr-2" /> Connection Error</h3>
        <p className="mt-2">Failed to connect to the backend server. Make sure FastAPI is running.</p>
        <button onClick={() => refetch()} className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors inline-flex items-center">
          <RefreshCw className="w-4 h-4 mr-2" /> Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center"><FileText className="mr-3 text-brand-accent" /> Processed Documents</h1>
          <p className="text-sm text-slate-400 mt-1">Manage documents, generate embeddings, and build the Knowledge Graph.</p>
        </div>
      </div>

      {/* Bulk Operations Toolbar */}
      {selectedIds.length > 0 && (
        <div className="bg-industrial-900/90 border border-brand-accent/30 rounded-xl p-4 flex flex-wrap gap-3 items-center justify-between shadow-lg animate-fade-in">
          <div className="text-sm font-semibold text-slate-200 flex items-center">
            <Check className="w-4 h-4 mr-2 text-brand-accent" /> {selectedIds.length} Selected
          </div>
          <div className="flex gap-2">
            <button 
              onClick={handleBulkEmbed}
              disabled={isBulkRunning}
              className="px-3.5 py-1.5 bg-brand-primary hover:bg-brand-primary/90 text-white font-medium rounded-lg text-xs transition-all inline-flex items-center"
            >
              <Database className="w-3.5 h-3.5 mr-1.5" /> Generate Embeddings
            </button>
            <button 
              onClick={handleBulkGraph}
              disabled={isBulkRunning}
              className="px-3.5 py-1.5 bg-brand-accent hover:bg-brand-accent/90 text-white font-medium rounded-lg text-xs transition-all inline-flex items-center"
            >
              <Hexagon className="w-3.5 h-3.5 mr-1.5" /> Build Graph
            </button>
            <button 
              onClick={handleExportCSV}
              disabled={isBulkRunning}
              className="px-3.5 py-1.5 bg-industrial-800 hover:bg-industrial-700 text-slate-200 font-medium rounded-lg text-xs transition-all inline-flex items-center border border-industrial-700"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 mr-1.5" /> Export CSV
            </button>
            <button 
              onClick={handleBulkDelete}
              disabled={isBulkRunning}
              className="px-3.5 py-1.5 bg-red-950/40 hover:bg-red-950/60 text-red-400 border border-red-900/40 font-medium rounded-lg text-xs transition-all inline-flex items-center"
            >
              <Trash2 className="w-3.5 h-3.5 mr-1.5" /> Delete
            </button>
          </div>
        </div>
      )}

      {/* Bulk Status Indicator */}
      {isBulkRunning && (
        <div className="bg-industrial-900 border border-industrial-800 rounded-xl p-4 flex items-center justify-center space-x-3 shadow-lg">
          <Loader2 className="w-5 h-5 text-brand-accent animate-spin" />
          <span className="text-sm font-medium text-slate-300">{bulkMessage}</span>
        </div>
      )}

      {/* Main Table Panel */}
      <div className="glass-panel overflow-hidden rounded-xl border border-industrial-800">
        <table className="min-w-full divide-y divide-industrial-700 text-left">
          <thead className="bg-industrial-900/80">
            <tr>
              <th className="px-6 py-4 w-4">
                <input 
                  type="checkbox" 
                  checked={selectedIds.length === docs.length && docs.length > 0} 
                  onChange={handleSelectAll}
                  className="rounded border-industrial-700 accent-brand-accent"
                />
              </th>
              <th className="px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">Document Name</th>
              <th className="px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">Size</th>
              <th className="px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">Status Stage</th>
              <th className="px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">Chunks</th>
              <th className="px-6 py-4 text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-industrial-800 bg-industrial-950/30">
            {docs.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center py-10 text-slate-400 italic">No processed documents found.</td>
              </tr>
            ) : docs.map((doc) => {
              const stage = getLifecycleStage(doc);
              const isSelected = selectedIds.includes(doc.document_id);
              
              return (
                <tr key={doc.document_id} className={`hover:bg-industrial-800/40 transition-colors ${isSelected ? 'bg-brand-primary/5' : ''}`}>
                  <td className="px-6 py-4">
                    <input 
                      type="checkbox" 
                      checked={isSelected}
                      onChange={() => handleSelectOne(doc.document_id)}
                      className="rounded border-industrial-700 accent-brand-accent"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link to={`/documents/${doc.document_id}`} className="flex items-center hover:underline group">
                      <FileText className="w-5 h-5 text-brand-primary mr-3 group-hover:text-brand-accent transition-colors" />
                      <span className="text-sm font-medium text-slate-200 group-hover:text-slate-100 transition-colors">{doc.filename || "Unknown"}</span>
                    </Link>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-400">
                    {doc.file_size_bytes ? (doc.file_size_bytes / (1024*1024)).toFixed(2) + " MB" : "N/A"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2.5 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full border ${stage.color}`}>
                      {stage.label}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-400 flex items-center">
                    <Database className="w-3.5 h-3.5 mr-1.5 text-purple-400" />
                    {doc.total_chunks || 0}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-xs font-medium">
                    <div className="flex items-center space-x-3">
                      <Link to={`/documents/${doc.document_id}`} className="text-slate-400 hover:text-white transition-colors" title="View details">
                        <Info className="w-4 h-4" />
                      </Link>
                      
                      {(!doc.total_chunks || doc.total_chunks === 0) && (
                        <button 
                          onClick={() => processMutation.mutate(doc.document_id)}
                          className="text-emerald-400 hover:text-emerald-300 transition-colors"
                          title="Clean and chunk document"
                          disabled={processMutation.isPending}
                        >
                          {processMutation.isPending && processMutation.variables === doc.document_id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <RefreshCw className="w-4 h-4" />
                          )}
                        </button>
                      )}

                      {doc.total_chunks > 0 && !doc.embedded && !doc.embedding_status && (
                        <button 
                          onClick={() => embedMutation.mutate(doc.document_id)}
                          className="text-brand-primary hover:text-brand-accent transition-colors"
                          title="Embed document"
                          disabled={embedMutation.isPending}
                        >
                          {embedMutation.isPending && embedMutation.variables === doc.document_id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Play className="w-4 h-4" />
                          )}
                        </button>
                      )}

                      {doc.total_chunks > 0 && (doc.embedded || doc.embedding_status === 'EMBEDDED') && !doc.graph_built && !doc.graph_status && (
                        <button 
                          onClick={() => graphMutation.mutate(doc.document_id)}
                          className="text-purple-400 hover:text-purple-300 transition-colors"
                          title="Build knowledge graph"
                          disabled={graphMutation.isPending}
                        >
                          {graphMutation.isPending && graphMutation.variables === doc.document_id ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Hexagon className="w-4 h-4" />
                          )}
                        </button>
                      )}
                      
                      <button 
                        onClick={() => {
                          if (window.confirm(`Delete ${doc.filename}?`)) {
                            deleteMutation.mutate(doc.document_id);
                          }
                        }}
                        className="text-red-500 hover:text-red-400 transition-colors"
                        title="Delete document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
