'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import { GeneratedReport } from '@/types/platform';
import {
  FileSpreadsheet,
  FileText,
  Download,
  FileCheck,
  Calendar,
  Sparkles,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Clock,
  Printer,
  Shield,
  Layers,
} from 'lucide-react';

export default function ReportsPage() {
  const { user } = useAuth();
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [loadingList, setLoadingList] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Form State
  const [title, setTitle] = useState('Executive Decision Intelligence Briefing');
  const [reportType, setReportType] = useState('EXECUTIVE_SUMMARY');
  const [format, setFormat] = useState<'PDF' | 'EXCEL' | 'CSV'>('PDF');
  const [dateRange, setDateRange] = useState('Q1 2026');
  const [notes, setNotes] = useState(
    'Quarterly enterprise performance indicates sustained revenue growth, positive net margin expansion, and optimal inventory turnover velocity across all operational sectors.'
  );

  const fetchReports = async () => {
    setLoadingList(true);
    try {
      const res = await apiClient.get<GeneratedReport[]>('/reports');
      setReports(res.data || []);
    } catch (err) {
      console.error('Error fetching reports:', err);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleGenerateReport = async (e: React.FormEvent) => {
    e.preventDefault();
    setGenerating(true);
    try {
      const res = await apiClient.post('/reports/generate', {
        title,
        report_type: reportType,
        format,
        date_range: dateRange,
        executive_summary_notes: notes,
      });
      setNotification({
        message: `Successfully generated ${format} document: '${res.data.title}'`,
        type: 'success',
      });
      fetchReports();
    } catch (err: any) {
      setNotification({
        message: err.response?.data?.detail || 'Failed to render enterprise report.',
        type: 'error',
      });
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = (report: GeneratedReport) => {
    const url = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/reports/${report.id}/download`;
    window.open(url, '_blank');
  };

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-2">
              <FileSpreadsheet className="w-3.5 h-3.5" />
              <span>Automated Report & Document Generator</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise Report Generator</h1>
            <p className="text-xs text-slate-400 mt-1">
              Produce boardroom-ready PDF briefs via ReportLab, structured multi-sheet Excel workbooks via OpenPyXL, and clean CSV datasets.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchReports}
              disabled={loadingList}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Reports"
            >
              <RefreshCw className={`w-4 h-4 ${loadingList ? 'animate-spin' : ''}`} />
            </button>
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

        {/* Generation Studio: Form & Live Document Preview */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Generator Form */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Printer className="w-4 h-4 text-blue-500" />
                Report Document Configuration
              </h3>
              <span className="text-[11px] text-slate-400 font-mono">Engine: ReportLab / OpenPyXL</span>
            </div>

            <form onSubmit={handleGenerateReport} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Document Title</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500 font-medium"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Report Template</label>
                  <select
                    value={reportType}
                    onChange={(e) => setReportType(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500 font-medium"
                  >
                    <option value="EXECUTIVE_SUMMARY">Executive Decision Summary</option>
                    <option value="FINANCIAL_HEALTH">Financial Health & Audit</option>
                    <option value="OPERATIONAL_AUDIT">Operational & Supply Chain Audit</option>
                    <option value="DATA_QUALITY">Data Quality & Governance Audit</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Date Horizon</label>
                  <select
                    value={dateRange}
                    onChange={(e) => setDateRange(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500 font-medium"
                  >
                    <option value="Q1 2026">Q1 2026 (Current Quarter)</option>
                    <option value="Q4 2025">Q4 2025 (Previous Quarter)</option>
                    <option value="FY 2025">FY 2025 (Full Fiscal Year)</option>
                    <option value="YTD 2026">YTD 2026 (Year to Date)</option>
                  </select>
                </div>
              </div>

              {/* Format Selector Pills */}
              <div>
                <label className="block text-slate-400 font-semibold mb-2">Export Document Format</label>
                <div className="grid grid-cols-3 gap-3">
                  {[
                    { id: 'PDF', label: 'PDF Document', desc: 'Boardroom Layout', icon: FileText, color: 'text-red-400' },
                    { id: 'EXCEL', label: 'Excel Workbook', desc: 'Multi-Tab Formulas', icon: FileSpreadsheet, color: 'text-emerald-400' },
                    { id: 'CSV', label: 'CSV Raw Data', desc: 'Dataset Extract', icon: FileCheck, color: 'text-blue-400' },
                  ].map((f) => (
                    <button
                      key={f.id}
                      type="button"
                      onClick={() => setFormat(f.id as any)}
                      className={`p-3 rounded-2xl border text-left transition-all ${
                        format === f.id
                          ? 'bg-blue-600/20 border-blue-500 text-white'
                          : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                      }`}
                    >
                      <f.icon className={`w-5 h-5 mb-1 ${f.color}`} />
                      <p className="font-bold text-xs text-white">{f.label}</p>
                      <p className="text-[10px] text-slate-400">{f.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Executive Summary Briefing Notes</label>
                <textarea
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div className="pt-2">
                <button
                  type="submit"
                  disabled={generating}
                  className="w-full py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-xl font-bold shadow-lg shadow-emerald-600/20 transition-all disabled:opacity-40 flex items-center justify-center gap-2 text-xs"
                >
                  {generating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Printer className="w-4 h-4" />}
                  {generating ? 'Rendering Executive Document...' : `Generate & Save ${format} Report`}
                </button>
              </div>
            </form>
          </div>

          {/* Right: Live Interactive Document Layout Preview */}
          <div className="bg-slate-950 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between space-y-4">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Live Document Header Preview</span>
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 font-mono">
                  {format} ENGINE
                </span>
              </div>

              {/* Mock PDF / Excel page card */}
              <div className="bg-white text-slate-900 rounded-2xl p-6 shadow-2xl space-y-4 font-sans text-xs">
                <div className="border-b border-slate-200 pb-3">
                  <span className="text-[10px] uppercase font-bold text-blue-600 tracking-wider">AEGISIQ ENTERPRISE DECISION PLATFORM</span>
                  <h4 className="text-lg font-bold text-slate-900 leading-tight mt-1">{title}</h4>
                  <p className="text-[10px] text-slate-500 font-mono mt-0.5">
                    Horizon: {dateRange} &bull; Classification: Enterprise Confidential
                  </p>
                </div>

                <div>
                  <h5 className="font-bold text-slate-800 text-[11px] mb-1">1. Executive Briefing</h5>
                  <p className="text-slate-600 text-[11px] leading-relaxed line-clamp-3">{notes}</p>
                </div>

                <div>
                  <h5 className="font-bold text-slate-800 text-[11px] mb-1">2. Core Enterprise Scorecard</h5>
                  <div className="grid grid-cols-3 gap-2 text-[10px] font-mono">
                    <div className="p-2 bg-slate-100 rounded-lg">
                      <span className="text-slate-500 block">ARR</span>
                      <span className="font-bold text-slate-900 text-xs">$24.8M (+18.4%)</span>
                    </div>
                    <div className="p-2 bg-slate-100 rounded-lg">
                      <span className="text-slate-500 block">Gross Margin</span>
                      <span className="font-bold text-slate-900 text-xs">68.4% (Healthy)</span>
                    </div>
                    <div className="p-2 bg-slate-100 rounded-lg">
                      <span className="text-slate-500 block">Net Retention</span>
                      <span className="font-bold text-slate-900 text-xs">118.5% (NRR)</span>
                    </div>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[9px] text-slate-400 font-mono">
                  <span>Signed & Certified by AegisIQ Backend</span>
                  <span>Page 1 of 1</span>
                </div>
              </div>
            </div>

            <p className="text-[11px] text-slate-500 text-center font-mono">
              Rendered directly using server-side Python ReportLab & OpenPyXL binaries.
            </p>
          </div>
        </div>

        {/* Previously Generated Reports Table */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <FileCheck className="w-4 h-4 text-emerald-400" />
              Generated Document Repository
            </h3>
            <span className="text-xs text-slate-400 font-mono">{reports.length} files available</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 uppercase font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Document Title</th>
                  <th className="py-3 px-4">Report Type</th>
                  <th className="py-3 px-4">Format</th>
                  <th className="py-3 px-4">File Size</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4 text-right">Download</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {loadingList ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-500">
                      <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                      Loading report repository...
                    </td>
                  </tr>
                ) : reports.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-500">
                      No reports generated yet. Click 'Generate & Save Report' above.
                    </td>
                  </tr>
                ) : (
                  reports.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3.5 px-4 font-semibold text-white flex items-center gap-2">
                        {r.format === 'PDF' ? (
                          <FileText className="w-4 h-4 text-red-400 shrink-0" />
                        ) : r.format === 'EXCEL' ? (
                          <FileSpreadsheet className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : (
                          <FileCheck className="w-4 h-4 text-blue-400 shrink-0" />
                        )}
                        {r.title}
                      </td>
                      <td className="py-3.5 px-4 text-slate-300 font-mono text-[11px]">{r.report_type}</td>
                      <td className="py-3.5 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                            r.format === 'PDF'
                              ? 'bg-red-500/10 text-red-400 border border-red-500/20'
                              : r.format === 'EXCEL'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                          }`}
                        >
                          {r.format}
                        </span>
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                        {(r.file_size_bytes / 1024).toFixed(1)} KB
                      </td>
                      <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                        {new Date(r.created_at).toLocaleString()}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <button
                          onClick={() => handleDownload(r)}
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600/20 hover:bg-blue-600 text-blue-300 hover:text-white rounded-lg text-xs font-semibold transition-all border border-blue-500/30"
                        >
                          <Download className="w-3.5 h-3.5" />
                          Download
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </EnterpriseShell>
  );
}
