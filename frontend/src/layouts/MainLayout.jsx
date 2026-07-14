import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Upload, 
  FileText, 
  Search, 
  MessageSquare, 
  Network, 
  Wrench, 
  ShieldAlert, 
  BarChart2, 
  Activity 
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Document Upload', href: '/upload', icon: Upload },
  { name: 'Processed Documents', href: '/documents', icon: FileText },
  { name: 'Semantic Search', href: '/search', icon: Search },
  { name: 'AI Assistant', href: '/chat', icon: MessageSquare },
  { name: 'Knowledge Graph', href: '/graph', icon: Network },
  { name: 'Maintenance Insights', href: '/maintenance', icon: Wrench },
  { name: 'Compliance Insights', href: '/compliance', icon: ShieldAlert },
  { name: 'Analytics', href: '/analytics', icon: BarChart2 },
  { name: 'System Status', href: '/status', icon: Activity },
];

export default function MainLayout({ children }) {
  return (
    <div className="flex h-screen bg-industrial-950 text-slate-100 font-sans">
      {/* Sidebar */}
      <div className="w-64 flex-shrink-0 bg-industrial-900 border-r border-industrial-800 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-industrial-800">
          <h1 className="text-xl font-bold text-brand-accent tracking-wide uppercase">IndusMind AI</h1>
        </div>
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center px-3 py-2.5 text-sm font-medium rounded-md transition-colors ${
                  isActive
                    ? 'bg-brand-primary/20 text-brand-accent'
                    : 'text-slate-400 hover:bg-industrial-800 hover:text-slate-200'
                }`
              }
            >
              <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navigation / Status Bar */}
        <header className="h-16 flex-shrink-0 bg-industrial-900/50 backdrop-blur border-b border-industrial-800 flex items-center justify-between px-6">
          <h2 className="text-lg font-semibold tracking-tight text-slate-200">Industrial Knowledge Intelligence Platform</h2>
          <div className="flex items-center space-x-4">
            <span className="flex items-center text-sm text-slate-400">
              <span className="w-2 h-2 rounded-full bg-green-500 mr-2 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span>
              System Online
            </span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6 scroll-smooth">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
