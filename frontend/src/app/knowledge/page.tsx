'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import {
  BookOpen,
  Search,
  Upload,
  FileText,
  FileCode,
  FileSpreadsheet,
  Trash2,
  RefreshCw,
  Sparkles,
  Layers,
  CheckCircle2,
  XCircle,
  Clock,
  Shield,
  Tag,
  ExternalLink,
  Sliders,
  Filter,
  ChevronRight,
  Eye,
  Hash,
} from 'lucide-react';

interface DocumentSummary {
  id: number;
  title: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
  total_chunks: number;
  total_tokens: number;
  category: string;
  created_at: string;
}

interface DocumentChunk {
  id: number;
  document_id: number;
  chunk_index: number;
  content: string;
  token_count: number;
  page_number: number;
  section_heading?: string;
  embedding_preview: number[];
  created_at: string;
}

interface DocumentDetail extends DocumentSummary {
  chunks: DocumentChunk[];
}

interface Citation {
  chunk_id: number;
  document_id: number;
  document_title: string;
  category: string;
  page_number: number;
  section_heading?: string;
  similarity_score: number;
  snippet: string;
}

interface RAGResponse {
  query: string;
  answer: string;
  matched_citations: Citation[];
  top_similarity_score: number;
  latency_ms: number;
  created_at: string;
}

export default function KnowledgePage() {
  const { hasRole } = useAuth();
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // RAG Search State
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(3);
  const [ragCategory, setRagCategory] = useState('');
  const [searching, setSearching] = useState(false);
  const [ragResult, setRagResult] = useState<RAGResponse | null>(null);

  // Chunk Inspector Drawer
  const [selectedDoc, setSelectedDoc] = useState<DocumentDetail | null>(null);
  const [loadingChunks, setLoadingChunks] = useState(false);

  // Upload Modal
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadCategory, setUploadCategory] = useState('POLICY');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const fetchDocuments = async () => {
    setLoadingDocs(true);
    try {
      let url = '/knowledge/documents';
      if (categoryFilter !== 'ALL') url += `?category=${categoryFilter}`;
      const res = await apiClient.get<DocumentSummary[]>(url);
      setDocuments(res.data || []);
    } catch (err) {
      console.error('Error fetching knowledge documents:', err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [categoryFilter]);

  const handleRAGSearch = async (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const q = customQuery || query;
    if (!q.trim()) return;

    setSearching(true);
    try {
      const res = await apiClient.post<RAGResponse>('/knowledge/query', {
        query: q,
        top_k: topK,
        category_filter: ragCategory || undefined,
      });
      setRagResult(res.data);
    } catch (err: any) {
      setNotification({
        message: err.response?.data?.detail || 'Failed to execute semantic RAG search.',
        type: 'error',
      });
    } finally {
      setSearching(false);
    }
  };

  const handleInspectChunks = async (docId: number) => {
    setLoadingChunks(true);
    try {
      const res = await apiClient.get<DocumentDetail>(`/knowledge/documents/${docId}`);
      setSelectedDoc(res.data);
    } catch (err) {
      console.error('Error loading chunks:', err);
    } finally {
      setLoadingChunks(false);
    }
  };

  const handleDeleteDocument = async (docId: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await apiClient.delete(`/knowledge/documents/${docId}`);
      setNotification({ message: 'Document and vector embeddings removed successfully.', type: 'success' });
      if (selectedDoc?.id === docId) setSelectedDoc(null);
      fetchDocuments();
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Failed to delete document.', type: 'error' });
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('title', uploadTitle);
    formData.append('category', uploadCategory);

    try {
      await apiClient.post('/knowledge/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setNotification({ message: `Document '${uploadTitle}' indexed into vector store!`, type: 'success' });
      setShowUploadModal(false);
      setUploadTitle('');
      setUploadFile(null);
      fetchDocuments();
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Failed to index document.', type: 'error' });
    } finally {
      setUploading(false);
    }
  };

  const canManageDocs = hasRole(['Admin', 'Data Analyst', 'Business Analyst']);

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-2">
              <BookOpen className="w-3.5 h-3.5" />
              <span>RAG & Enterprise Vector Knowledge Base</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise Knowledge Base & RAG Copilot</h1>
            <p className="text-xs text-slate-400 mt-1">
              Index unstructured corporate policies, financial filings, and contracts into semantic vector embeddings for citation-backed question answering.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchDocuments}
              disabled={loadingDocs}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Documents"
            >
              <RefreshCw className={`w-4 h-4 ${loadingDocs ? 'animate-spin' : ''}`} />
            </button>
            {canManageDocs && (
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all"
              >
                <Upload className="w-4 h-4" />
                Index New Document
              </button>
            )}
          </div>
        </div>

        {/* Notice alert */}
        {notification && (
          <div
            className={`p-4 rounded-2xl border text-xs flex items-center justify-between transition-all ${
              notification.type === 'success'
                ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-300'
                : 'bg-red-950/40 border-red-800/60 text-red-300'
            }`}
          >
            <div className="flex items-center gap-2">
              {notification.type === 'success' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : (
                <XCircle className="w-4 h-4 text-red-400 shrink-0" />
              )}
              <span>{notification.message}</span>
            </div>
            <button onClick={() => setNotification(null)} className="text-slate-400 hover:text-white font-bold ml-4">
              &times;
            </button>
          </div>
        )}

        {/* Semantic RAG Search Box */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-500" />
              Semantic Vector Retrieval & RAG Question Answering
            </h3>
            <span className="text-xs text-slate-400 font-mono">Cosine Vector Similarity Search</span>
          </div>

          <form onSubmit={handleRAGSearch} className="space-y-3">
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Ask any question across indexed corporate policies, financial filings, or SLA handbooks..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-slate-950 border border-slate-800 rounded-2xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-sans"
                />
              </div>

              <div className="flex items-center gap-2">
                <select
                  value={ragCategory}
                  onChange={(e) => setRagCategory(e.target.value)}
                  className="px-3 py-3 bg-slate-950 border border-slate-800 rounded-2xl text-xs text-white focus:outline-none cursor-pointer"
                >
                  <option value="">All Categories</option>
                  <option value="POLICY">Policy & Governance</option>
                  <option value="FINANCIAL_FILING">Financial Filings</option>
                  <option value="SLA_CONTRACT">SLA & Contracts</option>
                  <option value="SECURITY_COMPLIANCE">Security & Compliance</option>
                </select>

                <button
                  type="submit"
                  disabled={searching || !query.trim()}
                  className="px-5 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-2xl text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all disabled:opacity-40 flex items-center gap-1.5 shrink-0"
                >
                  {searching ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
                  {searching ? 'Retrieving...' : 'Search RAG'}
                </button>
              </div>
            </div>

            {/* Prompt Suggestion Chips */}
            <div className="flex flex-wrap gap-2 pt-1">
              <span className="text-[10px] text-slate-500 uppercase font-bold self-center">Try Asking:</span>
              {[
                'What is our guaranteed service availability uptime and disaster recovery RTO?',
                'What are our Zero-Trust 5-tier RBAC and JWT cryptographic standards?',
                'Summarize our Q1 2026 revenue growth across North America and APAC.',
              ].map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setQuery(s);
                    handleRAGSearch(undefined, s);
                  }}
                  className="px-3 py-1 bg-slate-950/60 hover:bg-slate-800 border border-slate-800 rounded-full text-[11px] text-slate-300 transition-colors"
                >
                  {s}
                </button>
              ))}
            </div>
          </form>

          {/* RAG Results Display */}
          {ragResult && (
            <div className="mt-4 pt-4 border-t border-slate-800 space-y-4">
              <div className="p-5 bg-slate-950 border border-slate-800 rounded-2xl space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-blue-400" />
                    <span className="text-xs font-bold text-white">Grounded Knowledge Synthesis</span>
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {(ragResult.top_similarity_score * 100).toFixed(1)}% Semantic Match ({ragResult.latency_ms}ms)
                  </span>
                </div>

                <div className="prose prose-invert prose-xs max-w-none text-xs text-slate-200 leading-relaxed whitespace-pre-wrap">
                  {ragResult.answer}
                </div>
              </div>

              {/* Citations Card Grid */}
              <div className="space-y-2">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                  Auditable Source Citations ({ragResult.matched_citations.length})
                </span>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {ragResult.matched_citations.map((c, idx) => (
                    <div key={idx} className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-2 text-xs">
                      <div className="flex items-start justify-between gap-2">
                        <span className="font-bold text-white line-clamp-1">{c.document_title}</span>
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-bold font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20 shrink-0">
                          {(c.similarity_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <p className="text-[10px] font-mono text-slate-400">
                        Page {c.page_number} &bull; {c.section_heading || 'Excerpt'}
                      </p>
                      <p className="text-[11px] text-slate-300 italic bg-slate-900/80 p-2 rounded-xl line-clamp-3">
                        "{c.snippet}"
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Document Library Catalog */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-emerald-400" />
                Indexed Enterprise Knowledge Catalog
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                {documents.length} Unstructured documents segmented into searchable vector chunks
              </p>
            </div>

            <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="bg-transparent text-white focus:outline-none cursor-pointer"
              >
                <option value="ALL" className="bg-slate-900">All Categories</option>
                <option value="POLICY" className="bg-slate-900">Policies</option>
                <option value="FINANCIAL_FILING" className="bg-slate-900">Financial Filings</option>
                <option value="SLA_CONTRACT" className="bg-slate-900">SLA Handbooks</option>
                <option value="SECURITY_COMPLIANCE" className="bg-slate-900">Security & Compliance</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {loadingDocs ? (
              <div className="col-span-3 py-12 text-center text-slate-500">
                <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                Loading indexed documents...
              </div>
            ) : documents.length === 0 ? (
              <div className="col-span-3 py-12 text-center text-slate-500">
                No documents found in knowledge base.
              </div>
            ) : (
              documents.map((doc) => (
                <div
                  key={doc.id}
                  className="bg-slate-950/60 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div className="w-9 h-9 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold text-xs">
                        {doc.file_type === 'PDF' ? (
                          <FileText className="w-4 h-4 text-red-400" />
                        ) : doc.file_type === 'DOCX' ? (
                          <FileText className="w-4 h-4 text-blue-400" />
                        ) : (
                          <FileCode className="w-4 h-4 text-emerald-400" />
                        )}
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-slate-800 text-slate-300 border border-slate-700">
                        {doc.category}
                      </span>
                    </div>

                    <div>
                      <h4 className="font-bold text-sm text-white line-clamp-1">{doc.title}</h4>
                      <p className="text-[11px] text-slate-400 font-mono truncate mt-0.5">{doc.filename}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-2 p-2.5 bg-slate-900/60 rounded-xl border border-slate-800/80 font-mono text-[10px] text-slate-400">
                      <div>
                        <span>Chunks:</span> <span className="font-bold text-white">{doc.total_chunks}</span>
                      </div>
                      <div>
                        <span>Tokens:</span> <span className="font-bold text-white">{doc.total_tokens}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between">
                    <button
                      onClick={() => handleInspectChunks(doc.id)}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Inspect Chunks
                    </button>
                    {canManageDocs && (
                      <button
                        onClick={(e) => handleDeleteDocument(doc.id, e)}
                        className="p-1.5 hover:bg-slate-800 text-slate-500 hover:text-red-400 rounded-lg transition-colors"
                        title="Delete Document"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Vector Chunk Inspector Modal */}
        {selectedDoc && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-3xl w-full shadow-2xl space-y-5 max-h-[85vh] flex flex-col">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Hash className="w-4 h-4 text-blue-500" />
                    Vector Chunks Inspector: {selectedDoc.title}
                  </h3>
                  <p className="text-[11px] text-slate-400 font-mono mt-0.5">
                    {selectedDoc.total_chunks} Chunks &bull; {selectedDoc.total_tokens} Tokens &bull; Dimension: 32-D Vectors
                  </p>
                </div>
                <button onClick={() => setSelectedDoc(null)} className="text-slate-400 hover:text-white font-bold">&times;</button>
              </div>

              <div className="flex-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
                {selectedDoc.chunks.map((c) => (
                  <div key={c.id} className="p-4 bg-slate-950 border border-slate-800 rounded-2xl space-y-2 text-xs">
                    <div className="flex items-center justify-between font-mono text-[10px]">
                      <span className="font-bold text-blue-400">Chunk #{c.chunk_index} (Page {c.page_number})</span>
                      <span className="text-slate-400">{c.token_count} tokens</span>
                    </div>
                    {c.section_heading && (
                      <p className="font-bold text-slate-200 text-xs">{c.section_heading}</p>
                    )}
                    <p className="text-slate-300 leading-relaxed text-xs">{c.content}</p>

                    {/* Vector preview heatmap pills */}
                    <div className="pt-2 border-t border-slate-800/80 flex items-center gap-1.5 flex-wrap">
                      <span className="text-[9px] text-slate-500 font-mono">Vector Snapshot:</span>
                      {c.embedding_preview.map((val, v_idx) => (
                        <span
                          key={v_idx}
                          className="px-1.5 py-0.5 rounded text-[9px] font-mono font-bold bg-blue-500/10 text-blue-300 border border-blue-500/20"
                        >
                          {val.toFixed(2)}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-3 border-t border-slate-800 flex justify-end">
                <button
                  onClick={() => setSelectedDoc(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-semibold"
                >
                  Close Inspector
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Upload Modal */}
        {showUploadModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Upload className="w-5 h-5 text-blue-500" />
                  Index Unstructured Document into Vector Store
                </h3>
                <button onClick={() => setShowUploadModal(false)} className="text-slate-400 hover:text-white font-bold">&times;</button>
              </div>

              <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Document Title</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Enterprise Cloud Privacy Policy 2026"
                    value={uploadTitle}
                    onChange={(e) => setUploadTitle(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500 font-medium"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Document Category</label>
                  <select
                    value={uploadCategory}
                    onChange={(e) => setUploadCategory(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="POLICY">Policy & Governance</option>
                    <option value="FINANCIAL_FILING">Financial Filing</option>
                    <option value="SLA_CONTRACT">SLA & Contract</option>
                    <option value="SECURITY_COMPLIANCE">Security & Compliance</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Select File (PDF, DOCX, TXT, MD)</label>
                  <input
                    type="file"
                    required
                    accept=".pdf,.docx,.txt,.md"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono file:mr-4 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer"
                  />
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowUploadModal(false)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={uploading || !uploadFile}
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-600/20 disabled:opacity-40 flex items-center gap-1.5"
                  >
                    {uploading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Upload className="w-3.5 h-3.5" />}
                    {uploading ? 'Chunking & Indexing...' : 'Upload & Index'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </EnterpriseShell>
  );
}
