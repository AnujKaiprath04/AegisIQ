'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import { DatasetDetail, DatasetPreview, DatasetSummary } from '@/types/platform';
import {
  Database,
  Upload,
  FileSpreadsheet,
  FileText,
  Table as TableIcon,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  Sparkles,
  RefreshCw,
  Search,
  Eye,
  Trash2,
  AlertCircle,
  BarChart2,
  Shield,
} from 'lucide-react';

export default function DatasetsPage() {
  const { user, hasRole } = useAuth();
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(null);
  const [selectedDetail, setSelectedDetail] = useState<DatasetDetail | null>(null);
  const [previewData, setPreviewData] = useState<DatasetPreview | null>(null);
  
  const [loadingList, setLoadingList] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [activeTab, setActiveTab] = useState<'preview' | 'schema'>('preview');

  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Upload form
  const [uploadName, setUploadName] = useState('');
  const [uploadDesc, setUploadDesc] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const fetchDatasets = async () => {
    setLoadingList(true);
    try {
      const res = await apiClient.get<DatasetSummary[]>('/datasets');
      setDatasets(res.data || []);
      if (res.data && res.data.length > 0 && !selectedDatasetId) {
        selectDataset(res.data[0].id);
      }
    } catch (err: any) {
      console.error('Error fetching datasets:', err);
    } finally {
      setLoadingList(false);
    }
  };

  const selectDataset = async (id: number) => {
    setSelectedDatasetId(id);
    setLoadingDetail(true);
    setLoadingPreview(true);
    try {
      const [detailRes, previewRes] = await Promise.all([
        apiClient.get<DatasetDetail>(`/datasets/${id}`),
        apiClient.get<DatasetPreview>(`/datasets/${id}/preview?limit=50`),
      ]);
      setSelectedDetail(detailRes.data);
      setPreviewData(previewRes.data);
    } catch (err: any) {
      setNotification({ message: 'Failed to load dataset details or preview.', type: 'error' });
    } finally {
      setLoadingDetail(false);
      setLoadingPreview(false);
    }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    if (uploadName) formData.append('name', uploadName);
    if (uploadDesc) formData.append('description', uploadDesc);

    try {
      const res = await apiClient.post('/datasets/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setNotification({ message: res.data.message || 'Dataset uploaded and registered successfully!', type: 'success' });
      setSelectedFile(null);
      setUploadName('');
      setUploadDesc('');
      fetchDatasets();
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Failed to upload dataset.', type: 'error' });
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDataset = async (id: number, name: string) => {
    if (!confirm(`Delete dataset '${name}' and its underlying files?`)) return;
    try {
      await apiClient.delete(`/datasets/${id}`);
      setNotification({ message: `Dataset '${name}' removed.`, type: 'success' });
      if (selectedDatasetId === id) {
        setSelectedDatasetId(null);
        setSelectedDetail(null);
        setPreviewData(null);
      }
      fetchDatasets();
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Failed to delete dataset.', type: 'error' });
    }
  };

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-400 text-xs font-semibold mb-2">
              <Database className="w-3.5 h-3.5" />
              <span>Enterprise Data Ingestion & Catalog</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise Datasets Repository</h1>
            <p className="text-xs text-slate-400 mt-1">
              Ingest multi-format files (CSV, XLSX, JSON), auto-introspect schemas, inspect data distributions, and monitor quality scores.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchDatasets}
              disabled={loadingList}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Repository"
            >
              <RefreshCw className={`w-4 h-4 ${loadingList ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Notifications */}
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

        {/* Ingestion Upload Card */}
        {hasRole(['Admin', 'Data Analyst', 'Business Analyst']) && (
          <div className="bg-slate-900/60 border border-slate-800 rounded-3xl p-6 shadow-xl">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
              <Upload className="w-4 h-4 text-blue-400" />
              Ingest Structured Enterprise Dataset
            </h3>
            <form onSubmit={handleFileUpload} className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
              <div className="md:col-span-1">
                <label className="block text-slate-400 font-semibold mb-1">Select File (CSV, XLSX, JSON)</label>
                <input
                  type="file"
                  required
                  accept=".csv,.xlsx,.xls,.json"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) {
                      setSelectedFile(f);
                      if (!uploadName) setUploadName(f.name.replace(/\.[^/.]+$/, ''));
                    }
                  }}
                  className="w-full text-slate-400 file:mr-3 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer bg-slate-950 p-1.5 rounded-xl border border-slate-800"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Dataset Label</label>
                <input
                  type="text"
                  placeholder="e.g. Sales Ledger 2026"
                  value={uploadName}
                  onChange={(e) => setUploadName(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Description / Notes</label>
                <input
                  type="text"
                  placeholder="e.g. Q1 enterprise contracts"
                  value={uploadDesc}
                  onChange={(e) => setUploadDesc(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="flex items-end">
                <button
                  type="submit"
                  disabled={uploading || !selectedFile}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-600/20 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {uploading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                  {uploading ? 'Processing Ingestion...' : 'Upload & Introspect'}
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Main 2-Column Catalog and Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column: Dataset List Cards */}
          <div className="space-y-3">
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider px-1">Registered Datasets ({datasets.length})</h2>
            {loadingList ? (
              <div className="p-8 text-center text-slate-500 bg-slate-900/40 rounded-2xl border border-slate-800">
                <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                Loading dataset catalog...
              </div>
            ) : datasets.length === 0 ? (
              <div className="p-8 text-center text-slate-500 bg-slate-900/40 rounded-2xl border border-slate-800">
                No datasets registered yet.
              </div>
            ) : (
              datasets.map((ds) => {
                const isSelected = selectedDatasetId === ds.id;
                return (
                  <div
                    key={ds.id}
                    onClick={() => selectDataset(ds.id)}
                    className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                      isSelected
                        ? 'bg-blue-950/40 border-blue-600/80 shadow-lg shadow-blue-900/20'
                        : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-3 mb-2">
                      <div className="flex items-center gap-2.5">
                        <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold text-xs shrink-0">
                          {ds.file_format.toUpperCase()}
                        </div>
                        <div>
                          <h4 className="text-xs font-bold text-white line-clamp-1">{ds.name}</h4>
                          <p className="text-[10px] text-slate-400">{ds.source_type}</p>
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {ds.quality_score}% Quality
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-400 line-clamp-2 mb-3">
                      {ds.description || 'Enterprise dataset registered in data warehouse.'}
                    </p>

                    <div className="flex items-center justify-between pt-2 border-t border-slate-800/80 text-[10px] text-slate-400 font-mono">
                      <span>{ds.row_count.toLocaleString()} rows &bull; {ds.column_count} cols</span>
                      <span>{(ds.file_size_bytes / 1024).toFixed(1)} KB</span>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Right Column: Schema Inspector & Tabular Preview */}
          <div className="lg:col-span-2 space-y-4">
            {selectedDetail ? (
              <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-6">
                {/* Header Summary */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                  <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <Database className="w-5 h-5 text-blue-500" />
                      {selectedDetail.name}
                    </h3>
                    <p className="text-xs text-slate-400 mt-0.5">{selectedDetail.description}</p>
                  </div>

                  <div className="flex items-center gap-2">
                    <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
                      <button
                        onClick={() => setActiveTab('preview')}
                        className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                          activeTab === 'preview' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        Data Preview
                      </button>
                      <button
                        onClick={() => setActiveTab('schema')}
                        className={`px-3 py-1 rounded-lg font-semibold transition-all ${
                          activeTab === 'schema' ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        Schema ({selectedDetail.column_count} Cols)
                      </button>
                    </div>

                    {hasRole(['Admin', 'Data Analyst']) && (
                      <button
                        onClick={() => handleDeleteDataset(selectedDetail.id, selectedDetail.name)}
                        className="p-2 hover:bg-red-500/10 text-slate-400 hover:text-red-400 rounded-xl border border-slate-800 transition-colors"
                        title="Delete Dataset"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Tab 1: Data Preview Table */}
                {activeTab === 'preview' && (
                  <div>
                    {loadingPreview ? (
                      <div className="py-16 text-center text-slate-500">
                        <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                        Rendering tabular slice...
                      </div>
                    ) : previewData && previewData.rows.length > 0 ? (
                      <div className="overflow-x-auto border border-slate-800 rounded-2xl">
                        <table className="w-full text-left text-xs">
                          <thead className="bg-slate-950/80 text-slate-400 uppercase font-semibold border-b border-slate-800">
                            <tr>
                              {previewData.columns.map((col) => (
                                <th key={col} className="py-3 px-4 whitespace-nowrap">
                                  {col}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/60 font-mono">
                            {previewData.rows.map((row, idx) => (
                              <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                                {previewData.columns.map((col) => (
                                  <td key={col} className="py-2.5 px-4 whitespace-nowrap text-slate-300">
                                    {row[col] !== null && row[col] !== undefined ? String(row[col]) : <span className="text-slate-600">null</span>}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 py-8 text-center">No data preview records available.</p>
                    )}
                  </div>
                )}

                {/* Tab 2: Column Schema Inspector */}
                {activeTab === 'schema' && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {selectedDetail.columns.map((c) => (
                      <div key={c.name} className="bg-slate-950/60 border border-slate-800/80 rounded-2xl p-4 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-xs text-white font-mono">{c.name}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase">
                            {c.data_type}
                          </span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
                          <div>
                            <span className="text-slate-500">Null Count:</span> {c.null_count} ({c.null_percentage}%)
                          </div>
                          <div>
                            <span className="text-slate-500">Uniques:</span> {c.unique_count}
                          </div>
                          {c.min_value !== null && (
                            <div>
                              <span className="text-slate-500">Min:</span> {c.min_value}
                            </div>
                          )}
                          {c.max_value !== null && (
                            <div>
                              <span className="text-slate-500">Max:</span> {c.max_value}
                            </div>
                          )}
                        </div>

                        {c.sample_values && c.sample_values.length > 0 && (
                          <div className="text-[10px] text-slate-400 bg-slate-900/60 p-2 rounded-lg font-mono truncate">
                            <span className="text-slate-500">Samples:</span> {c.sample_values.join(', ')}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-12 text-center text-slate-500">
                <Layers className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                Select a dataset on the left to inspect its schema and data preview.
              </div>
            )}
          </div>
        </div>
      </div>
    </EnterpriseShell>
  );
}
