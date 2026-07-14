import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { chatWithAgents } from '../services/api';
import { Send, Bot, User, ShieldAlert, Wrench, Search, Zap, Clock, Activity, CheckCircle2 } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

export default function AIAssistant() {
  const [session] = useState(uuidv4());
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello. I am IndusMind AI. You can ask me about maintenance history, compliance rules, or equipment topologies. How can I assist you today?',
    }
  ]);
  const [input, setInput] = useState('');

  const chatMutation = useMutation({
    mutationFn: (q) => chatWithAgents(q, session),
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, meta: data }
      ]);
    },
    onError: (err) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'There was an error communicating with the LangGraph backend. Please try again.', isError: true }
      ]);
    }
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || chatMutation.isPending) return;
    
    setMessages((prev) => [...prev, { role: 'user', content: input.trim() }]);
    chatMutation.mutate(input.trim());
    setInput('');
  };

  return (
    <div className="max-w-5xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      <div className="flex-1 overflow-y-auto pr-4 space-y-6 pb-6">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-[85%] space-x-3 ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
              
              {/* Avatar */}
              <div className="flex-shrink-0">
                {msg.role === 'user' ? (
                  <div className="w-10 h-10 rounded-full bg-brand-primary flex items-center justify-center shadow-lg">
                    <User className="w-5 h-5 text-white" />
                  </div>
                ) : (
                  <div className="w-10 h-10 rounded-full bg-industrial-800 border border-brand-accent/50 flex items-center justify-center shadow-[0_0_10px_rgba(14,165,233,0.3)]">
                    <Bot className="w-5 h-5 text-brand-accent" />
                  </div>
                )}
              </div>

              {/* Message Bubble */}
              <div className={`p-5 rounded-2xl ${
                msg.role === 'user' 
                  ? 'bg-brand-primary text-white rounded-tr-sm shadow-md' 
                  : msg.isError 
                    ? 'glass-panel border-red-500/50 rounded-tl-sm text-red-200' 
                    : 'glass-panel rounded-tl-sm text-slate-200'
              }`}>
                <p className="whitespace-pre-wrap leading-relaxed text-[15px]">{msg.content}</p>

                {/* Rich Explainability Metadata (Only for Assistant) */}
                {msg.meta && (
                  <div className="mt-5 pt-4 border-t border-industrial-700/50 space-y-4">
                    
                    {/* Metrics Row */}
                    <div className="flex flex-wrap gap-4 text-xs">
                      <div className="flex items-center text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded">
                        <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                        Confidence: {(msg.meta.confidence * 100).toFixed(0)}%
                      </div>
                      <div className="flex items-center text-amber-400 bg-amber-400/10 px-2 py-1 rounded">
                        <Clock className="w-3.5 h-3.5 mr-1.5" />
                        {msg.meta.execution_time_ms}ms
                      </div>
                      <div className="flex items-center text-blue-400 bg-blue-400/10 px-2 py-1 rounded">
                        <Activity className="w-3.5 h-3.5 mr-1.5" />
                        {msg.meta.agents_used?.length || 0} Agents
                      </div>
                    </div>

                    {/* Reasoning Trace */}
                    {msg.meta.reasoning_trace && msg.meta.reasoning_trace.length > 0 && (
                      <div className="bg-industrial-950/50 p-3 rounded-lg border border-industrial-800">
                        <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider flex items-center">
                          <Zap className="w-3 h-3 mr-1" /> LangGraph Trace
                        </p>
                        <ul className="space-y-1.5">
                          {msg.meta.reasoning_trace.map((step, idx) => (
                            <li key={idx} className="text-xs text-slate-500 font-mono flex items-start">
                              <span className="text-brand-accent mr-2">❯</span>
                              <span>{step}</span>
                            </li>
                          ))}
                        </ul>
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
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-industrial-800 border border-brand-accent/50 flex items-center justify-center animate-pulse">
                <Bot className="w-5 h-5 text-brand-accent" />
              </div>
              <div className="glass-panel rounded-2xl rounded-tl-sm p-5 flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-brand-accent animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-brand-accent animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-brand-accent animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="flex-shrink-0 glass-panel p-2 rounded-xl mt-4 focus-within:border-brand-primary/50 focus-within:ring-1 focus-within:ring-brand-primary/50 transition-all">
        <form onSubmit={handleSubmit} className="flex items-center">
          <input
            type="text"
            className="flex-1 bg-transparent border-none text-slate-100 px-4 py-3 focus:outline-none placeholder-slate-500 text-[15px]"
            placeholder="Ask a question about maintenance, safety, or equipment..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={chatMutation.isPending}
          />
          <button
            type="submit"
            disabled={!input.trim() || chatMutation.isPending}
            className="p-3 bg-brand-primary hover:bg-brand-primary/90 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}
