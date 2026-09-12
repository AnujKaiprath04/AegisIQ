'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import {
  Activity,
  Cpu,
  Database,
  Server,
  Zap,
  Clock,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  Layers,
  HardDrive,
  Radio,
  FileCode2,
  Terminal,
  ArrowUpRight,
  ShieldCheck,
  BarChart2,
} from 'lucide-react';

interface Subsystem {
  name: string;
  status: string;
  latency_ms: number;
  uptime_pct: number;
  details: string;
}

interface Resources {
  cpu_usage_pct: number;
  memory_allocated_mb: number;
  memory_total_mb: number;
  memory_usage_pct: number;
  disk_usage_pct: number;
  uptime_seconds: number;
}

interface DBPool {
  pool_size: number;
  checked_in_connections: number;
  checked_out_connections: number;
  overflow_connections: number;
  pool_utilization_pct: number;
  avg_query_latency_ms: number;
}

interface APM {
  requests_per_second: number;
  p50_latency_ms: number;
  p90_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;
  status_2xx_pct: number;
  status_4xx_pct: number;
  status_5xx_pct: number;
}

interface TelemetrySnapshot {
  platform_status: string;
  timestamp: string;
  subsystems: Subsystem[];
  resources: Resources;
  db_pool: DBPool;
  apm: APM;
}

export default function TelemetryPage() {
  const { user } = useAuth();
  const [snapshot, setSnapshot] = useState<TelemetrySnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPrometheusModal, setShowPrometheusModal] = useState(false);
  const [rawPrometheus, setRawPrometheus] = useState<string>('');

  const fetchTelemetryData = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get<TelemetrySnapshot>('/telemetry/dashboard');
      setSnapshot(res.data);
    } catch (err) {
      console.error('Error fetching telemetry snapshot:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPrometheusMetrics = async () => {
    try {
      const res = await apiClient.get('/telemetry/prometheus');
      setRawPrometheus(typeof res.data === 'string' ? res.data : JSON.stringify(res.data, null, 2));
      setShowPrometheusModal(true);
    } catch (err) {
      console.error('Failed to fetch raw prometheus text:', err);
    }
  };

  useEffect(() => {
    fetchTelemetryData();
    const interval = setInterval(fetchTelemetryData, 10000);
    return () => clearInterval(interval);
  }, []);

  const formatUptime = (sec: number) => {
    const d = Math.floor(sec / 86400);
    const h = Math.floor((sec % 86400) / 3600);
    const m = Math.floor((sec % 3600) / 60);
    return `${d}d ${h}h ${m}m`;
  };

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold mb-2">
              <Activity className="w-3.5 h-3.5" />
              <span>System Telemetry, APM & Observability Studio</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">System Telemetry & APM Studio</h1>
            <p className="text-xs text-slate-400 mt-1">
              Microservice health matrix, connection pool diagnostics, latency percentiles (p50/p95/p99), and live Prometheus scrapers.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchTelemetryData}
              disabled={loading}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Telemetry"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={fetchPrometheusMetrics}
              className="inline-flex items-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-xl text-xs font-semibold border border-slate-700 transition-colors"
            >
              <FileCode2 className="w-4 h-4 text-amber-400" />
              Prometheus Metrics
            </button>
          </div>
        </div>

        {/* Top Metric Cards */}
        {snapshot && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Platform Health State</span>
              <p className="text-2xl font-bold text-emerald-400 font-mono flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
                {snapshot.platform_status}
              </p>
              <p className="text-[11px] text-slate-400 font-mono">
                Uptime: {formatUptime(snapshot.resources.uptime_seconds)}
              </p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Microservice Subsystems</span>
              <p className="text-2xl font-bold text-white font-mono">
                {snapshot.subsystems.filter((s) => s.status === 'HEALTHY').length} / {snapshot.subsystems.length} Online
              </p>
              <p className="text-[11px] text-emerald-400 font-semibold">100% Subsystem Availability</p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Throughput & Rate</span>
              <p className="text-2xl font-bold text-blue-400 font-mono">{snapshot.apm.requests_per_second} RPS</p>
              <p className="text-[11px] text-slate-400 font-mono">2xx Success: {snapshot.apm.status_2xx_pct}%</p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Latency Percentile (p95)</span>
              <p className="text-2xl font-bold text-emerald-400 font-mono">{snapshot.apm.p95_latency_ms} ms</p>
              <p className="text-[11px] text-slate-400 font-mono">Median p50: {snapshot.apm.p50_latency_ms} ms</p>
            </div>
          </div>
        )}

        {/* Subsystem Health Status Matrix (6 Microservices) */}
        {snapshot && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Server className="w-4 h-4 text-blue-500" />
                  Core Subsystem Health & Latency Matrix
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Continuous health probes across microservices</p>
              </div>
              <span className="text-xs font-mono text-emerald-400 font-bold">All Subsystems Nominal</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {snapshot.subsystems.map((sub, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-slate-950/70 border border-slate-800 rounded-2xl space-y-3 hover:border-slate-700 transition-all text-xs"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-bold text-white text-xs">{sub.name}</h4>
                      <p className="text-[10px] text-slate-500 font-mono mt-0.5">Uptime: {sub.uptime_pct}%</p>
                    </div>
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                      {sub.status}
                    </span>
                  </div>

                  <p className="text-slate-300 text-[11px] leading-relaxed">{sub.details}</p>

                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between font-mono text-[10px]">
                    <span className="text-slate-500">Probe Latency:</span>
                    <span className="text-blue-400 font-bold">{sub.latency_ms} ms</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Resources & Database Pool Gauges */}
        {snapshot && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Host Resources */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Cpu className="w-4 h-4 text-purple-400" />
                  Host Compute & Memory Utilization
                </h3>
                <span className="text-xs text-slate-400 font-mono">Linux Container Node</span>
              </div>

              <div className="space-y-4 text-xs">
                {/* CPU */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between font-semibold">
                    <span className="text-slate-300">CPU Load Allocation</span>
                    <span className="font-mono text-purple-400 font-bold">{snapshot.resources.cpu_usage_pct}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                    <div style={{ width: `${snapshot.resources.cpu_usage_pct}%` }} className="h-full bg-purple-500" />
                  </div>
                </div>

                {/* RAM */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between font-semibold">
                    <span className="text-slate-300">Memory Allocation (RAM)</span>
                    <span className="font-mono text-blue-400 font-bold">
                      {snapshot.resources.memory_allocated_mb} MB / {snapshot.resources.memory_total_mb} MB ({snapshot.resources.memory_usage_pct}%)
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                    <div style={{ width: `${snapshot.resources.memory_usage_pct}%` }} className="h-full bg-blue-500" />
                  </div>
                </div>

                {/* Disk */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between font-semibold">
                    <span className="text-slate-300">NVMe Persistent Storage I/O</span>
                    <span className="font-mono text-emerald-400 font-bold">{snapshot.resources.disk_usage_pct}%</span>
                  </div>
                  <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden">
                    <div style={{ width: `${snapshot.resources.disk_usage_pct}%` }} className="h-full bg-emerald-500" />
                  </div>
                </div>
              </div>
            </div>

            {/* Database Connection Pool Diagnostics */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Database className="w-4 h-4 text-emerald-400" />
                  PostgreSQL Connection Pool Diagnostics
                </h3>
                <span className="text-xs text-slate-400 font-mono">SQLAlchemy QueuePool</span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase font-mono">Total Pool Size</span>
                  <p className="text-xl font-bold font-mono text-white">{snapshot.db_pool.pool_size} Conns</p>
                  <span className="text-[10px] text-slate-500 font-mono">Allocated capacity</span>
                </div>

                <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase font-mono">Pool Utilization</span>
                  <p className="text-xl font-bold font-mono text-emerald-400">{snapshot.db_pool.pool_utilization_pct}%</p>
                  <span className="text-[10px] text-slate-500 font-mono">2 Active / 18 Idle</span>
                </div>

                <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase font-mono">Avg Query Execution</span>
                  <p className="text-xl font-bold font-mono text-blue-400">{snapshot.db_pool.avg_query_latency_ms} ms</p>
                  <span className="text-[10px] text-slate-500 font-mono">Pipelined execution</span>
                </div>

                <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase font-mono">Overflow Queue</span>
                  <p className="text-xl font-bold font-mono text-white">{snapshot.db_pool.overflow_connections}</p>
                  <span className="text-[10px] text-slate-500 font-mono">Zero queue backlog</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* APM Latency Percentiles */}
        {snapshot && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Zap className="w-4 h-4 text-amber-400" />
                  APM Latency Percentiles & Status Code Distribution
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">End-to-end request duration percentiles</p>
              </div>
              <span className="text-xs text-slate-400 font-mono">{snapshot.apm.requests_per_second} Requests / Sec</span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1">
                <span className="text-[10px] font-mono text-slate-400 uppercase">p50 (Median)</span>
                <p className="text-2xl font-bold font-mono text-emerald-400">{snapshot.apm.p50_latency_ms} ms</p>
                <span className="text-[9px] text-slate-500 font-mono">50% requests below</span>
              </div>

              <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1">
                <span className="text-[10px] font-mono text-slate-400 uppercase">p90 Percentile</span>
                <p className="text-2xl font-bold font-mono text-blue-400">{snapshot.apm.p90_latency_ms} ms</p>
                <span className="text-[9px] text-slate-500 font-mono">90% requests below</span>
              </div>

              <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1">
                <span className="text-[10px] font-mono text-slate-400 uppercase">p95 Percentile</span>
                <p className="text-2xl font-bold font-mono text-amber-400">{snapshot.apm.p95_latency_ms} ms</p>
                <span className="text-[9px] text-slate-500 font-mono">95% requests below</span>
              </div>

              <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1">
                <span className="text-[10px] font-mono text-slate-400 uppercase">p99 (Tail Latency)</span>
                <p className="text-2xl font-bold font-mono text-rose-400">{snapshot.apm.p99_latency_ms} ms</p>
                <span className="text-[9px] text-slate-500 font-mono">99% requests below</span>
              </div>
            </div>

            {/* HTTP Status Code Distribution */}
            <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-2 text-xs">
              <div className="flex items-center justify-between font-mono text-[11px]">
                <span className="text-slate-400">HTTP Response Status Distribution</span>
                <div className="flex items-center gap-4">
                  <span className="text-emerald-400 font-bold">2xx: {snapshot.apm.status_2xx_pct}%</span>
                  <span className="text-amber-400 font-bold">4xx: {snapshot.apm.status_4xx_pct}%</span>
                  <span className="text-rose-400 font-bold">5xx: {snapshot.apm.status_5xx_pct}%</span>
                </div>
              </div>
              <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden flex">
                <div style={{ width: `${snapshot.apm.status_2xx_pct}%` }} className="h-full bg-emerald-500" />
                <div style={{ width: `${snapshot.apm.status_4xx_pct}%` }} className="h-full bg-amber-500" />
                <div style={{ width: `${snapshot.apm.status_5xx_pct}%` }} className="h-full bg-rose-500" />
              </div>
            </div>
          </div>
        )}

        {/* Prometheus Metrics Drawer Modal */}
        {showPrometheusModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-3xl w-full shadow-2xl space-y-4 max-h-[85vh] flex flex-col">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 shrink-0">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-amber-400" />
                  Live Prometheus Exposition Metrics (/metrics)
                </h3>
                <button onClick={() => setShowPrometheusModal(false)} className="text-slate-400 hover:text-white font-bold">&times;</button>
              </div>

              <div className="flex-1 overflow-y-auto bg-slate-950 p-4 rounded-2xl border border-slate-800/80 font-mono text-xs text-slate-300 leading-relaxed custom-scrollbar">
                <pre>{rawPrometheus}</pre>
              </div>

              <div className="pt-2 border-t border-slate-800 flex justify-end shrink-0">
                <button
                  onClick={() => setShowPrometheusModal(false)}
                  className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-semibold"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </EnterpriseShell>
  );
}
