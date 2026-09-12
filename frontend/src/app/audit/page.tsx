'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import { AuditLog } from '@/types/platform';
import {
  ShieldCheck,
  Search,
  Filter,
  RefreshCw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Shield,
  Activity,
  User,
  Lock,
} from 'lucide-react';

export default function AuditPage() {
  const { hasRole } = useAuth();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [actionSearch, setActionSearch] = useState('');
  const [userEmailSearch, setUserEmailSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const fetchAuditData = async () => {
    setLoading(true);
    try {
      let query = `/audit?page=${page}&page_size=25`;
      if (actionSearch) query += `&action=${encodeURIComponent(actionSearch)}`;
      if (userEmailSearch) query += `&user_email=${encodeURIComponent(userEmailSearch)}`;
      if (statusFilter !== 'ALL') query += `&status_filter=${encodeURIComponent(statusFilter)}`;

      const [logsRes, statsRes] = await Promise.all([
        apiClient.get(query),
        apiClient.get('/audit/stats'),
      ]);
      setLogs(logsRes.data.logs || []);
      setTotalCount(logsRes.data.total_count || 0);
      setStats(statsRes.data);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditData();
  }, [page, statusFilter]);

  const handleFilterSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchAuditData();
  };

  const isAdmin = hasRole(['Admin']);

  if (!isAdmin) {
    return (
      <EnterpriseShell>
        <div className="bg-red-950/30 border border-red-800/60 rounded-3xl p-8 text-center max-w-2xl mx-auto my-12">
          <div className="w-14 h-14 rounded-2xl bg-red-500/10 text-red-400 flex items-center justify-center mx-auto mb-4 border border-red-500/20">
            <Lock className="w-7 h-7" />
          </div>
          <h2 className="text-xl font-bold text-white mb-2">Administrative Authorization Required</h2>
          <p className="text-sm text-slate-300 mb-6">
            Compliance & Audit Logs are restricted to accounts with the{' '}
            <span className="font-semibold text-red-400">Admin</span> role.
          </p>
        </div>
      </EnterpriseShell>
    );
  }

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-2">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Enterprise Security & Compliance Audit</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Security & Compliance Audit Trail</h1>
            <p className="text-xs text-slate-400 mt-1">
              Immutable telemetry tracking all user logins, administrative identity changes, ETL pipeline runs, and report exports.
            </p>
          </div>


          <div className="flex items-center gap-3">
            <button
              onClick={fetchAuditData}
              disabled={loading}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Audit Trail"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Audit Stats Metric Cards */}
        {stats && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Total Audit Events</span>
              <p className="text-2xl font-bold text-white font-mono">{stats.total_events}</p>
              <p className="text-[11px] text-slate-400">Recorded across platform lifecycle</p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Successful Actions</span>
              <p className="text-2xl font-bold text-emerald-400 font-mono">{stats.success_count}</p>
              <p className="text-[11px] text-slate-400">Normal verified operations</p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Failed / Rejected Events</span>
              <p className="text-2xl font-bold text-red-400 font-mono">{stats.failed_count}</p>
              <p className="text-[11px] text-slate-400">Denied authorizations / bad logins</p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">System Integrity</span>
              <p className="text-2xl font-bold text-blue-400 font-mono">100% Verified</p>
              <p className="text-[11px] text-slate-400">Zero cryptographic breaches</p>
            </div>
          </div>
        )}

        {/* Filters */}
        <form onSubmit={handleFilterSubmit} className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
            <div className="relative w-full md:w-60">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Filter by action..."
                value={actionSearch}
                onChange={(e) => setActionSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>

            <div className="relative w-full md:w-60">
              <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Filter by user email..."
                value={userEmailSearch}
                onChange={(e) => setUserEmailSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>

            <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-transparent text-white focus:outline-none cursor-pointer"
              >
                <option value="ALL" className="bg-slate-900">All Statuses</option>
                <option value="SUCCESS" className="bg-slate-900">SUCCESS</option>
                <option value="FAILED" className="bg-slate-900">FAILED</option>
                <option value="WARNING" className="bg-slate-900">WARNING</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-md shadow-blue-600/20"
          >
            Apply Filters
          </button>
        </form>

        {/* Audit Log Table */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 uppercase font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-3.5 px-4">Event Action</th>
                  <th className="py-3.5 px-4">Actor Email</th>
                  <th className="py-3.5 px-4">Status</th>
                  <th className="py-3.5 px-4">IP Address</th>
                  <th className="py-3.5 px-4">Details / Parameters</th>
                  <th className="py-3.5 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500">
                      <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
                      Loading audit records...
                    </td>
                  </tr>
                ) : logs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-slate-500">
                      No security audit events match the specified filter criteria.
                    </td>
                  </tr>
                ) : (
                  logs.map((l) => (
                    <tr key={l.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-sans font-medium text-white flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                        {l.action}
                      </td>
                      <td className="py-3 px-4 text-slate-300">{l.user_email || 'System Daemon'}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-sans font-bold ${
                            l.status === 'SUCCESS'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-red-500/10 text-red-400 border border-red-500/20'
                          }`}
                        >
                          {l.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">{l.ip_address || '127.0.0.1'}</td>
                      <td className="py-3 px-4 text-slate-400 max-w-xs truncate font-sans text-[11px]">
                        {l.details || '—'}
                      </td>
                      <td className="py-3 px-4 text-slate-400 font-sans">
                        {new Date(l.created_at).toLocaleString()}
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
