import React from 'react';
import { Wrench, AlertTriangle, PenTool } from 'lucide-react';

export default function MaintenanceIntelligence() {
  const issues = [
    { equip: 'Pump P-101', issue: 'Bearing Overheat', date: '2024-05-12', action: 'Bearing replaced. Routine inspection set to 6 months.' }
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><Wrench className="mr-3 text-brand-accent" /> Maintenance Intelligence</h1>
        <p className="text-sm text-slate-400 mt-1">Aggregated historical failure data and predictive root cause analysis.</p>
      </div>

      <div className="grid gap-6">
        {issues.map((issue, idx) => (
          <div key={idx} className="glass-panel p-6 rounded-xl border-l-4 border-amber-500 space-y-4">
            <div className="flex justify-between items-start">
              <h3 className="text-lg font-semibold text-amber-400 flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" /> {issue.equip}: {issue.issue}
              </h3>
              <span className="text-sm text-slate-400">{issue.date}</span>
            </div>
            <div className="bg-industrial-950 p-4 rounded-lg border border-industrial-800 flex items-start space-x-3">
              <PenTool className="w-5 h-5 text-slate-400 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-slate-200">Resolution & RCA</p>
                <p className="text-sm text-slate-400 mt-1">{issue.action}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
