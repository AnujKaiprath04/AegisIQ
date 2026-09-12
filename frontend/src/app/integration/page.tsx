'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import {
  Database,
  Server,
  Globe,
  FileCode,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Plus,
  Activity,
  Play,
  Clock,
  Layers,
  Search,
  Lock,
  Key,
  Shield,
  Sparkles,
  ChevronRight,
  Table as TableIcon,
  Columns,
  Cpu,
} from 'lucide-react';

interface ConnectionSummary {
  id: number;
  name: string;
  description?: string;
  connection_type: 'POSTGRESQL' | 'MYSQL' | 'SQLITE' | 'MONGODB' | 'REST_API' | 'FILE_STORAGE';
  host?: string;
  port?: number;
  database_name?: string;
  api_endpoint_url?: string;
  status: string;
  latency_ms: number;
  ssl_enabled: boolean;
  last_tested_at?: string;
  tables_count: number;
  created_at: string;
}

interface ColumnMeta {
  id: number;
  column_name: string;
  data_type: string;
  is_nullable: boolean;
  is_primary_key: boolean;
  is_foreign_key: boolean;
  sample_values: any[];
}

interface TableMeta {
  id: number;
  connection_id: number;
  table_name: string;
  schema_name: string;
  table_type: string;
  estimated_row_count: number;
  column_count: number;
  primary_key_columns?: string;
  columns: ColumnMeta[];
  discovered_at: string;
}

interface SchemaTree {
  connection_id: number;
  connection_name: string;
  connection_type: string;
  database_name?: string;
  tables: TableMeta[];
  total_tables: number;
  total_columns: number;
}

interface IngestionJob {
  id: number;
  connection_id: number;
  job_name: string;
  sync_mode: string;
  sync_schedule: string;
  status: string;
  rows_ingested: number;
  bytes_transferred: number;
  duration_seconds: number;
  last_run_at?: string;
}

export default function IntegrationPage() {
  const { hasRole } = useAuth();
  const [connections, setConnections] = useState<ConnectionSummary[]>([]);
  const [selectedConnId, setSelectedConnId] = useState<number | null>(null);
  const [schemaTree, setSchemaTree] = useState<SchemaTree | null>(null);
  const [selectedTable, setSelectedTable] = useState<TableMeta | null>(null);
  const [ingestionJobs, setIngestionJobs] = useState<IngestionJob[]>([]);

  const [loadingList, setLoadingList] = useState(true);
  const [loadingSchema, setLoadingSchema] = useState(false);
  const [testingId, setTestingId] = useState<number | null>(null);
  const [runningJobId, setRunningJobId] = useState<number | null>(null);

  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // New Connection Modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [connType, setConnType] = useState<string>('POSTGRESQL');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    host: 'db.internal.aegisiq.com',
    port: 5432,
    database_name: 'enterprise_dw',
    username: 'aegis_reader',
    password: '',
    connection_string: '',
    api_endpoint_url: 'https://api.aegisiq.com/v1/telemetry',
    api_auth_type: 'BEARER_TOKEN',
    ssl_enabled: true,
  });

  const fetchInitialData = async () => {
    setLoadingList(true);
    try {
      const [connRes, jobsRes] = await Promise.all([
        apiClient.get<ConnectionSummary[]>('/integration/connections'),
        apiClient.get<IngestionJob[]>('/integration/jobs'),
      ]);
      setConnections(connRes.data || []);
      setIngestionJobs(jobsRes.data || []);
      if (connRes.data && connRes.data.length > 0) {
        selectConnection(connRes.data[0].id);
      }
    } catch (err) {
      console.error('Error fetching integration data:', err);
    } finally {
      setLoadingList(false);
    }
  };

  const selectConnection = async (id: number) => {
    setSelectedConnId(id);
    setLoadingSchema(true);
    try {
      const res = await apiClient.get<SchemaTree>(`/integration/connections/${id}/schema`);
      setSchemaTree(res.data);
      if (res.data.tables && res.data.tables.length > 0) {
        setSelectedTable(res.data.tables[0]);
      } else {
        setSelectedTable(null);
      }
    } catch (err) {
      console.error('Error loading schema tree:', err);
    } finally {
      setLoadingSchema(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const handleTestConnection = async (id: number, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    setTestingId(id);
    try {
      const res = await apiClient.post(`/integration/connections/${id}/test`);
      setNotification({
        message: `Diagnostics Verified: ${res.data.server_version || 'Connection online'} (${res.data.latency_ms}ms latency)`,
        type: 'success',
      });
      // Refresh list to update latency
      const connRes = await apiClient.get<ConnectionSummary[]>('/integration/connections');
      setConnections(connRes.data || []);
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Connection test failed.', type: 'error' });
    } finally {
      setTestingId(null);
    }
  };

  const handleCreateConnection = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await apiClient.post('/integration/connections', {
        ...formData,
        connection_type: connType,
      });
      setNotification({ message: `Data connection '${res.data.name}' registered & cataloged successfully!`, type: 'success' });
      setShowAddModal(false);
      fetchInitialData();
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Failed to register connection.', type: 'error' });
    }
  };

  const handleRunSyncJob = async (jobId: number) => {
    setRunningJobId(jobId);
    try {
      const res = await apiClient.post(`/integration/jobs/${jobId}/run`);
      setNotification({ message: res.data.message || 'Ingestion sync completed successfully.', type: 'success' });
      const jobsRes = await apiClient.get<IngestionJob[]>('/integration/jobs');
      setIngestionJobs(jobsRes.data || []);
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Job execution failed.', type: 'error' });
    } finally {
      setRunningJobId(null);
    }
  };

  const canManageIntegrations = hasRole(['Admin', 'Data Analyst']);

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-2">
              <Database className="w-3.5 h-3.5" />
              <span>Enterprise Data Integration Hub</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise Data Integration Studio</h1>
            <p className="text-xs text-slate-400 mt-1">
              Connect relational databases (PostgreSQL, MySQL, SQLite), MongoDB NoSQL clusters, cloud REST APIs, and multi-format files into unified data pipelines.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchInitialData}
              disabled={loadingList}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Connectors"
            >
              <RefreshCw className={`w-4 h-4 ${loadingList ? 'animate-spin' : ''}`} />
            </button>
            {canManageIntegrations && (
              <button
                onClick={() => setShowAddModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all"
              >
                <Plus className="w-4 h-4" />
                Add Data Connection
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

        {/* Connector Hub Cards */}
        <div>
          <div className="flex items-center justify-between mb-3 px-1">
            <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Configured Enterprise Data Sources ({connections.length})
            </h2>
            <span className="text-xs font-mono text-slate-400">
              Avg Latency: {(connections.reduce((acc, c) => acc + c.latency_ms, 0) / Math.max(connections.length, 1)).toFixed(1)}ms
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {connections.map((conn) => {
              const isSelected = selectedConnId === conn.id;
              const isTesting = testingId === conn.id;
              return (
                <div
                  key={conn.id}
                  onClick={() => selectConnection(conn.id)}
                  className={`p-5 rounded-3xl border transition-all cursor-pointer flex flex-col justify-between space-y-4 ${
                    isSelected
                      ? 'bg-blue-950/40 border-blue-600/80 shadow-xl shadow-blue-900/20'
                      : 'bg-slate-900/70 border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <div className="w-10 h-10 rounded-2xl bg-blue-500/10 text-blue-400 flex items-center justify-center font-bold text-sm">
                        {conn.connection_type === 'POSTGRESQL' ? (
                          <Database className="w-5 h-5" />
                        ) : conn.connection_type === 'SQLITE' ? (
                          <FileCode className="w-5 h-5 text-emerald-400" />
                        ) : conn.connection_type === 'REST_API' ? (
                          <Globe className="w-5 h-5 text-purple-400" />
                        ) : (
                          <Server className="w-5 h-5 text-amber-400" />
                        )}
                      </div>
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                        {conn.status}
                      </span>
                    </div>

                    <div>
                      <h3 className="text-sm font-bold text-white line-clamp-1">{conn.name}</h3>
                      <p className="text-[11px] text-slate-400 line-clamp-2 mt-1">{conn.description}</p>
                    </div>

                    <div className="p-2.5 bg-slate-950/60 rounded-xl border border-slate-800/80 font-mono text-[10px] text-slate-400 space-y-1">
                      <div className="flex items-center justify-between">
                        <span>Target:</span>
                        <span className="text-slate-200 truncate max-w-[130px]">
                          {conn.database_name || conn.api_endpoint_url || 'Local Node'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span>Ping Latency:</span>
                        <span className="text-emerald-400 font-bold">{conn.latency_ms}ms</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-800 flex items-center justify-between">
                    <span className="text-[10px] text-slate-500 font-mono">
                      {conn.ssl_enabled ? 'TLS / SSL' : 'Internal'}
                    </span>
                    <button
                      onClick={(e) => handleTestConnection(conn.id, e)}
                      disabled={isTesting}
                      className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-blue-400 hover:text-white rounded-lg text-[11px] font-semibold transition-all border border-slate-700 flex items-center gap-1"
                    >
                      <Activity className={`w-3 h-3 ${isTesting ? 'animate-spin' : ''}`} />
                      {isTesting ? 'Testing...' : 'Test Ping'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Schema Discovery Explorer & Metadata Catalog */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Columns className="w-5 h-5 text-blue-500" />
                Metadata Catalog & Schema Tree Explorer
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Introspected tables, collections, schema definitions, and column data types
              </p>
            </div>
            {schemaTree && (
              <span className="px-3 py-1 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-slate-300">
                {schemaTree.connection_name} &bull; {schemaTree.total_tables} Tables &bull; {schemaTree.total_columns} Columns Cataloged
              </span>
            )}
          </div>

          {loadingSchema ? (
            <div className="py-16 text-center text-slate-500">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
              Introspecting metadata catalog...
            </div>
          ) : !schemaTree || schemaTree.tables.length === 0 ? (
            <div className="py-12 text-center text-slate-500">
              No metadata tables cataloged for this data connection.
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Discovered Tables */}
              <div className="space-y-2">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Discovered Tables & Endpoints
                </span>
                {schemaTree.tables.map((t) => {
                  const isTableActive = selectedTable?.id === t.id;
                  return (
                    <div
                      key={t.id}
                      onClick={() => setSelectedTable(t)}
                      className={`p-3.5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between ${
                        isTableActive
                          ? 'bg-blue-600/20 border-blue-500 text-white'
                          : 'bg-slate-950/60 border-slate-800/80 text-slate-300 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <TableIcon className="w-4 h-4 text-blue-400 shrink-0" />
                        <div>
                          <p className="font-bold text-xs font-mono">{t.table_name}</p>
                          <p className="text-[10px] text-slate-400">
                            Schema: {t.schema_name} &bull; {t.column_count} columns
                          </p>
                        </div>
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">
                        {t.estimated_row_count.toLocaleString()} rows
                      </span>
                    </div>
                  );
                })}
              </div>

              {/* Right Column: Column Schema Inspector */}
              <div className="lg:col-span-2 space-y-3">
                {selectedTable ? (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                        Column Dictionary: <code className="text-blue-400 font-mono">{selectedTable.table_name}</code>
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">
                        Primary Key: {selectedTable.primary_key_columns || 'None'}
                      </span>
                    </div>

                    <div className="overflow-x-auto border border-slate-800 rounded-2xl">
                      <table className="w-full text-left text-xs">
                        <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800 uppercase text-[10px]">
                          <tr>
                            <th className="py-2.5 px-4">Column Name</th>
                            <th className="py-2.5 px-4">Data Type</th>
                            <th className="py-2.5 px-4">Key Constraints</th>
                            <th className="py-2.5 px-4">Nullable</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60 font-mono">
                          {selectedTable.columns.map((col) => (
                            <tr key={col.id} className="hover:bg-slate-800/40 transition-colors">
                              <td className="py-2.5 px-4 font-bold text-white flex items-center gap-2">
                                {col.is_primary_key && <Key className="w-3 h-3 text-amber-400" />}
                                {col.column_name}
                              </td>
                              <td className="py-2.5 px-4 text-blue-400">{col.data_type}</td>
                              <td className="py-2.5 px-4">
                                {col.is_primary_key ? (
                                  <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
                                    PRIMARY KEY
                                  </span>
                                ) : (
                                  <span className="text-slate-600 text-[10px]">STANDARD</span>
                                )}
                              </td>
                              <td className="py-2.5 px-4 text-slate-400">
                                {col.is_nullable ? 'YES' : 'NO (NOT NULL)'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div className="py-12 text-center text-slate-500">
                    Select a table to view its column schema.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Ingestion & Sync Job Scheduler Center */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-emerald-400" />
              Ingestion & Data Synchronization Jobs
            </h3>
            <span className="text-xs text-slate-400 font-mono">{ingestionJobs.length} Sync Schedules Active</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 uppercase font-semibold border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Job Identifier</th>
                  <th className="py-3 px-4">Sync Mode</th>
                  <th className="py-3 px-4">Cadence</th>
                  <th className="py-3 px-4">Throughput</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Execute Sync</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-sans">
                {ingestionJobs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-6 text-center text-slate-500">
                      No active synchronization jobs configured.
                    </td>
                  </tr>
                ) : (
                  ingestionJobs.map((j) => {
                    const isRunning = runningJobId === j.id;
                    return (
                      <tr key={j.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3 px-4 font-bold text-white">{j.job_name}</td>
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-300">{j.sync_mode}</td>
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-400">{j.sync_schedule}</td>
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-300">
                          {j.rows_ingested.toLocaleString()} rows ({(j.bytes_transferred / (1024 * 1024)).toFixed(2)} MB)
                        </td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                            {j.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={() => handleRunSyncJob(j.id)}
                            disabled={isRunning || !canManageIntegrations}
                            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-blue-600/20 transition-all disabled:opacity-40"
                          >
                            {isRunning ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
                            {isRunning ? 'Syncing...' : 'Sync Now'}
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Add Connection Modal */}
        {showAddModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-xl w-full shadow-2xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Database className="w-5 h-5 text-blue-500" />
                  Configure Enterprise Data Connection
                </h3>
                <button onClick={() => setShowAddModal(false)} className="text-slate-400 hover:text-white font-bold">&times;</button>
              </div>

              {/* Connector Type Selector */}
              <div className="grid grid-cols-3 sm:grid-cols-4 gap-2">
                {[
                  { id: 'POSTGRESQL', label: 'PostgreSQL', icon: Database },
                  { id: 'MYSQL', label: 'MySQL', icon: Server },
                  { id: 'SQLITE', label: 'SQLite', icon: FileCode },
                  { id: 'MONGODB', label: 'MongoDB', icon: Server },
                  { id: 'REST_API', label: 'REST API', icon: Globe },
                  { id: 'FILE_STORAGE', label: 'Cloud Lake', icon: Layers },
                ].map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    onClick={() => setConnType(t.id)}
                    className={`p-2.5 rounded-xl border text-center transition-all ${
                      connType === t.id
                        ? 'bg-blue-600 text-white font-bold border-blue-500'
                        : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    <t.icon className="w-4 h-4 mx-auto mb-1" />
                    <span className="text-[10px] block">{t.label}</span>
                  </button>
                ))}
              </div>

              <form onSubmit={handleCreateConnection} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Connection Label</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Production Operations Database"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                {connType !== 'REST_API' ? (
                  <>
                    <div className="grid grid-cols-3 gap-3">
                      <div className="col-span-2">
                        <label className="block text-slate-400 font-semibold mb-1">Host / Network Node</label>
                        <input
                          type="text"
                          value={formData.host}
                          onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                          className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono"
                        />
                      </div>
                      <div>
                        <label className="block text-slate-400 font-semibold mb-1">Port</label>
                        <input
                          type="number"
                          value={formData.port}
                          onChange={(e) => setFormData({ ...formData, port: Number(e.target.value) })}
                          className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <label className="block text-slate-400 font-semibold mb-1">Database Name</label>
                        <input
                          type="text"
                          value={formData.database_name}
                          onChange={(e) => setFormData({ ...formData, database_name: e.target.value })}
                          className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono"
                        />
                      </div>
                      <div>
                        <label className="block text-slate-400 font-semibold mb-1">Username</label>
                        <input
                          type="text"
                          value={formData.username}
                          onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                          className="w-full px-3.5 py-2 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono"
                        />
                      </div>
                    </div>
                  </>
                ) : (
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">API Endpoint URL</label>
                    <input
                      type="url"
                      value={formData.api_endpoint_url}
                      onChange={(e) => setFormData({ ...formData, api_endpoint_url: e.target.value })}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono"
                    />
                  </div>
                )}

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowAddModal(false)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-600/20"
                  >
                    Save & Discover Schema
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
