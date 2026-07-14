import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BarChart2 } from 'lucide-react';

export default function Analytics() {
  const data = [
    { name: 'Jan', documents: 12, chunks: 450 },
    { name: 'Feb', documents: 19, chunks: 800 },
    { name: 'Mar', documents: 25, chunks: 1100 },
    { name: 'Apr', documents: 32, chunks: 1450 },
    { name: 'May', documents: 40, chunks: 1900 },
    { name: 'Jun', documents: 55, chunks: 2600 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><BarChart2 className="mr-3 text-brand-accent" /> Analytics</h1>
        <p className="text-sm text-slate-400 mt-1">System usage and intelligence growth over time.</p>
      </div>

      <div className="glass-panel p-6 rounded-xl">
        <h3 className="text-lg font-semibold text-slate-200 mb-6">Knowledge Base Growth</h3>
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" />
              <YAxis yAxisId="left" stroke="#0ea5e9" />
              <YAxis yAxisId="right" orientation="right" stroke="#8b5cf6" />
              <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }} />
              <Bar yAxisId="left" dataKey="documents" fill="#0ea5e9" radius={[4, 4, 0, 0]} name="Documents" />
              <Bar yAxisId="right" dataKey="chunks" fill="#8b5cf6" radius={[4, 4, 0, 0]} name="Vector Chunks" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
