import React, { useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getDocumentDetails, 
  getDocumentText, 
  embedDocument, 
  buildGraph, 
  deleteDocument,
  downloadOriginalPDF 
} from '../services/api';
import { 
  FileText, 
  Database, 
  Hexagon, 
  Download, 
  Trash2, 
  MessageSquare, 
  Sparkles, 
  Clock, 
  ChevronRight, 
  Compass,
  AlertTriangle,
  RefreshCw,
  Layout,
  CheckCircle2,
  FileJson
} from 'lucide-react';

export default function DocumentDetails() {
  const { documentId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('overview');
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Queries
  const { data: detailsData, isLoading: detailsLoading, error: detailsError, refetch: refetchDetails } = useQuery({
    queryKey: ['docDetails', documentId],
    queryFn: () => getDocumentDetails(documentId),
  });

  const { data: textData, isLoading: textLoading } = useQuery({
    queryKey: ['docText', documentId],
    queryFn: () => getDocumentText(documentId),
    enabled: activeTab === 'text',
  });

  const { data: chunksData, isLoading: chunksLoading } = useQuery({
    queryKey: ['docChunks', documentId],
    queryFn: async () => {
      const res = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/chunks`);
      return res.json();
    },
    enabled: activeTab === 'chunks',
  });

  // Mutations
  const embedMutation = useMutation({
    mutationFn: () => embedDocument(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['docDetails', documentId] });
      queryClient.invalidateQueries({ queryKey: ['systemMetrics'] });
      queryClient.invalidateQueries({ queryKey: ['processedDocs'] });
    }
  });

  const graphMutation = useMutation({
    mutationFn: () => buildGraph(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['docDetails', documentId] });
      queryClient.invalidateQueries({ queryKey: ['systemMetrics'] });
      queryClient.invalidateQueries({ queryKey: ['processedDocs'] });
      queryClient.invalidateQueries({ queryKey: ['graphData'] });
    }
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteDocument(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['systemMetrics'] });
      queryClient.invalidateQueries({ queryKey: ['processedDocs'] });
      navigate('/documents');
    }
  });

  if (detailsLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-accent"></div>
      </div>
    );
  }

  if (detailsError || !detailsData?.success) {
    return (
      <div className="p-6 bg-red-900/20 border border-red-500/50 rounded-lg text-red-200 text-center max-w-lg mx-auto mt-10">
        <h3 className="text-lg font-semibold flex items-center justify-center"><AlertTriangle className="mr-2" /> Error Loading Document</h3>
        <p className="mt-2">Failed to retrieve document details from the backend server.</p>
        <button onClick={() => refetchDetails()} className="mt-4 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors inline-flex items-center">
          <RefreshCw className="w-4 h-4 mr-2" /> Retry
        </button>
      </div>
    );
  }

  const doc = detailsData.data || {};
  
  // Calculate lifecycle stages
  const isUploaded = !!doc.document_id;
  const isProcessing = doc.status === 'COMPLETED' || doc.status === 'FAILED';
  const isOcrComplete = doc.ocr_used !== undefined;
  const isChunked = doc.total_chunks > 0;
  const isEmbedded = doc.embedding_status === 'EMBEDDED' || doc.embedded === true;
  const isGraphBuilt = doc.graph_status === 'GRAPH_BUILT' || doc.graph_built === true;
  const isAiReady = isEmbedded && isGraphBuilt;

  const stages = [
    { label: 'Uploaded', completed: isUploaded, desc: 'File archived raw.' },
    { label: 'Processing', completed: isProcessing, desc: 'Cleaned & normalized.' },
    { label: 'OCR Complete', completed: isOcrComplete, desc: 'Text extracted.' },
    { label: 'Chunked', completed: isChunked, desc: `${doc.total_chunks || 0} chunks generated.` },
    { label: 'Embedded', completed: isEmbedded, desc: 'Stored in ChromaDB.' },
    { label: 'Graph Built', completed: isGraphBuilt, desc: 'Mapped to Neo4j.' },
    { label: 'AI Ready', completed: isAiReady, desc: 'Agents verified.' },
  ];

  const handleDownloadText = () => {
    if (!textData?.data?.text) return;
    const element = document.createElement("a");
    const file = new Blob([textData.data.text], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `${doc.filename}_extracted.txt`;
    document.body.appendChild(element);
    element.click();
  };

  const tabs = [
    { id: 'overview', name: 'Overview' },
    { id: 'text', name: 'Extracted Text' },
    { id: 'chunks', name: 'Chunks' },
    { id: 'metadata', name: 'Metadata' }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center space-x-2 text-sm text-slate-400">
        <Link to="/documents" className="hover:text-white transition-colors">Documents</Link>
        <ChevronRight className="w-4 h-4" />
        <span className="text-slate-200 truncate max-w-xs">{doc.filename}</span>
      </div>

      <div className="flex justify-between items-start border-b border-industrial-800 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center">
            <FileText className="mr-3 text-brand-accent w-7 h-7" /> {doc.filename}
          </h1>
          <p className="text-xs text-slate-400 mt-1">ID: {doc.document_id}</p>
        </div>
        <div className="flex space-x-3">
          <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
            doc.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
          }`}>
            {doc.status || 'INGESTING'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main tabs view */}
        <div className="lg:col-span-3 space-y-6">
          <div className="border-b border-industrial-800">
            <nav className="flex space-x-6" aria-label="Tabs">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`border-b-2 py-4 px-1 text-sm font-medium transition-colors ${
                    activeTab === tab.id
                      ? 'border-brand-accent text-brand-accent'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          <div className="glass-panel p-6 rounded-xl">
            {activeTab === 'overview' && (
              <div className="space-y-8">
                <div>
                  <h3 className="text-lg font-semibold text-slate-200 mb-6 flex items-center">
                    <Clock className="w-5 h-5 mr-2 text-brand-accent" /> Document Lifecycle Progress
                  </h3>
                  {/* Vertical Timeline */}
                  <div className="relative pl-8 border-l border-industrial-800 space-y-6">
                    {stages.map((stage, idx) => (
                      <div key={idx} className="relative">
                        {/* Dot */}
                        <div className={`absolute -left-[41px] top-1 w-6 h-6 rounded-full flex items-center justify-center border ${
                          stage.completed 
                            ? 'bg-emerald-950 border-emerald-500 text-emerald-400' 
                            : 'bg-industrial-900 border-industrial-700 text-slate-500'
                        }`}>
                          {stage.completed ? <CheckCircle2 className="w-4 h-4" /> : <div className="w-2 h-2 rounded-full bg-slate-500" />}
                        </div>
                        <div>
                          <h4 className={`text-sm font-semibold ${stage.completed ? 'text-slate-100' : 'text-slate-500'}`}>{stage.label}</h4>
                          <p className="text-xs text-slate-400 mt-0.5">{stage.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'text' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-md font-semibold text-slate-200">Extracted UTF-8 Plaintext</h3>
                  <button 
                    onClick={handleDownloadText} 
                    disabled={textLoading || !textData?.data?.text}
                    className="px-3 py-1.5 bg-industrial-800 hover:bg-industrial-700 disabled:opacity-50 text-slate-200 font-medium rounded-lg text-xs transition-colors inline-flex items-center"
                  >
                    <Download className="w-3.5 h-3.5 mr-1.5" /> Download TXT
                  </button>
                </div>
                {textLoading ? (
                  <div className="text-slate-400 py-10 text-center text-sm">Loading plain text...</div>
                ) : (
                  <pre className="bg-industrial-950 border border-industrial-800 rounded-lg p-4 font-mono text-xs text-slate-300 leading-relaxed overflow-x-auto whitespace-pre-wrap max-h-[500px]">
                    {textData?.data?.text || 'No text extracted.'}
                  </pre>
                )}
              </div>
            )}

            {activeTab === 'chunks' && (
              <div className="space-y-4">
                <h3 className="text-md font-semibold text-slate-200">Processed Document Chunks</h3>
                {chunksLoading ? (
                  <div className="text-slate-400 py-10 text-center text-sm">Loading chunks...</div>
                ) : !chunksData?.data || chunksData.data.length === 0 ? (
                  <div className="text-slate-400 py-10 text-center text-sm">No chunks processed yet.</div>
                ) : (
                  <div className="space-y-4">
                    {chunksData.data.map((chunk, idx) => (
                      <div key={idx} className="bg-industrial-950/50 border border-industrial-800 rounded-lg p-5 space-y-3">
                        <div className="flex justify-between items-center text-xs text-slate-400 border-b border-industrial-800 pb-2">
                          <div className="flex items-center space-x-4">
                            <span>Chunk ID: <span className="font-mono text-slate-300">{chunk.chunk_id}</span></span>
                            <span>Number: <span className="font-semibold text-slate-300">{chunk.chunk_number}</span></span>
                          </div>
                          <div className="flex items-center space-x-3">
                            <span>Chars: {chunk.character_count || chunk.content.length}</span>
                            <span>Words: {chunk.content.split(' ').length}</span>
                          </div>
                        </div>
                        <p className="text-xs text-slate-200 leading-relaxed font-mono whitespace-pre-wrap">{chunk.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'metadata' && (
              <div className="space-y-4">
                <h3 className="text-md font-semibold text-slate-200">Full Raw Document Metadata</h3>
                <div className="border border-industrial-800 rounded-lg overflow-hidden">
                  <table className="min-w-full divide-y divide-industrial-800 text-xs">
                    <tbody className="divide-y divide-industrial-800 bg-industrial-950/20">
                      {Object.entries(doc).map(([key, val]) => (
                        <tr key={key}>
                          <td className="px-5 py-3 font-semibold text-slate-400 bg-industrial-950/50 w-1/3">{key}</td>
                          <td className="px-5 py-3 font-mono text-slate-200 break-all">{typeof val === 'object' ? JSON.stringify(val) : String(val)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions Panel */}
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-xl space-y-4">
            <h3 className="text-md font-semibold text-slate-200 flex items-center border-b border-industrial-800 pb-2">
              <Compass className="w-5 h-5 mr-2 text-brand-primary" /> Quick Actions
            </h3>
            
            <button 
              onClick={() => embedMutation.mutate()}
              disabled={embedMutation.isPending || isEmbedded}
              className="w-full px-4 py-2.5 bg-brand-primary hover:bg-brand-primary/90 text-white font-medium rounded-lg text-sm transition-colors inline-flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {embedMutation.isPending ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Database className="w-4 h-4 mr-2" />}
              {isEmbedded ? 'Embeddings Generated' : 'Generate Embeddings'}
            </button>

            <button 
              onClick={() => graphMutation.mutate()}
              disabled={graphMutation.isPending || isGraphBuilt || !isEmbedded}
              className="w-full px-4 py-2.5 bg-brand-accent hover:bg-brand-accent/90 text-white font-medium rounded-lg text-sm transition-colors inline-flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {graphMutation.isPending ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Hexagon className="w-4 h-4 mr-2" />}
              {isGraphBuilt ? 'Graph Built' : 'Build Knowledge Graph'}
            </button>

            <Link 
              to={`/chat?doc_filter=${documentId}`}
              className="w-full px-4 py-2.5 bg-industrial-800 hover:bg-industrial-700 text-slate-200 font-medium rounded-lg text-sm transition-colors inline-flex items-center justify-center border border-industrial-700"
            >
              <MessageSquare className="w-4 h-4 mr-2 text-brand-accent" /> Ask AI About Document
            </Link>

            <a 
              href={downloadOriginalPDF(documentId)}
              target="_blank"
              rel="noreferrer"
              className="w-full px-4 py-2.5 bg-industrial-800 hover:bg-industrial-700 text-slate-200 font-medium rounded-lg text-sm transition-colors inline-flex items-center justify-center border border-industrial-700"
            >
              <Download className="w-4 h-4 mr-2 text-slate-400" /> Download PDF
            </a>

            <button 
              onClick={() => setShowDeleteModal(true)}
              className="w-full px-4 py-2.5 bg-red-950/20 hover:bg-red-950/40 text-red-400 border border-red-900/50 font-medium rounded-lg text-sm transition-colors inline-flex items-center justify-center"
            >
              <Trash2 className="w-4 h-4 mr-2" /> Delete Document
            </button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-industrial-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass-panel max-w-md w-full rounded-xl border border-industrial-700 shadow-2xl p-6 bg-industrial-900/95 space-y-4">
            <h3 className="text-lg font-semibold text-red-400 flex items-center"><Trash2 className="mr-2" /> Delete Document?</h3>
            <p className="text-sm text-slate-300">
              Are you sure you want to permanently delete **{doc.filename}**? This will delete the raw file, chunks, embeddings, and Neo4j graph nodes.
            </p>
            <div className="flex justify-end space-x-3 pt-2">
              <button 
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 bg-industrial-800 hover:bg-industrial-700 text-slate-200 font-medium rounded-lg text-xs transition-colors"
              >
                Cancel
              </button>
              <button 
                onClick={() => {
                  deleteMutation.mutate();
                  setShowDeleteModal(false);
                }}
                disabled={deleteMutation.isPending}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-medium rounded-lg text-xs transition-colors disabled:opacity-50"
              >
                {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
