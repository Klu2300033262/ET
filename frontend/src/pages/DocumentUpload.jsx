import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, Loader2, AlertCircle } from 'lucide-react';
import { uploadDocument, processDocument, embedDocument, buildGraph } from '../services/api';

export default function DocumentUpload() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState('idle'); // idle, uploading, processing, embedding, graphing, complete, error
  const [errorMsg, setErrorMsg] = useState('');
  const [docId, setDocId] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setStatus('idle');
      setErrorMsg('');
      setDocId(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'image/*': ['.png', '.jpg', '.jpeg'], 'text/plain': ['.txt'] },
    multiple: false
  });

  const handleUploadPipeline = async () => {
    if (!file) return;
    try {
      setStatus('uploading');
      const uploadRes = await uploadDocument(file);
      const id = uploadRes.data.document_id;
      setDocId(id);

      setStatus('processing');
      await processDocument(id);

      setStatus('embedding');
      await embedDocument(id);

      setStatus('graphing');
      await buildGraph(id);

      setStatus('complete');
    } catch (err) {
      console.error(err);
      setStatus('error');
      setErrorMsg(err.response?.data?.detail || err.message || 'An unknown error occurred.');
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Document Ingestion Pipeline</h1>
        <p className="text-sm text-slate-400 mt-1">Upload technical manuals, P&ID diagrams, and maintenance logs.</p>
      </div>

      {/* Drag & Drop Zone */}
      <div 
        {...getRootProps()} 
        className={`glass-panel border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200
          ${isDragActive ? 'border-brand-primary bg-brand-primary/10' : 'border-industrial-700 hover:border-brand-accent/50'}`}
      >
        <input {...getInputProps()} />
        <div className="mx-auto w-16 h-16 rounded-full bg-industrial-800 flex items-center justify-center mb-4">
          <Upload className={`w-8 h-8 ${isDragActive ? 'text-brand-primary' : 'text-slate-400'}`} />
        </div>
        <p className="text-lg font-medium text-slate-200">
          {isDragActive ? 'Drop the file here' : 'Drag & drop your industrial document'}
        </p>
        <p className="text-sm text-slate-400 mt-2">Supports PDF, PNG, JPG, and TXT (Max 50MB)</p>
      </div>

      {/* Selected File & Trigger */}
      {file && status === 'idle' && (
        <div className="glass-panel p-4 rounded-lg flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FileText className="w-6 h-6 text-brand-accent" />
            <div>
              <p className="text-sm font-medium text-slate-200">{file.name}</p>
              <p className="text-xs text-slate-400">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          </div>
          <button 
            onClick={handleUploadPipeline}
            className="px-4 py-2 bg-brand-primary hover:bg-brand-primary/90 text-white text-sm font-medium rounded-md shadow-lg transition-colors"
          >
            Start Pipeline
          </button>
        </div>
      )}

      {/* Pipeline Status Tracking */}
      {status !== 'idle' && (
        <div className="glass-panel p-6 rounded-xl space-y-4">
          <h3 className="text-lg font-semibold text-slate-200 mb-4">Processing Pipeline</h3>
          
          <PipelineStep label="1. Uploading Document" isActive={status === 'uploading'} isDone={['processing', 'embedding', 'graphing', 'complete'].includes(status)} />
          <PipelineStep label="2. OCR & Text Extraction" isActive={status === 'processing'} isDone={['embedding', 'graphing', 'complete'].includes(status)} />
          <PipelineStep label="3. Vector Embedding (ChromaDB)" isActive={status === 'embedding'} isDone={['graphing', 'complete'].includes(status)} />
          <PipelineStep label="4. Knowledge Graph Construction (Neo4j)" isActive={status === 'graphing'} isDone={status === 'complete'} />
          
          {status === 'complete' && (
            <div className="mt-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg flex items-start space-x-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-green-300">Pipeline Completed Successfully</p>
                <p className="text-xs text-green-400/80 mt-1">Document ID: {docId}</p>
              </div>
            </div>
          )}

          {status === 'error' && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-300">Pipeline Failed</p>
                <p className="text-xs text-red-400/80 mt-1">{errorMsg}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function PipelineStep({ label, isActive, isDone }) {
  return (
    <div className={`flex items-center space-x-3 ${isActive ? 'text-brand-accent' : isDone ? 'text-slate-200' : 'text-slate-600'}`}>
      {isDone ? (
        <CheckCircle className="w-5 h-5 text-green-500" />
      ) : isActive ? (
        <Loader2 className="w-5 h-5 animate-spin" />
      ) : (
        <div className="w-5 h-5 rounded-full border-2 border-slate-700"></div>
      )}
      <span className={`text-sm ${isActive ? 'font-semibold' : 'font-medium'}`}>{label}</span>
    </div>
  );
}
