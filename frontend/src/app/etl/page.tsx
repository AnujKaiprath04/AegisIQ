'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import { DataQualityReport, DatasetSummary, ETLRun } from '@/types/platform';
import {
  Workflow,
  Sparkles,
  Play,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldCheck,
  RefreshCw,
  Sliders,
  Terminal,
  Activity,
  Layers,
  Database,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';

export default function ETLPage() {
  const { hasRole } = useAuth();
  const [datasets, setDatasets] = useState<DatasetSummary[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(null);
  const [qualityReport, setQualityReport] = useState<DataQualityReport | null>(null);
  const [recentRuns, setRecentRuns] = useState<ETLRun[]>([]);
  
  const [loadingDatasets, setLoadingDatasets] = useState(true);
  const [loadingReport, setLoadingReport] = useState(false);
  const [runningPipeline, setRunningPipeline] = useState(false);
  const [liveLogs, setLiveLogs] = useState<string>('');

  // ETL Config Form
  const [config, setConfig] = useState({
    pipeline_name: 'Automated 4-Pillar Quality Cleaning Pipeline',
    remove_duplicates: true,
    handle_missing: true,
    missing_strategy: 'auto',
    handle_outliers: true,
    outlier_method: 'iqr',
    outlier_action: 'clip',
    standardize_headers: true,
  });

  const fetchInitialData = async () => {
    setLoadingDatasets(true);
    try {
      const [dsRes, runsRes] = await Promise.all([
        apiClient.get<DatasetSummary[]>('/datasets'),
        apiClient.get<ETLRun[]>('/etl/runs?limit=10'),
      ]);
      setDatasets(dsRes.data || []);
      setRecentRuns(runsRes.data || []);
      if (dsRes.data && dsRes.data.length > 0) {
        setSelectedDatasetId(dsRes.data[0].id);
        fetchQualityReport(dsRes.data[0].id);
      }
    } catch (err) {
      console.error('Error fetching ETL initial data:', err);
    } finally {
      setLoadingDatasets(false);
    }
  };

  const fetchQualityReport = async (dsId: number) => {
    setLoadingReport(true);
    try {
      const res = await apiClient.get<DataQualityReport>(`/etl/quality-report/${dsId}`);
      setQualityReport(res.data);
    } catch (err) {
      console.error('Error loading quality scorecard:', err);
    } finally {
      setLoadingReport(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const handleRunETL = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDatasetId) return;

    setRunningPipeline(true);
    setLiveLogs('Initializing ETL execution worker...\nVerifying schema integrity...\nApplying transformation rules...');

    try {
      const res = await apiClient.post<ETLRun>('/etl/clean', {
        dataset_id: selectedDatasetId,
        ...config,
      });
      setLiveLogs(res.data.log_output || 'Pipeline completed successfully.');
      fetchQualityReport(selectedDatasetId);
      
      // Refresh runs
      const runsRes = await apiClient.get<ETLRun[]>('/etl/runs?limit=10');
      setRecentRuns(runsRes.data || []);
    } catch (err: any) {
      setLiveLogs(`ERROR: Pipeline execution failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setRunningPipeline(false);
    }
  };

  const canExecuteETL = hasRole(['Admin', 'Data Analyst']);

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold mb-2">
              <Workflow className="w-3.5 h-3.5" />
              <span>ETL Engine & Quality Assurance</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">ETL Pipeline & Data Quality Studio</h1>
            <p className="text-xs text-slate-400 mt-1">
              Configure data cleaning transformations, execute automated deduplication, impute missing records, and assess 4-pillar quality scorecards.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={selectedDatasetId || ''}
              onChange={(e) => {
                const id = Number(e.target.value);
                setSelectedDatasetId(id);
                fetchQualityReport(id);
              }}
              className="px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white focus:outline-none focus:border-blue-500"
            >
              {datasets.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name} ({d.row_count} rows)
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* 4-Pillar Quality Scorecards */}
        {qualityReport && (
          <div>
            <div className="flex items-center justify-between mb-3 px-1">
              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Enterprise 4-Pillar Quality Scorecard ({qualityReport.dataset_name})
              </h2>
              <span className="text-xs font-bold text-emerald-400 flex items-center gap-1.5 font-mono">
                Overall Health: {qualityReport.overall_score}%
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Completeness */}
              <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400">1. Completeness</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    {qualityReport.completeness.status}
                  </span>
                </div>
                <div className="text-2xl font-bold text-white font-mono">{qualityReport.completeness.score}%</div>
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${qualityReport.completeness.score}%` }} />
                </div>
                <p className="text-[11px] text-slate-400 leading-tight">{qualityReport.completeness.details}</p>
              </div>

              {/* Uniqueness */}
              <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400">2. Uniqueness</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20">
                    {qualityReport.uniqueness.status}
                  </span>
                </div>
                <div className="text-2xl font-bold text-white font-mono">{qualityReport.uniqueness.score}%</div>
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-purple-500 h-1.5 rounded-full" style={{ width: `${qualityReport.uniqueness.score}%` }} />
                </div>
                <p className="text-[11px] text-slate-400 leading-tight">{qualityReport.uniqueness.details}</p>
              </div>

              {/* Validity */}
              <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400">3. Validity</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    {qualityReport.validity.status}
                  </span>
                </div>
                <div className="text-2xl font-bold text-white font-mono">{qualityReport.validity.score}%</div>
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-emerald-500 h-1.5 rounded-full" style={{ width: `${qualityReport.validity.score}%` }} />
                </div>
                <p className="text-[11px] text-slate-400 leading-tight">{qualityReport.validity.details}</p>
              </div>

              {/* Consistency */}
              <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold text-slate-400">4. Consistency</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                    {qualityReport.consistency.status}
                  </span>
                </div>
                <div className="text-2xl font-bold text-white font-mono">{qualityReport.consistency.score}%</div>
                <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                  <div className="bg-amber-500 h-1.5 rounded-full" style={{ width: `${qualityReport.consistency.score}%` }} />
                </div>
                <p className="text-[11px] text-slate-400 leading-tight">{qualityReport.consistency.details}</p>
              </div>
            </div>
          </div>
        )}

        {/* Pipeline Builder & Live Execution Terminal */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Transformation Configurator */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Sliders className="w-4 h-4 text-blue-500" />
                Pipeline Rule Configurator
              </h3>
              <span className="text-[11px] text-slate-400 font-mono">FastAPI / Pandas Engine</span>
            </div>

            <form onSubmit={handleRunETL} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Pipeline Run Identifier</label>
                <input
                  type="text"
                  value={config.pipeline_name}
                  onChange={(e) => setConfig({ ...config, pipeline_name: e.target.value })}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4 bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.remove_duplicates}
                    onChange={(e) => setConfig({ ...config, remove_duplicates: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600 focus:ring-0 bg-slate-900 border-slate-700"
                  />
                  <span className="text-slate-200 font-medium">Remove Duplicate Rows</span>
                </label>

                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={config.standardize_headers}
                    onChange={(e) => setConfig({ ...config, standardize_headers: e.target.checked })}
                    className="w-4 h-4 rounded text-blue-600 focus:ring-0 bg-slate-900 border-slate-700"
                  />
                  <span className="text-slate-200 font-medium">Normalize Column Names</span>
                </label>
              </div>

              {/* Missing Values Strategy */}
              <div className="space-y-2 bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.handle_missing}
                      onChange={(e) => setConfig({ ...config, handle_missing: e.target.checked })}
                      className="w-4 h-4 rounded text-blue-600 focus:ring-0 bg-slate-900 border-slate-700"
                    />
                    <span className="text-slate-200 font-medium">Missing Value Imputation</span>
                  </label>
                </div>
                {config.handle_missing && (
                  <div className="pt-2">
                    <select
                      value={config.missing_strategy}
                      onChange={(e) => setConfig({ ...config, missing_strategy: e.target.value })}
                      className="w-full px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-xl text-white text-xs"
                    >
                      <option value="auto">Auto-Select (Mean for numeric, Mode for text)</option>
                      <option value="mean">Mean Imputation</option>
                      <option value="median">Median Imputation</option>
                      <option value="ffill">Forward-fill / Backfill</option>
                      <option value="drop">Drop Rows with Nulls</option>
                    </select>
                  </div>
                )}
              </div>

              {/* Outliers Strategy */}
              <div className="space-y-2 bg-slate-950/60 p-4 rounded-2xl border border-slate-800">
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={config.handle_outliers}
                      onChange={(e) => setConfig({ ...config, handle_outliers: e.target.checked })}
                      className="w-4 h-4 rounded text-blue-600 focus:ring-0 bg-slate-900 border-slate-700"
                    />
                    <span className="text-slate-200 font-medium">Outlier Detection & Remediation</span>
                  </label>
                </div>
                {config.handle_outliers && (
                  <div className="grid grid-cols-2 gap-2 pt-2">
                    <select
                      value={config.outlier_method}
                      onChange={(e) => setConfig({ ...config, outlier_method: e.target.value })}
                      className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-xl text-white text-xs"
                    >
                      <option value="iqr">IQR (Interquartile 1.5x)</option>
                      <option value="zscore">Z-Score (3.0 Sigma)</option>
                    </select>
                    <select
                      value={config.outlier_action}
                      onChange={(e) => setConfig({ ...config, outlier_action: e.target.value })}
                      className="px-3 py-1.5 bg-slate-900 border border-slate-700 rounded-xl text-white text-xs"
                    >
                      <option value="clip">Clip Boundaries</option>
                      <option value="drop">Drop Outlier Rows</option>
                    </select>
                  </div>
                )}
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={runningPipeline || !canExecuteETL || !selectedDatasetId}
                  className="w-full py-3 bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-500 hover:to-orange-500 text-white rounded-xl font-bold shadow-lg shadow-amber-600/20 transition-all disabled:opacity-40 flex items-center justify-center gap-2 text-xs"
                >
                  {runningPipeline ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                  {runningPipeline ? 'Executing Transformation Pipeline...' : 'Run Pipeline & Assess Quality'}
                </button>
              </div>
            </form>
          </div>

          {/* Right: Live Terminal & Run History */}
          <div className="space-y-4">
            {/* Live Terminal */}
            <div className="bg-slate-950 border border-slate-800 rounded-3xl p-5 shadow-xl font-mono text-xs text-slate-300">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
                <span className="flex items-center gap-2 text-slate-400 font-sans font-bold">
                  <Terminal className="w-4 h-4 text-emerald-400" />
                  Live Pipeline Execution Output
                </span>
                <span className="flex items-center gap-1.5 text-[10px] text-emerald-400">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  Ready
                </span>
              </div>
              <pre className="h-44 overflow-y-auto custom-scrollbar text-[11px] leading-relaxed text-emerald-300/90 whitespace-pre-wrap">
                {liveLogs || "Pipeline output logs will appear here during execution."}
              </pre>
            </div>

            {/* Historical ETL Runs */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-5 shadow-xl">
              <h3 className="text-xs font-bold text-white mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4 text-blue-400" />
                Recent Pipeline Executions
              </h3>
              <div className="space-y-2 overflow-y-auto max-h-48 custom-scrollbar">
                {recentRuns.length === 0 ? (
                  <p className="text-xs text-slate-500 py-3 text-center">No previous ETL pipeline runs logged.</p>
                ) : (
                  recentRuns.map((r) => (
                    <div key={r.id} className="p-3 bg-slate-950/60 border border-slate-800/80 rounded-xl flex items-center justify-between text-xs">
                      <div>
                        <p className="font-semibold text-white line-clamp-1">{r.run_name}</p>
                        <p className="text-[10px] text-slate-400 font-mono">
                          {r.rows_before} &rarr; {r.rows_after} rows &bull; {r.execution_duration_ms}ms
                        </p>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                        {r.status}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </EnterpriseShell>
  );
}
