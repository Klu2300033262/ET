import React from 'react';
import { ShieldAlert, Info } from 'lucide-react';

export default function ComplianceIntelligence() {
  const rules = [
    { target: 'Pump P-101', rule: 'Operators must wear PPE at all times when servicing. Warning: High pressure system.' }
  ];

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-slate-100 flex items-center"><ShieldAlert className="mr-3 text-red-500" /> Compliance Intelligence</h1>
        <p className="text-sm text-slate-400 mt-1">Regulatory safety requirements and hazards extracted from documents.</p>
      </div>

      <div className="grid gap-6">
        {rules.map((r, idx) => (
          <div key={idx} className="glass-panel p-6 rounded-xl border-l-4 border-red-500 space-y-3">
            <h3 className="text-lg font-semibold text-red-400 flex items-center">
              Hazard / Safety Rule for {r.target}
            </h3>
            <div className="bg-red-500/10 p-4 rounded-lg border border-red-500/20 flex items-start space-x-3">
              <Info className="w-5 h-5 text-red-400 mt-0.5" />
              <p className="text-sm text-red-200">{r.rule}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
