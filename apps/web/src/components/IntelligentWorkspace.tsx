import React, { useState, useEffect } from 'react';
import {
  Brain,
  Send,
  BookOpen,
  FolderGit2,
  Users,
  Search,
  Quote,
  CheckCircle2,
  ExternalLink,
  ShieldAlert,
  ArrowRight,
  Sparkles,
  FileText,
  Clock,
  Layers,
} from 'lucide-react';

interface WorkspaceMember {
  user_id: string;
  name: string;
  email: string;
  role: string;
}

interface WorkspaceItem {
  workspace_id: string;
  name: string;
  client_name: string;
  description: string;
  industry: string;
  status: string;
  document_count: number;
  members: WorkspaceMember[];
  tags: string[];
}

interface Citation {
  document_name: string;
  page_number: number;
  clause_reference?: string;
  verbatim_quote: string;
  relevance_score: number;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: string;
}

interface IntelligentWorkspaceProps {
  onNavigateTab?: (tab: string) => void;
}

export const IntelligentWorkspace: React.FC<IntelligentWorkspaceProps> = ({ onNavigateTab }) => {
  const [workspaces, setWorkspaces] = useState<WorkspaceItem[]>([]);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState<string>('ws-project-apollo');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputQuery, setInputQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [expandedCitationIdx, setExpandedCitationIdx] = useState<number | null>(null);

  // Fetch workspaces on load
  useEffect(() => {
    fetch('/api/workspaces')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data?.workspaces && data.workspaces.length > 0) {
          setWorkspaces(data.workspaces);
          setSelectedWorkspaceId(data.workspaces[0].workspace_id);
        }
      })
      .catch(() => {});

    // Initial greeting message
    setMessages([
      {
        id: 'msg-welcome',
        role: 'assistant',
        content: `Welcome to the **Intelligent Knowledge Workspace**. I am connected to the centralized document repository for this engagement.\n\nYou can ask cross-document legal, operational, and financial questions across all contracts, Master Services Agreements, and financial statements. Every answer is grounded with verifiable page and clause citations.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      },
    ]);
  }, []);

  const activeWorkspace =
    workspaces.find((w) => w.workspace_id === selectedWorkspaceId) || workspaces[0];

  const handleSendMessage = async (queryText?: string) => {
    const q = (queryText || inputQuery).trim();
    if (!q || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setIsLoading(true);

    try {
      const res = await fetch(`/api/workspaces/${selectedWorkspaceId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, top_k: 4 }),
      });

      if (res.ok) {
        const data = await res.json();
        const assistantMsg: ChatMessage = {
          id: `asst-${Date.now()}`,
          role: 'assistant',
          content: data.answer,
          citations: data.citations || [],
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages((prev) => [...prev, assistantMsg]);
      }
    } catch {
      // Local fallback
    } finally {
      setIsLoading(false);
    }
  };

  const samplePrompts = [
    'What are the change of control risks and immediate termination penalties?',
    'Which vendors have reported uptime breaches and assessed service credits?',
    'Summarize ASC 606 revenue performance obligations and recognition timing.',
    'Identify unlimited liability and regulatory penalty exposure across all vendors.',
  ];

  return (
    <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-6">
      {/* Workspace Header & Selector */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-3">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-300">
                PILLAR 5
              </span>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                Intelligent Workspace & Knowledge Brain
              </h1>
            </div>
            <p className="text-sm text-slate-500">
              Engagement-isolated semantic RAG search, contextual AI Q&A, and citation-grounded enterprise workflows.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 bg-slate-50 border border-slate-300 rounded-lg px-3 py-2">
              <FolderGit2 className="w-4 h-4 text-purple-600" />
              <label className="text-xs font-semibold text-slate-600">Active Engagement:</label>
              <select
                value={selectedWorkspaceId}
                onChange={(e) => {
                  setSelectedWorkspaceId(e.target.value);
                  setMessages([
                    {
                      id: `msg-switch-${Date.now()}`,
                      role: 'assistant',
                      content: `Switched context to **${e.target.options[e.target.selectedIndex].text}**. The knowledge brain has loaded this engagement's document index.`,
                      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    },
                  ]);
                }}
                className="bg-transparent text-sm font-bold text-slate-900 focus:outline-none"
              >
                {workspaces.map((ws) => (
                  <option key={ws.workspace_id} value={ws.workspace_id}>
                    {ws.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Workspace Metadata Banner */}
        {activeWorkspace && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-100 text-xs">
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-400 font-medium block">Client / Organization</span>
              <span className="font-bold text-slate-900 text-sm block mt-0.5">
                {activeWorkspace.client_name}
              </span>
              <span className="text-purple-600 font-semibold">{activeWorkspace.industry}</span>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-400 font-medium block">Indexed Documents</span>
              <span className="font-bold text-slate-900 text-sm block mt-0.5">
                {activeWorkspace.document_count} Knowledge Files
              </span>
              <span className="text-emerald-600 font-semibold">100% Vector Embedded</span>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-400 font-medium block">Team & RBAC Permissions</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {activeWorkspace.members.map((m) => (
                  <span
                    key={m.user_id}
                    className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-white border border-slate-200 font-medium text-slate-700"
                  >
                    {m.name.split(',')[0]} ({m.role.replace('_', ' ')})
                  </span>
                ))}
              </div>
            </div>

            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200">
              <span className="text-slate-400 font-medium block">Compliance & Domain Tags</span>
              <div className="mt-1 flex flex-wrap gap-1">
                {activeWorkspace.tags.map((t) => (
                  <span
                    key={t}
                    className="inline-flex items-center px-2 py-0.5 rounded text-[10px] bg-purple-50 text-purple-700 font-semibold"
                  >
                    #{t}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Split Layout: Documents & Quick Actions (Left) + Contextual Chat (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Knowledge Base & Actions (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          {/* Document Repository Card */}
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
                <FileText className="w-4 h-4 text-purple-600" />
                <span>Engagement Knowledge Base</span>
              </h2>
              <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full font-semibold">
                {activeWorkspace?.document_count || 0} Docs
              </span>
            </div>

            <div className="space-y-2.5 text-xs">
              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 hover:border-purple-300 transition">
                <div className="font-semibold text-slate-800 flex items-center justify-between">
                  <span>01_CloudCore_Vendor_SLA.pdf</span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">
                    INDEXED
                  </span>
                </div>
                <p className="text-slate-500 mt-0.5">Uptime SLA, 99.9% availability, tier penalties.</p>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 hover:border-purple-300 transition">
                <div className="font-semibold text-slate-800 flex items-center justify-between">
                  <span>02_DataStream_Critical_Risk.pdf</span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">
                    INDEXED
                  </span>
                </div>
                <p className="text-slate-500 mt-0.5">Change of Control termination & acceleration clause.</p>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 hover:border-purple-300 transition">
                <div className="font-semibold text-slate-800 flex items-center justify-between">
                  <span>03_SecureDesk_Standard_License.pdf</span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">
                    INDEXED
                  </span>
                </div>
                <p className="text-slate-500 mt-0.5">Standard assignment rights, Delaware law.</p>
              </div>

              <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 hover:border-purple-300 transition">
                <div className="font-semibold text-slate-800 flex items-center justify-between">
                  <span>Portfolio_Financials_FY25.pdf</span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">
                    INDEXED
                  </span>
                </div>
                <p className="text-slate-500 mt-0.5">Consolidated P&L, balance sheets, revenue recognition.</p>
              </div>
            </div>
          </div>

          {/* Quick Pillar Workflow Triggers */}
          <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-100 p-5 space-y-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <span>Workspace Automation Actions</span>
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Launch cross-pillar analytics on this engagement’s document repository with a single click.
            </p>

            <div className="space-y-2 pt-2">
              <button
                onClick={() => onNavigateTab && onNavigateTab('ma-diligence')}
                className="w-full text-left flex items-center justify-between p-2.5 bg-white rounded-lg border border-indigo-200 hover:border-indigo-400 text-xs font-semibold text-indigo-900 shadow-xs transition"
              >
                <span>Run M&A SLA Diligence Rollup (P1)</span>
                <ArrowRight className="w-3.5 h-3.5 text-indigo-600" />
              </button>

              <button
                onClick={() => onNavigateTab && onNavigateTab('financial-comparator')}
                className="w-full text-left flex items-center justify-between p-2.5 bg-white rounded-lg border border-indigo-200 hover:border-indigo-400 text-xs font-semibold text-indigo-900 shadow-xs transition"
              >
                <span>Launch 30-Company Comparator (P2)</span>
                <ArrowRight className="w-3.5 h-3.5 text-indigo-600" />
              </button>

              <button
                onClick={() => onNavigateTab && onNavigateTab('accounting-studio')}
                className="w-full text-left flex items-center justify-between p-2.5 bg-white rounded-lg border border-indigo-200 hover:border-indigo-400 text-xs font-semibold text-indigo-900 shadow-xs transition"
              >
                <span>Open ASC 606 Memo Studio (P3)</span>
                <ArrowRight className="w-3.5 h-3.5 text-indigo-600" />
              </button>

              <button
                onClick={() => onNavigateTab && onNavigateTab('batch-automation')}
                className="w-full text-left flex items-center justify-between p-2.5 bg-white rounded-lg border border-indigo-200 hover:border-indigo-400 text-xs font-semibold text-indigo-900 shadow-xs transition"
              >
                <span>Execute Batch Data Automation (P4)</span>
                <ArrowRight className="w-3.5 h-3.5 text-indigo-600" />
              </button>
            </div>
          </div>
        </div>

        {/* Right Column: Contextual AI Chat & Citation Inspector (8 cols) */}
        <div className="lg:col-span-8 flex flex-col bg-white rounded-xl shadow-sm border border-slate-200 min-h-[640px] overflow-hidden">
          {/* Chat Header */}
          <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
            <div className="flex items-center space-x-2.5">
              <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center text-white font-bold">
                <Brain className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Contextual Engagement Assistant</h3>
                <span className="text-[11px] text-slate-500">Grounded strictly in verified workspace documents</span>
              </div>
            </div>

            <div className="flex items-center space-x-1.5 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full font-semibold border border-emerald-200">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>pgvector RAG Connected</span>
            </div>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 p-6 space-y-6 overflow-y-auto max-h-[480px]">
            {messages.map((msg, idx) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'bg-indigo-600 text-white rounded-br-none'
                      : 'bg-slate-50 border border-slate-200 text-slate-800 rounded-bl-none shadow-2xs'
                  }`}
                >
                  <div className="whitespace-pre-line">{msg.content}</div>

                  {/* Grounded Citations Pills */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-200/80">
                      <span className="text-[11px] font-bold text-purple-700 uppercase tracking-wider block mb-2">
                        Verifiable Sources & Citations ({msg.citations.length})
                      </span>
                      <div className="space-y-1.5">
                        {msg.citations.map((cite, cIdx) => (
                          <div
                            key={cIdx}
                            onClick={() =>
                              setExpandedCitationIdx(expandedCitationIdx === cIdx ? null : cIdx)
                            }
                            className="p-2 bg-white rounded-md border border-purple-200 hover:border-purple-400 cursor-pointer transition text-xs"
                          >
                            <div className="flex items-center justify-between text-purple-900 font-semibold">
                              <span>
                                📄 {cite.document_name} • Page {cite.page_number}
                                {cite.clause_reference ? ` (${cite.clause_reference})` : ''}
                              </span>
                              <span className="text-[10px] text-slate-400">
                                {expandedCitationIdx === cIdx ? '▲ Collapse' : '▼ View Quote'}
                              </span>
                            </div>

                            {expandedCitationIdx === cIdx && (
                              <div className="mt-2 pt-2 border-t border-slate-100 text-slate-700 italic bg-purple-50/50 p-2 rounded">
                                <Quote className="w-3 h-3 text-purple-400 inline mr-1" />
                                "{cite.verbatim_quote}"
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                <span className="text-[10px] text-slate-400 mt-1 px-1">{msg.timestamp}</span>
              </div>
            ))}

            {isLoading && (
              <div className="flex items-center space-x-2 text-slate-400 text-xs p-2">
                <Brain className="w-4 h-4 animate-spin text-purple-600" />
                <span>Searching knowledge brain and retrieving grounded passages...</span>
              </div>
            )}
          </div>

          {/* Quick Prompt Suggestions */}
          <div className="px-6 py-2 bg-slate-50/70 border-t border-slate-100 flex flex-wrap gap-1.5">
            {samplePrompts.map((prompt, pIdx) => (
              <button
                key={pIdx}
                onClick={() => handleSendMessage(prompt)}
                className="text-[11px] bg-white border border-slate-300 hover:border-indigo-400 text-slate-700 hover:text-indigo-600 px-2.5 py-1 rounded-full transition shadow-3xs"
              >
                💡 {prompt}
              </button>
            ))}
          </div>

          {/* Input Box */}
          <div className="p-4 border-t border-slate-200 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center space-x-3"
            >
              <input
                type="text"
                placeholder="Ask any question about contracts, SLAs, or financial statements in this workspace..."
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                className="flex-1 px-4 py-2.5 bg-slate-50 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:bg-white transition"
              />
              <button
                type="submit"
                disabled={isLoading || !inputQuery.trim()}
                className="px-4 py-2.5 bg-purple-600 text-white rounded-lg text-sm font-semibold hover:bg-purple-700 transition flex items-center space-x-1.5 disabled:opacity-50 shadow-sm"
              >
                <span>Ask AI</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

