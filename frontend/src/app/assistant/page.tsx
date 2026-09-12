'use client';

import React, { useState, useEffect, useRef } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import {
  Sparkles,
  Send,
  User,
  Bot,
  Terminal,
  Code,
  CheckCircle2,
  TrendingUp,
  DollarSign,
  Cpu,
  ShieldCheck,
  BarChart3,
  Plus,
  Trash2,
  RefreshCw,
  Zap,
  ChevronDown,
  ChevronUp,
  Clock,
  Layers,
  Database,
} from 'lucide-react';

interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  generated_sql?: string;
  data_results?: Array<Record<string, any>>;
  citations?: string[];
  recommendations?: string[];
  tokens_used?: number;
  latency_ms?: number;
  created_at?: string;
}

interface ConversationSummary {
  id: number;
  title: string;
  persona: string;
  messages_count: number;
  created_at: string;
}

interface PromptTemplate {
  id: string;
  persona: string;
  title: string;
  prompt_text: string;
  category: string;
}

const PERSONAS = [
  {
    id: 'CEO_STRATEGIST',
    title: 'CEO Strategy Copilot',
    roleLabel: 'Chief Executive Strategy',
    description: 'Quarterly ARR expansion, strategic market positioning, and territory growth.',
    icon: TrendingUp,
    badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    avatarGradient: 'from-blue-600 to-indigo-600',
  },
  {
    id: 'CFO_FINANCIAL',
    title: 'CFO Financial Copilot',
    roleLabel: 'Chief Financial Officer',
    description: 'Cash runway, Quick Ratio solvency, EBITDA margins, and unit economics.',
    icon: DollarSign,
    badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    avatarGradient: 'from-emerald-600 to-teal-600',
  },
  {
    id: 'CTO_ARCHITECT',
    title: 'CTO Systems Copilot',
    roleLabel: 'Chief Technology Officer',
    description: 'Data connector latencies, 4-pillar ETL quality, and system infrastructure.',
    icon: Cpu,
    badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    avatarGradient: 'from-purple-600 to-indigo-600',
  },
  {
    id: 'BI_ANALYST',
    title: 'BI Analyst Copilot',
    roleLabel: 'Lead BI & Data Analyst',
    description: 'Natural Language to SQL queries, cohort retention, and tabular slicing.',
    icon: BarChart3,
    badgeColor: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    avatarGradient: 'from-amber-600 to-orange-600',
  },
  {
    id: 'SECURITY_OFFICER',
    title: 'Security & Compliance',
    roleLabel: 'Chief Information Security',
    description: 'Zero-trust RBAC telemetry, anomaly detection, and access audit scans.',
    icon: ShieldCheck,
    badgeColor: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    avatarGradient: 'from-rose-600 to-red-600',
  },
];

export default function AssistantPage() {
  const { user } = useAuth();
  const [selectedPersona, setSelectedPersona] = useState<string>('CEO_STRATEGIST');
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConvId, setActiveConvId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);

  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [openSqlDrawerId, setOpenSqlDrawerId] = useState<number | null>(null);

  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const fetchConversations = async () => {
    try {
      const res = await apiClient.get<ConversationSummary[]>('/assistant/conversations');
      setConversations(res.data || []);
    } catch (err) {
      console.error('Error loading conversations:', err);
    }
  };

  const fetchPrompts = async (persona: string) => {
    try {
      const res = await apiClient.get<PromptTemplate[]>(`/assistant/prompts?persona=${persona}`);
      setPrompts(res.data || []);
    } catch (err) {
      console.error('Error loading prompts:', err);
    }
  };

  const loadConversation = async (convId: number) => {
    setActiveConvId(convId);
    setLoadingHistory(true);
    try {
      const res = await apiClient.get(`/assistant/conversations/${convId}`);
      setMessages(res.data.messages || []);
      if (res.data.persona) {
        setSelectedPersona(res.data.persona);
      }
    } catch (err) {
      console.error('Error loading conversation detail:', err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const startNewChat = () => {
    setActiveConvId(null);
    setMessages([]);
    setInputQuery('');
  };

  const handleDeleteConversation = async (convId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient.delete(`/assistant/conversations/${convId}`);
      if (activeConvId === convId) {
        startNewChat();
      }
      fetchConversations();
    } catch (err) {
      console.error('Error deleting conversation:', err);
    }
  };

  useEffect(() => {
    fetchConversations();
    fetchPrompts(selectedPersona);
  }, [selectedPersona]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSendMessage = async (queryText?: string) => {
    const q = queryText || inputQuery;
    if (!q.trim()) return;

    const userMsg: Message = {
      role: 'user',
      content: q,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await apiClient.post('/assistant/query', {
        query: q,
        persona: selectedPersona,
        conversation_id: activeConvId,
        include_sql_synthesis: true,
      });

      const assistantMsg: Message = res.data.message;
      setMessages((prev) => [...prev, assistantMsg]);
      if (!activeConvId && res.data.conversation_id) {
        setActiveConvId(res.data.conversation_id);
      }
      fetchConversations();
    } catch (err: any) {
      const errorMsg: Message = {
        role: 'assistant',
        content: `**Error**: ${err.response?.data?.detail || 'Failed to process AI query. Please verify server connectivity.'}`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const activePersonaObj = PERSONAS.find((p) => p.id === selectedPersona) || PERSONAS[0];

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI Executive Assistant & Natural Language Querying (NLQ)</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">AI Decision Intelligence Copilot</h1>
            <p className="text-xs text-slate-400 mt-1">
              Natural Language to SQL data synthesis, multi-persona executive reasoning, and transparent decision recommendations.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={startNewChat}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all"
            >
              <Plus className="w-4 h-4" />
              New Conversation Thread
            </button>
          </div>
        </div>

        {/* Persona Switcher Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {PERSONAS.map((p) => {
            const isSelected = selectedPersona === p.id;
            return (
              <button
                key={p.id}
                onClick={() => {
                  setSelectedPersona(p.id);
                  startNewChat();
                }}
                className={`p-4 rounded-2xl border text-left transition-all flex flex-col justify-between space-y-3 ${
                  isSelected
                    ? 'bg-blue-950/40 border-blue-500 shadow-lg shadow-blue-900/20'
                    : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className={`w-8 h-8 rounded-xl bg-gradient-to-tr ${p.avatarGradient} flex items-center justify-center text-white`}>
                    <p.icon className="w-4 h-4" />
                  </div>
                  {isSelected && (
                    <span className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                  )}
                </div>
                <div>
                  <p className="text-xs font-bold text-white">{p.title}</p>
                  <p className="text-[10px] text-slate-400 line-clamp-2 mt-0.5">{p.description}</p>
                </div>
              </button>
            );
          })}
        </div>

        {/* Main 2-Column Chat Studio */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Left Column: Conversation History */}
          <div className="space-y-3 lg:col-span-1">
            <div className="flex items-center justify-between px-1">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                Decision Dialogues ({conversations.length})
              </span>
            </div>

            <div className="space-y-2 max-h-[600px] overflow-y-auto custom-scrollbar">
              {conversations.length === 0 ? (
                <div className="p-6 text-center text-slate-500 bg-slate-900/40 rounded-2xl border border-slate-800 text-xs">
                  No conversation threads logged yet.
                </div>
              ) : (
                conversations.map((c) => {
                  const isActive = activeConvId === c.id;
                  return (
                    <div
                      key={c.id}
                      onClick={() => loadConversation(c.id)}
                      className={`p-3 rounded-xl border transition-all cursor-pointer flex items-center justify-between group ${
                        isActive
                          ? 'bg-blue-600/20 border-blue-500 text-white'
                          : 'bg-slate-900/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
                      }`}
                    >
                      <div className="overflow-hidden pr-2">
                        <p className="font-semibold text-xs truncate">{c.title}</p>
                        <p className="text-[10px] text-slate-500 font-mono">
                          {c.persona.replace('_', ' ')} &bull; {c.messages_count} msgs
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDeleteConversation(c.id, e)}
                        className="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-800 text-slate-400 hover:text-red-400 rounded transition-all"
                        title="Delete Thread"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Column: Active Interactive Chat Canvas */}
          <div className="lg:col-span-3 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between space-y-4 min-h-[620px]">
            {/* Thread Header */}
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-3">
                <div className={`w-9 h-9 rounded-xl bg-gradient-to-tr ${activePersonaObj.avatarGradient} flex items-center justify-center text-white shadow-md`}>
                  <activePersonaObj.icon className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    {activePersonaObj.title}
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${activePersonaObj.badgeColor}`}>
                      {activePersonaObj.roleLabel}
                    </span>
                  </h3>
                  <p className="text-[11px] text-slate-400">Grounded with verified enterprise dataset & KPI telemetry</p>
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs font-mono text-slate-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                Zero Prompt Leakage Safe
              </div>
            </div>

            {/* Chat Stream Area */}
            <div className="flex-1 overflow-y-auto max-h-[440px] space-y-4 pr-2 custom-scrollbar">
              {messages.length === 0 ? (
                <div className="py-12 text-center space-y-4">
                  <div className="w-12 h-12 rounded-2xl bg-blue-500/10 text-blue-400 flex items-center justify-center mx-auto border border-blue-500/20">
                    <Sparkles className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white">How can I assist your strategic decision-making today?</h4>
                    <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                      Select an executive prompt chip below or type an analytical question regarding financial margins, pipeline growth, or security audit logs.
                    </p>
                  </div>

                  {/* Quick Action Prompt Chips */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 max-w-2xl mx-auto pt-2">
                    {prompts.map((p) => (
                      <button
                        key={p.id}
                        onClick={() => handleSendMessage(p.prompt_text)}
                        className="p-3 bg-slate-950/60 hover:bg-slate-800/80 border border-slate-800 rounded-2xl text-left transition-all group"
                      >
                        <span className="text-[10px] font-bold text-blue-400 uppercase font-mono block mb-1">
                          {p.category}
                        </span>
                        <p className="text-xs font-semibold text-white group-hover:text-blue-300 transition-colors line-clamp-1">
                          {p.title}
                        </p>
                        <p className="text-[11px] text-slate-400 line-clamp-2 mt-0.5">{p.prompt_text}</p>
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                messages.map((m, idx) => (
                  <div
                    key={idx}
                    className={`flex flex-col space-y-2 ${
                      m.role === 'user' ? 'items-end' : 'items-start'
                    }`}
                  >
                    {/* Message Bubble */}
                    <div
                      className={`max-w-[85%] rounded-3xl p-4 sm:p-5 text-xs ${
                        m.role === 'user'
                          ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                          : 'bg-slate-950/90 text-slate-200 border border-slate-800/80 shadow-md'
                      }`}
                    >
                      {/* Assistant Header Badge */}
                      {m.role === 'assistant' && (
                        <div className="flex items-center justify-between gap-3 mb-2 pb-2 border-b border-slate-800">
                          <span className="font-bold text-blue-400 flex items-center gap-1.5 font-mono text-[11px]">
                            <Sparkles className="w-3.5 h-3.5" />
                            AegisIQ Intelligence Response
                          </span>
                          {m.latency_ms !== undefined && (
                            <span className="text-[10px] text-slate-500 font-mono">
                              {m.latency_ms}ms &bull; {m.tokens_used} tokens
                            </span>
                          )}
                        </div>
                      )}

                      {/* Content Body */}
                      <div className="prose prose-invert prose-xs max-w-none space-y-2 whitespace-pre-wrap leading-relaxed">
                        {m.content}
                      </div>

                      {/* Expandable Generated SQL & Data Verification Drawer */}
                      {m.generated_sql && (
                        <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-2 font-mono text-[11px]">
                          <button
                            onClick={() => setOpenSqlDrawerId(openSqlDrawerId === idx ? null : idx)}
                            className="flex items-center gap-1.5 text-blue-400 hover:text-blue-300 font-bold transition-colors font-sans"
                          >
                            <Terminal className="w-3.5 h-3.5" />
                            <span>{openSqlDrawerId === idx ? 'Hide Synthesized SQL Query' : 'View Synthesized SQL & Verified Data'}</span>
                            {openSqlDrawerId === idx ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                          </button>

                          {openSqlDrawerId === idx && (
                            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 space-y-2">
                              <pre className="text-[10px] text-emerald-300 whitespace-pre-wrap">{m.generated_sql}</pre>
                              {m.data_results && m.data_results.length > 0 && (
                                <div className="overflow-x-auto pt-2 border-t border-slate-800">
                                  <table className="w-full text-left text-[10px]">
                                    <tbody className="divide-y divide-slate-800">
                                      {m.data_results.map((row, r_idx) => (
                                        <tr key={r_idx}>
                                          {Object.entries(row).map(([k, v]) => (
                                            <td key={k} className="py-1 px-2 text-slate-400">
                                              <span className="text-slate-500">{k}:</span> {String(v)}
                                            </td>
                                          ))}
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      )}

                      {/* Strategic Recommendations Card */}
                      {m.recommendations && m.recommendations.length > 0 && (
                        <div className="mt-4 p-3 bg-blue-950/30 border border-blue-800/40 rounded-2xl space-y-2">
                          <span className="text-[11px] font-bold text-blue-300 flex items-center gap-1.5 font-sans">
                            <Zap className="w-3.5 h-3.5 text-amber-400" />
                            Actionable Strategic Recommendations
                          </span>
                          <ul className="space-y-1 pl-4 list-disc text-[11px] text-slate-300">
                            {m.recommendations.map((rec, rec_idx) => (
                              <li key={rec_idx}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Citations */}
                      {m.citations && m.citations.length > 0 && (
                        <div className="mt-3 text-[10px] text-slate-500 font-mono">
                          <span>Auditable Sources: {m.citations.join(' | ')}</span>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}

              {loading && (
                <div className="flex items-center gap-3 p-4 bg-slate-950/60 rounded-2xl border border-slate-800 text-xs text-slate-400 w-fit">
                  <RefreshCw className="w-4 h-4 animate-spin text-blue-500" />
                  <span>Synthesizing multi-persona decision intelligence...</span>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Bottom Input Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="relative flex items-center gap-2 pt-2 border-t border-slate-800"
            >
              <input
                type="text"
                placeholder={`Ask ${activePersonaObj.title} an executive decision or data query...`}
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                disabled={loading}
                className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-2xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-sans"
              />
              <button
                type="submit"
                disabled={loading || !inputQuery.trim()}
                className="px-5 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all disabled:opacity-40 flex items-center gap-1.5"
              >
                <Send className="w-3.5 h-3.5" />
                Ask
              </button>
            </form>
          </div>
        </div>
      </div>
    </EnterpriseShell>
  );
}
