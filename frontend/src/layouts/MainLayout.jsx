import React, { useState } from 'react';
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
  Activity,
  Menu,
  X
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
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-industrial-950 text-slate-100 font-sans overflow-hidden">
      {/* Desktop Sidebar (visible on md screens and up) */}
      <div className="hidden md:flex w-64 flex-shrink-0 bg-industrial-900 border-r border-industrial-800 flex-col">
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

      {/* Mobile Sidebar / Drawer (visible on mobile only when open) */}
      {isSidebarOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          {/* Backdrop overlay */}
          <div 
            className="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity duration-300" 
            onClick={() => setIsSidebarOpen(false)}
          />
          
          {/* Drawer content */}
          <div className="relative flex w-full max-w-xs flex-1 flex-col bg-industrial-900 border-r border-industrial-800 pt-5 pb-4">
            <div className="absolute top-2 right-2">
              <button
                type="button"
                className="flex h-10 w-10 items-center justify-center rounded-full text-slate-400 hover:text-slate-200 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-brand-accent"
                onClick={() => setIsSidebarOpen(false)}
              >
                <span className="sr-only">Close sidebar</span>
                <X className="h-6 w-6" aria-hidden="true" />
              </button>
            </div>
            
            <div className="flex flex-shrink-0 items-center px-6">
              <h1 className="text-xl font-bold text-brand-accent tracking-wide uppercase">IndusMind AI</h1>
            </div>
            
            <nav className="mt-5 flex-1 h-0 overflow-y-auto px-3 space-y-1">
              {navigation.map((item) => (
                <NavLink
                  key={item.name}
                  to={item.href}
                  onClick={() => setIsSidebarOpen(false)}
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
        </div>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navigation / Status Bar */}
        <header className="h-16 flex-shrink-0 bg-industrial-900/50 backdrop-blur border-b border-industrial-800 flex items-center justify-between px-4 sm:px-6">
          <div className="flex items-center">
            {/* Hamburger button on mobile */}
            <button 
              onClick={() => setIsSidebarOpen(true)}
              className="md:hidden p-2 rounded-md text-slate-400 hover:text-slate-200 hover:bg-industrial-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-brand-accent mr-3"
            >
              <Menu className="h-6 w-6" />
            </button>
            <h2 className="text-sm sm:text-lg font-semibold tracking-tight text-slate-200 truncate max-w-[200px] xs:max-w-xs sm:max-w-md md:max-w-lg lg:max-w-2xl">
              <span className="hidden xs:inline">Industrial Knowledge Intelligence Platform</span>
              <span className="xs:hidden">IndusMind AI</span>
            </h2>
          </div>
          <div className="flex items-center space-x-4">
            <span className="flex items-center text-xs sm:text-sm text-slate-400">
              <span className="w-2 h-2 rounded-full bg-green-500 mr-2 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span>
              Online
            </span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 scroll-smooth">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
