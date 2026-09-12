'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import { ActivityLog } from '@/types/auth';
import {
  Shield,
  User,
  Activity,
  Layers,
  Database,
  Workflow,
  BarChart3,
  TrendingUp,
  FileSpreadsheet,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  ArrowUpRight,
  RefreshCw,
  Users,
} from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, roles } = useAuth();
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [loadingLogs, setLoadingLogs] = useState(false);
  
  // RBAC test states
  const [rbacTestResult, setRbacTestResult] = useState<{
    endpoint: string;
    status: number | string;
    message: string;
    type: 'success' | 'error' | null;
  }>({
    endpoint: '',
    status: '',
    message: 'Click one of the test buttons above to verify live RBAC enforcement on FastAPI backend.',
    type: null,
  });

  const fetchLogs = async () => {
    setLoadingLogs(true);
    try {
      const res = await apiClient.get<ActivityLog[]>('/auth/activity-logs?limit=8');
      setLogs(res.data);
    } catch (err) {
      console.error('Error fetching activity logs:', err);
    } finally {
      setLoadingLogs(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const testEndpoint = async (path: string, label: string) => {
    try {
      const res = await apiClient.get(path);
      setRbacTestResult({
        endpoint: label,
        status: res.status,
        message: res.data.message || 'Access Authorized by Backend RBAC Engine!',
        type: 'success',
      });
      fetchLogs(); // refresh audit logs since test calls might be logged
    } catch (err: any) {
      setRbacTestResult({
        endpoint: label,
        status: err.response?.status || 500,
        message: err.response?.data?.detail || 'RBAC Authorization Failed (Access Denied).',
        type: 'error',
      });
      fetchLogs();
    }
  };

  const primaryRole = roles[0] || 'Viewer';

  return (
    <EnterpriseShell>
      <div className="space-y-8">
        {/* Welcome Banner */}
        <div className="relative overflow-hidden bg-gradient-to-r from-blue-900/60 via-indigo-900/40 to-slate-900 border border-blue-800/40 rounded-3xl p-6 sm:p-8 shadow-xl">
          <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-2">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Enterprise Decision Intelligence Platform</span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-white tracking-tight">
                Welcome, {user?.full_name || 'Enterprise User'}
              </h1>
              <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
                You are currently authenticated with the{' '}
                <span className="font-semibold text-blue-400">{primaryRole}</span> role in the{' '}
                <span className="font-medium text-slate-200">{user?.department || 'General'}</span>{' '}
                department. All enterprise modules and RBAC policies are enforced in real time.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <div className="bg-slate-900/80 border border-slate-700/60 rounded-2xl p-3.5 flex items-center gap-4">
                <div>
                  <p className="text-[11px] text-slate-400 font-medium">Session Identifier</p>
                  <p className="text-xs font-mono font-semibold text-slate-200 truncate max-w-[140px]">
                    {user?.email}
                  </p>
                </div>
                <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center">
                  <CheckCircle2 className="w-4 h-4" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats & System Status Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-slate-400">Assigned Role</span>
              <div className="w-8 h-8 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center">
                <Shield className="w-4 h-4" />
              </div>
            </div>
            <p className="text-xl font-bold text-white">{primaryRole}</p>
            <p className="text-[11px] text-slate-400 mt-1">Tier-level RBAC Policy</p>
          </div>

          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-slate-400">Authentication Mode</span>
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center">
                <User className="w-4 h-4" />
              </div>
            </div>
            <p className="text-xl font-bold text-white">JWT Bearer (HS256)</p>
            <p className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> Signed & Verified
            </p>
          </div>

          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-slate-400">Backend Engine</span>
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                <Activity className="w-4 h-4" />
              </div>
            </div>
            <p className="text-xl font-bold text-white">FastAPI 0.115</p>
            <p className="text-[11px] text-slate-400 mt-1">Python 3.13 / Clean Architecture</p>
          </div>

          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm hover:border-slate-700 transition-colors">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-medium text-slate-400">Database Engine</span>
              <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center">
                <Database className="w-4 h-4" />
              </div>
            </div>
            <p className="text-xl font-bold text-white">SQLAlchemy 2.0</p>
            <p className="text-[11px] text-slate-400 mt-1">PostgreSQL Ready / SQLite Active</p>
          </div>
        </div>

        {/* Live RBAC Enforcement Live Testing Panel */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-7 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5 mb-6">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Shield className="w-5 h-5 text-blue-500" />
                Live RBAC Enforcement Tester
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Execute authenticated requests to role-gated backend endpoints to test FastAPI security dependencies
              </p>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Your Active Role:</span>
              <span className="px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-bold font-mono">
                {primaryRole}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <button
              onClick={() =>
                testEndpoint('/auth/test-rbac/admin-only', 'Admin-Only Endpoint (/api/v1/auth/test-rbac/admin-only)')
              }
              className="p-4 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-blue-500/50 rounded-2xl text-left transition-all group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-white group-hover:text-blue-400 transition-colors">
                  Test Admin-Restricted Route
                </span>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20">
                  Requires Admin
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Tests high-privilege administrative operations. Only accessible by users with <code className="text-slate-300">Admin</code> role.
              </p>
            </button>

            <button
              onClick={() =>
                testEndpoint(
                  '/auth/test-rbac/executive-or-analyst',
                  'Executive & Analyst Route (/api/v1/auth/test-rbac/executive-or-analyst)'
                )
              }
              className="p-4 bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60 hover:border-blue-500/50 rounded-2xl text-left transition-all group"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold text-white group-hover:text-blue-400 transition-colors">
                  Test Analytical / Executive Route
                </span>
                <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  Admin / Exec / Analyst
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Tests business intelligence view authorization. Accessible by Admin, Executive, Business Analyst, Data Analyst.
              </p>
            </button>
          </div>

          {/* Live RBAC Terminal Response */}
          {rbacTestResult.endpoint && (
            <div
              className={`p-4 rounded-2xl border text-xs font-mono transition-all ${
                rbacTestResult.type === 'success'
                  ? 'bg-emerald-950/30 border-emerald-800/60 text-emerald-300'
                  : 'bg-red-950/30 border-red-800/60 text-red-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  {rbacTestResult.type === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-400 shrink-0" />
                  )}
                  <span className="font-bold">{rbacTestResult.endpoint}</span>
                </div>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    rbacTestResult.type === 'success'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  HTTP {rbacTestResult.status}
                </span>
              </div>
              <p className="text-slate-300 pl-6">{rbacTestResult.message}</p>
            </div>
          )}
        </div>

        {/* Enterprise Platform Capabilities Grid */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-lg font-bold text-white">Enterprise Platform Capabilities</h2>
              <p className="text-xs text-slate-400">
                Foundational Enterprise Platform, Data Engineering & Business Intelligence Suite
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-slate-900/60 border border-emerald-500/30 rounded-2xl p-5 flex flex-col justify-between hover:border-emerald-500/50 transition-all">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center">
                    <Shield className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    Active
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mb-1">Authentication & RBAC</h3>
                <p className="text-xs text-slate-400">
                  JWT token lifecycle, 5-tier role hierarchy, session security, password recovery, and audit tracking.
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-slate-800 text-[11px] text-emerald-400 font-medium flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> Fully Operational
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between hover:border-slate-700 transition-all">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center">
                    <Users className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    Active
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mb-1">User Management</h3>
                <p className="text-xs text-slate-400">
                  Admin user creation, updates, deactivation, role assignments, and organizational department mapping.
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-slate-800 text-[11px] text-slate-400 font-medium">
                Fully Operational
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between hover:border-slate-700 transition-all">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center">
                    <Database className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                    Active
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mb-1">Enterprise Data Management</h3>
                <p className="text-xs text-slate-400">
                  Multi-format ingestion (CSV, Excel, JSON), dataset previewing, column introspection, and profiling.
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-slate-800 text-[11px] text-slate-400 font-medium">
                Fully Operational
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between hover:border-slate-700 transition-all">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center">
                    <Workflow className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                    Active
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mb-1">ETL & Data Quality Pipeline</h3>
                <p className="text-xs text-slate-400">
                  Data transformation, cleaning, duplicate & outlier detection, column mapping, and quality reports.
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-slate-800 text-[11px] text-slate-400 font-medium">
                Fully Operational
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between hover:border-slate-700 transition-all">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center">
                    <BarChart3 className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                    Active
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mb-1">BI & Analytics Dashboards</h3>
                <p className="text-xs text-slate-400">
                  Interactive multi-chart analytics for Sales, Revenue, Customers, Inventory, and Employee performance.
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-slate-800 text-[11px] text-slate-400 font-medium">
                Fully Operational
              </div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 flex flex-col justify-between hover:border-slate-700 transition-all">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="w-9 h-9 rounded-xl bg-rose-500/10 text-rose-400 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5" />
                  </div>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                    Active
                  </span>
                </div>
                <h3 className="text-sm font-bold text-white mb-1">KPI Engine & Report Generator</h3>
                <p className="text-xs text-slate-400">
                  Automated financial/operational KPI formulas and exportable PDF, Excel, and CSV enterprise reports.
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-slate-800 text-[11px] text-slate-400 font-medium">
                Fully Operational
              </div>
            </div>
          </div>
        </div>


        {/* Security Activity & Audit Logs */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-7 shadow-xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
            <div>
              <h2 className="text-lg font-bold text-white flex items-center gap-2">
                <Clock className="w-5 h-5 text-blue-500" />
                Security Activity & Audit Log
              </h2>
              <p className="text-xs text-slate-400">Real-time enterprise audit events recorded in database</p>
            </div>
            <button
              onClick={fetchLogs}
              disabled={loadingLogs}
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="Refresh Activity Log"
            >
              <RefreshCw className={`w-4 h-4 ${loadingLogs ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/60 text-slate-400 uppercase font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Event Action</th>
                  <th className="py-3 px-4">User</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">IP Address</th>
                  <th className="py-3 px-4">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-6 text-center text-slate-500">
                      No activity records found.
                    </td>
                  </tr>
                ) : (
                  logs.map((log) => (
                    <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-sans font-medium text-white flex items-center gap-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                        {log.action}
                      </td>
                      <td className="py-3 px-4 text-slate-300">{log.user_email || 'System'}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-sans font-bold ${
                            log.status === 'SUCCESS'
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-red-500/10 text-red-400 border border-red-500/20'
                          }`}
                        >
                          {log.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-slate-400">{log.ip_address || '127.0.0.1'}</td>
                      <td className="py-3 px-4 text-slate-400 font-sans">
                        {new Date(log.created_at).toLocaleTimeString([], {
                          hour: '2-digit',
                          minute: '2-digit',
                          second: '2-digit',
                        })}
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
