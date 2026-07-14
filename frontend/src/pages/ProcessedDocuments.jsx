import React from 'react';
import { FileText, Database, Share2, Hexagon } from 'lucide-react';

export default function ProcessedDocuments() {
  const docs = [
    { id: '1', name: 'sample_manual.pdf', size: '1.3 MB', status: 'Completed', chunks: 14, date: '2026-07-14' }
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><FileText className="mr-3 text-brand-accent" /> Processed Documents</h1>
        <p className="text-sm text-slate-400 mt-1">Manage documents ingested into the knowledge base.</p>
      </div>

      <div className="glass-panel overflow-hidden rounded-xl border border-industrial-800">
        <table className="min-w-full divide-y divide-industrial-700">
          <thead className="bg-industrial-900/80">
            <tr>
              <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Document Name</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Size</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Status</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Chunks</th>
              <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">Date Ingested</th>
              <th className="px-6 py-4 text-right text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-industrial-800 bg-industrial-950/30">
            {docs.map((doc) => (
              <tr key={doc.id} className="hover:bg-industrial-800/50 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <FileText className="w-5 h-5 text-brand-primary mr-3" />
                    <span className="text-sm font-medium text-slate-200">{doc.name}</span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{doc.size}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {doc.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400 flex items-center">
                  <Database className="w-4 h-4 mr-2 text-purple-400" />
                  {doc.chunks}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{doc.date}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button className="text-brand-accent hover:text-brand-primary ml-4" title="View Graph"><Hexagon className="w-5 h-5 inline" /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
