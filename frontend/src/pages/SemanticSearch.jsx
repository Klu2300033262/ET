import React, { useState } from 'react';
import { Search, SlidersHorizontal, BookOpen, AlertCircle, RefreshCw, Loader2, Database } from 'lucide-react';
import { semanticSearch } from '../services/api';
import { useMutation } from '@tanstack/react-query';

export default function SemanticSearch() {
  const [query, setQuery] = useState('');
  const [threshold, setThreshold] = useState(0.3);
  
  const searchMutation = useMutation({
    mutationFn: () => semanticSearch(query, 5, threshold),
  });

  const handleSearch = (e) => {
    e.preventDefault();
    if (query.trim()) searchMutation.mutate();
  };

  // Safe normalization of results from various backend configurations
  const rawData = searchMutation.data;
  const results = rawData?.results || rawData?.data?.results || rawData?.data || [];
  const searchTime = rawData?.execution_time_ms || rawData?.data?.execution_time_ms || 0;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><Search className="mr-3 text-brand-accent" /> Semantic Search</h1>
        <p className="text-sm text-slate-400 mt-1">Query the vector database to retrieve semantic content chunks.</p>
      </div>

      {/* Query Bar */}
      <div className="glass-panel p-6 rounded-xl space-y-4">
        <form onSubmit={handleSearch} className="flex space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
            <input 
              type="text" 
              placeholder="Enter search query (e.g. Pump failure root cause)..." 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full bg-industrial-950 border border-industrial-800 focus:border-brand-primary/50 text-slate-200 rounded-lg py-2.5 pl-10 pr-4 focus:outline-none focus:ring-1 focus:ring-brand-primary/55 transition-all text-sm"
              disabled={searchMutation.isPending}
            />
          </div>
          <button 
            type="submit" 
            disabled={searchMutation.isPending || !query.trim()}
            className="px-6 py-2.5 bg-brand-primary hover:bg-brand-primary/95 text-white font-medium rounded-lg text-sm transition-colors disabled:opacity-50 inline-flex items-center"
          >
            {searchMutation.isPending && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
            {searchMutation.isPending ? 'Searching...' : 'Search Vectors'}
          </button>
        </form>

        <div className="flex items-center space-x-4 text-xs text-slate-400">
          <SlidersHorizontal className="w-4 h-4 text-slate-500" />
          <span className="font-semibold uppercase">Similarity Threshold: {threshold}</span>
          <input 
            type="range" min="0.1" max="0.9" step="0.05" 
            value={threshold} onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-32 accent-brand-accent"
          />
        </div>
      </div>

      {/* Error state */}
      {searchMutation.isError && (
        <div className="p-5 bg-red-950/20 border border-red-500/40 rounded-xl text-red-200 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <div>
              <h4 className="font-semibold">Search Execution Failed</h4>
              <p className="text-xs text-slate-400 mt-0.5">{searchMutation.error?.message || 'Check connection to ChromaDB.'}</p>
            </div>
          </div>
          <button 
            onClick={() => searchMutation.mutate()} 
            className="px-3.5 py-1.5 bg-red-800 hover:bg-red-700 text-white rounded-lg text-xs transition-colors flex items-center"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Retry
          </button>
        </div>
      )}

      {/* Results or Loading / Empty States */}
      {searchMutation.isPending && (
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="glass-panel p-5 rounded-lg border-l-4 border-slate-700 animate-pulse space-y-3">
              <div className="h-4 bg-industrial-800 rounded w-1/3"></div>
              <div className="h-3 bg-industrial-800 rounded w-full"></div>
              <div className="h-3 bg-industrial-800 rounded w-5/6"></div>
            </div>
          ))}
        </div>
      )}

      {!searchMutation.isPending && searchMutation.isSuccess && (
        <div className="space-y-4">
          <div className="flex justify-between items-center text-xs text-slate-400">
            <span>Retrieved {results.length} Chunks</span>
            {searchTime > 0 && <span>Query completed in {searchTime}ms</span>}
          </div>

          {results.length === 0 ? (
            <div className="glass-panel p-10 rounded-xl text-center text-slate-400 italic text-sm">
              No matching semantic vectors found above the {threshold} similarity threshold.
            </div>
          ) : (
            <div className="space-y-4">
              {results.map((chunk, idx) => (
                <div key={idx} className="glass-panel p-5 rounded-xl border-l-4 border-brand-accent space-y-3">
                  <div className="flex justify-between items-start">
                    <div className="flex items-center space-x-2 text-xs text-slate-400">
                      <BookOpen className="w-3.5 h-3.5 text-brand-primary" />
                      <span className="font-semibold text-slate-300">{chunk.metadata?.source_document || chunk.metadata?.document_id || 'Unknown Document'}</span>
                      {chunk.metadata?.chunk_id && (
                        <>
                          <span>•</span>
                          <span>Chunk ID: <span className="font-mono text-slate-400">{chunk.metadata.chunk_id}</span></span>
                        </>
                      )}
                    </div>
                    <span className="text-xs font-semibold px-2 py-0.5 bg-industrial-950 border border-brand-accent/30 rounded text-brand-accent">
                      Score: {(chunk.score || chunk.similarity_score || 0).toFixed(4)}
                    </span>
                  </div>
                  <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap font-mono bg-industrial-950/40 p-3 rounded border border-industrial-850">{chunk.content || chunk.text || 'No content'}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
