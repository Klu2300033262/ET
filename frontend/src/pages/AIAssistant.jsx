import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { chatWithAgents } from '../services/api';
import { 
  Send, 
  Bot, 
  User, 
  Clock, 
  Activity, 
  CheckCircle2, 
  Trash2, 
  Copy, 
  Download, 
  HelpCircle,
  ChevronDown,
  ChevronUp,
  FileText,
  Hexagon,
  FileJson,
  Plus
} from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

export default function AIAssistant() {
  const [session, setSession] = useState(uuidv4());
  const [history, setHistory] = useState([
    { id: session, title: 'New Conversation' }
  ]);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello. I am IndusMind AI. You can ask me about maintenance history, compliance rules, or equipment topologies. How can I assist you today?',
    }
  ]);
  const [input, setInput] = useState('');
  const [expandedSection, setExpandedSection] = useState({});

  const toggleSection = (msgIdx, section) => {
    const key = `${msgIdx}-${section}`;
    setExpandedSection(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const isSectionExpanded = (msgIdx, section) => {
    return !!expandedSection[`${msgIdx}-${section}`];
  };

  const chatMutation = useMutation({
    queryKey: ['chatWithAgents'],
    mutationFn: (q) => chatWithAgents(q, session),
    onSuccess: (res) => {
      // Invalidate system metrics to update AI request counter
      setMessages((prev) => [
        ...prev,
        { 
          role: 'assistant', 
          content: res.answer || res.response || 'No answer found.', 
          meta: res 
        }
      ]);
    },
    onError: (err) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Failed to communicate with LangGraph. Neo4j or Gemini API might be offline.', isError: true }
      ]);
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || chatMutation.isPending) return;
    
    const queryText = input.trim();
    setMessages((prev) => [...prev, { role: 'user', content: queryText }]);
    chatMutation.mutate(queryText);
    setInput('');

    // Update conversation title if first user message
    if (messages.length === 1) {
      setHistory(prev => prev.map(h => h.id === session ? { ...h, title: queryText.slice(0, 24) + '...' } : h));
    }
  };

  const handleSuggestedQuestion = (question) => {
    setInput(question);
  };

  const handleNewChat = () => {
    const newSession = uuidv4();
    setSession(newSession);
    setHistory(prev => [{ id: newSession, title: 'New Conversation' }, ...prev]);
    setMessages([
      {
        role: 'assistant',
        content: 'Hello. I am IndusMind AI. You can ask me about maintenance history, compliance rules, or equipment topologies. How can I assist you today?',
      }
    ]);
  };

  const handleClearHistory = () => {
    setHistory([{ id: session, title: 'New Conversation' }]);
    setMessages([
      {
        role: 'assistant',
        content: 'Hello. I am IndusMind AI. You can ask me about maintenance history, compliance rules, or equipment topologies. How can I assist you today?',
      }
    ]);
  };

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
    alert('Answer copied to clipboard!');
  };

  const handleExportJSON = (msg) => {
    const element = document.createElement("a");
    const file = new Blob([JSON.stringify(msg.meta || msg, null, 2)], {type: 'application/json'});
    element.href = URL.createObjectURL(file);
    element.download = `indusmind_ai_chat_${Date.now()}.json`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleExportTXT = (msg) => {
    const element = document.createElement("a");
    const content = `User Query: ${messages.find(m => m.role === 'user')?.content || ''}\n\nAI Answer:\n${msg.content}`;
    const file = new Blob([content], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `indusmind_ai_chat_${Date.now()}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const suggestedQuestions = [
    "What is the recommended maintenance procedure for Pump P-101?",
    "Are there any critical compliance warnings for Valve A-12?",
    "Show the safety procedure for boiler maintenance.",
  ];

  return (
    <div className="flex gap-6 h-[calc(100vh-8rem)] max-w-7xl mx-auto">
      {/* Sidebar - History */}
      <div className="w-64 glass-panel rounded-xl p-4 flex flex-col justify-between hidden md:flex">
        <div className="space-y-4 overflow-y-auto">
          <button 
            onClick={handleNewChat}
            className="w-full py-2 bg-brand-primary hover:bg-brand-primary/95 text-white font-medium rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>New Chat</span>
          </button>
          
          <div className="space-y-2">
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Conversations</h3>
            <div className="space-y-1">
              {history.map((h) => (
                <div 
                  key={h.id} 
                  className={`px-3 py-2 rounded-lg text-xs font-medium cursor-pointer transition-colors truncate ${
                    h.id === session ? 'bg-industrial-800 text-brand-accent' : 'text-slate-400 hover:bg-industrial-800/40 hover:text-slate-200'
                  }`}
                >
                  {h.title}
                </div>
              ))}
            </div>
          </div>
        </div>

        <button 
          onClick={handleClearHistory}
          className="w-full py-2 bg-red-950/20 hover:bg-red-950/40 text-red-400 border border-red-900/50 font-medium rounded-lg text-xs flex items-center justify-center space-x-1.5 transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear Chat History</span>
        </button>
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col h-full bg-industrial-900/40 border border-industrial-800 rounded-xl p-5 overflow-hidden">
        <div className="flex-1 overflow-y-auto pr-2 space-y-6 pb-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`flex max-w-[90%] space-x-3 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className="flex-shrink-0">
                  {msg.role === 'user' ? (
                    <div className="w-9 h-9 rounded-full bg-brand-primary flex items-center justify-center shadow-lg">
                      <User className="w-4 h-4 text-white" />
                    </div>
                  ) : (
                    <div className="w-9 h-9 rounded-full bg-industrial-800 border border-brand-accent/50 flex items-center justify-center">
                      <Bot className="w-4 h-4 text-brand-accent" />
                    </div>
                  )}
                </div>

                <div className={`p-4 rounded-xl relative ${
                  msg.role === 'user' 
                    ? 'bg-brand-primary text-white rounded-tr-none' 
                    : msg.isError 
                      ? 'bg-red-950/30 border border-red-900/50 text-red-200 rounded-tl-none' 
                      : 'bg-industrial-950/50 border border-industrial-800 text-slate-200 rounded-tl-none'
                }`}>
                  <p className="whitespace-pre-wrap leading-relaxed text-sm font-sans">{msg.content}</p>

                  {/* Actions for Assistant Bubble */}
                  {msg.role === 'assistant' && !msg.isError && (
                    <div className="flex items-center space-x-2 mt-3 pt-2 border-t border-industrial-800 text-xs text-slate-400">
                      <button onClick={() => handleCopy(msg.content)} className="hover:text-slate-200 transition-colors inline-flex items-center space-x-1">
                        <Copy className="w-3.5 h-3.5" />
                        <span>Copy</span>
                      </button>
                      <span>•</span>
                      <button onClick={() => handleExportJSON(msg)} className="hover:text-slate-200 transition-colors inline-flex items-center space-x-1">
                        <Download className="w-3.5 h-3.5" />
                        <span>Export JSON</span>
                      </button>
                      <span>•</span>
                      <button onClick={() => handleExportTXT(msg)} className="hover:text-slate-200 transition-colors inline-flex items-center space-x-1">
                        <FileText className="w-3.5 h-3.5" />
                        <span>Export TXT</span>
                      </button>
                    </div>
                  )}

                  {/* Explanatory telemetry */}
                  {msg.meta && (
                    <div className="mt-4 pt-3 border-t border-industrial-800 space-y-3">
                      {/* Telemetry Row */}
                      <div className="flex flex-wrap gap-2 text-xs">
                        <div className="flex items-center text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          <CheckCircle2 className="w-3 h-3 mr-1" />
                          Confidence: {msg.meta.confidence ? `${(msg.meta.confidence * 100).toFixed(0)}%` : 'N/A'}
                        </div>
                        <div className="flex items-center text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20">
                          <Clock className="w-3 h-3 mr-1" />
                          Time: {msg.meta.execution_time_ms}ms
                        </div>
                      </div>

                      {/* Sources Accordion */}
                      {msg.meta.sources && msg.meta.sources.length > 0 && (
                        <div className="border border-industrial-800 rounded-lg overflow-hidden bg-industrial-950/20 text-xs">
                          <button 
                            onClick={() => toggleSection(i, 'sources')} 
                            className="w-full px-3 py-2 flex items-center justify-between text-slate-300 font-semibold border-b border-industrial-800 bg-industrial-950/40"
                          >
                            <span className="flex items-center"><FileText className="w-3.5 h-3.5 mr-1.5 text-blue-400" /> Inline Sources ({msg.meta.sources.length})</span>
                            {isSectionExpanded(i, 'sources') ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>
                          {isSectionExpanded(i, 'sources') && (
                            <div className="p-3 space-y-2 max-h-48 overflow-y-auto divide-y divide-industrial-850">
                              {msg.meta.sources.map((src, idx) => (
                                <div key={idx} className="pt-2 first:pt-0">
                                  <div className="font-semibold text-slate-300">{src.document || src.source_document || 'Unknown'}</div>
                                  <div className="text-[10px] text-slate-500 mt-0.5">
                                    Chunk ID: <span className="font-mono">{src.chunk_id}</span> • Score: {(src.score || src.similarity_score || 0).toFixed(4)}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Graph Nodes Accordion */}
                      {msg.meta.graph_nodes && msg.meta.graph_nodes.length > 0 && (
                        <div className="border border-industrial-800 rounded-lg overflow-hidden bg-industrial-950/20 text-xs">
                          <button 
                            onClick={() => toggleSection(i, 'nodes')} 
                            className="w-full px-3 py-2 flex items-center justify-between text-slate-300 font-semibold border-b border-industrial-800 bg-industrial-950/40"
                          >
                            <span className="flex items-center"><Hexagon className="w-3.5 h-3.5 mr-1.5 text-emerald-400" /> Graph Entities ({msg.meta.graph_nodes.length})</span>
                            {isSectionExpanded(i, 'nodes') ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>
                          {isSectionExpanded(i, 'nodes') && (
                            <div className="p-3 max-h-48 overflow-y-auto flex flex-wrap gap-1.5">
                              {msg.meta.graph_nodes.map((node, idx) => (
                                <span key={idx} className="px-2 py-0.5 bg-industrial-800 border border-industrial-700 text-slate-300 rounded text-[10px] font-mono">
                                  {node.name} ({node.type})
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {chatMutation.isPending && (
            <div className="flex justify-start">
              <div className="flex space-x-3 max-w-[85%]">
                <div className="flex-shrink-0 w-9 h-9 rounded-full bg-industrial-800 border border-brand-accent/50 flex items-center justify-center animate-pulse">
                  <Bot className="w-4 h-4 text-brand-accent" />
                </div>
                <div className="glass-panel rounded-xl rounded-tl-none p-4 flex items-center space-x-2">
                  <div className="w-2 h-2 rounded-full bg-brand-accent animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-brand-accent animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 rounded-full bg-brand-accent animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Suggestion Chips */}
        {messages.length === 1 && (
          <div className="flex flex-wrap gap-2 mb-3">
            {suggestedQuestions.map((q, idx) => (
              <button 
                key={idx}
                onClick={() => handleSuggestedQuestion(q)}
                className="px-3 py-1.5 bg-industrial-800 hover:bg-industrial-700 border border-industrial-700 hover:border-slate-500 text-slate-300 font-medium rounded-lg text-xs transition-all flex items-center space-x-1.5"
              >
                <HelpCircle className="w-3.5 h-3.5 text-brand-accent" />
                <span>{q}</span>
              </button>
            ))}
          </div>
        )}

        {/* Chat Input Bar */}
        <div className="flex-shrink-0 glass-panel p-2 rounded-xl focus-within:border-brand-primary/50 focus-within:ring-1 focus-within:ring-brand-primary/55 transition-all">
          <form onSubmit={handleSubmit} className="flex items-center">
            <input 
              type="text"
              className="flex-1 bg-transparent border-none text-slate-200 px-3 py-2.5 focus:outline-none placeholder-slate-500 text-sm"
              placeholder="Ask IndusMind AI Agent..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={chatMutation.isPending}
            />
            <button 
              type="submit"
              disabled={!input.trim() || chatMutation.isPending}
              className="p-2.5 bg-brand-primary hover:bg-brand-primary/90 text-white rounded-lg transition-colors disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
