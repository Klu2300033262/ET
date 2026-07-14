import React, { useState } from 'react';
import { Search, SlidersHorizontal, BookOpen } from 'lucide-react';
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

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Semantic Search</h1>
        <p className="text-sm text-slate-400 mt-1">Directly query the vector database for highly relevant chunks.</p>
      </div>

      <div className="glass-panel p-6 rounded-xl space-y-4">
        <form onSubmit={handleSearch} className="flex space-x-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input 
              type="text" 
              placeholder="Enter search query..." 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full bg-industrial-800 border border-industrial-700 rounded-lg py-2.5 pl-10 pr-4 text-slate-200 focus:border-brand-primary focus:ring-1 focus:ring-brand-primary transition-all"
            />
          </div>
          <button 
            type="submit" 
            disabled={searchMutation.isPending || !query.trim()}
            className="px-6 py-2.5 bg-brand-primary hover:bg-brand-primary/90 text-white font-medium rounded-lg disabled:opacity-50"
          >
            {searchMutation.isPending ? 'Searching...' : 'Search Vectors'}
          </button>
        </form>

        <div className="flex items-center space-x-4 text-sm text-slate-400">
          <SlidersHorizontal className="w-4 h-4" />
          <span>Similarity Threshold: {threshold}</span>
          <input 
            type="range" min="0.1" max="0.9" step="0.1" 
            value={threshold} onChange={(e) => setThreshold(parseFloat(e.target.value))}
            className="w-32 accent-brand-accent"
          />
        </div>
      </div>

      {searchMutation.data && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-200">
            Retrieved {searchMutation.data.length} Chunks
          </h3>
          <div className="grid gap-4">
            {searchMutation.data.map((chunk, idx) => (
              <div key={idx} className="glass-panel p-5 rounded-lg border-l-4 border-brand-accent space-y-3">
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-2 text-sm text-slate-400">
                    <BookOpen className="w-4 h-4" />
                    <span>{chunk.metadata.source_document || chunk.metadata.document_id}</span>
                  </div>
                  <span className="text-xs font-semibold px-2 py-1 bg-industrial-800 rounded text-brand-accent">
                    Score: {chunk.similarity_score.toFixed(3)}
                  </span>
                </div>
                <p className="text-slate-200 text-sm leading-relaxed">{chunk.content}</p>
              </div>
            ))}
            {searchMutation.data.length === 0 && (
              <p className="text-slate-400 italic">No matching vectors found.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
