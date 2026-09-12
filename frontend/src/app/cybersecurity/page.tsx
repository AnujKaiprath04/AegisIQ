'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Lock,
  Globe,
  Activity,
  RefreshCw,
  Ban,
  UserX,
  CheckCircle2,
  XCircle,
  Clock,
  Key,
  Layers,
  Search,
  Plus,
  Terminal,
  ChevronRight,
  Shield,
  Eye,
} from 'lucide-react';

interface Scorecard {
  overall_risk_score: number;
  risk_level: string;
  auth_entropy_score: number;
  rbac_enclosure_score: number;
  encryption_score: number;
  anomaly_defense_score: number;
  active_threats_count: number;
  evaluated_at: string;
}

interface Incident {
  id: number;
  incident_code: string;
  title: string;
  severity: string;
  category: string;
  status: string;
  actor_ip?: string;
  actor_email?: string;
  location_country?: string;
  event_count: number;
  description: string;
  mitigation_action_taken?: string;
  detected_at: string;
  resolved_at?: string;
}

interface IPBlock {
  id: number;
  ip_address: string;
  reason: string;
  is_permanent: boolean;
  created_at: string;
}

export default function CybersecurityPage() {
  const { hasRole } = useAuth();
  const [scorecard, setScorecard] = useState<Scorecard | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [blocklist, setBlocklist] = useState<IPBlock[]>([]);
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);

  // Manual IP Ban Modal
  const [showBanModal, setShowBanModal] = useState(false);
  const [banIp, setBanIp] = useState('');
  const [banReason, setBanReason] = useState('');

  const fetchCyberData = async () => {
    setLoading(true);
    try {
      let queryUrl = '/cybersecurity/incidents';
      const params: string[] = [];
      if (severityFilter !== 'ALL') params.push(`severity=${severityFilter}`);
      if (statusFilter !== 'ALL') params.push(`status_filter=${statusFilter}`);
      if (params.length > 0) queryUrl += `?${params.join('&')}`;

      const [scoreRes, incRes, blockRes] = await Promise.all([
        apiClient.get<Scorecard>('/cybersecurity/scorecard'),
        apiClient.get<Incident[]>(queryUrl),
        apiClient.get<IPBlock[]>('/cybersecurity/blocklist'),
      ]);
      setScorecard(scoreRes.data);
      setIncidents(incRes.data || []);
      setBlocklist(blockRes.data || []);
    } catch (err) {
      console.error('Error fetching cybersecurity telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCyberData();
  }, [severityFilter, statusFilter]);

  const handleRemediation = async (incidentId: number, action: string) => {
    setActionLoadingId(incidentId);
    try {
      const res = await apiClient.post(`/cybersecurity/incidents/${incidentId}/action`, {
        action,
      });
      setNotification({ message: res.data.message, type: 'success' });
      fetchCyberData();
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Action failed.', type: 'error' });
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleManualBan = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/cybersecurity/blocklist', {
        ip_address: banIp,
        reason: banReason,
        is_permanent: true,
      });
      setNotification({ message: `IP Address ${banIp} successfully quarantined on perimeter firewall.`, type: 'success' });
      setShowBanModal(false);
      setBanIp('');
      setBanReason('');
      fetchCyberData();
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Failed to ban IP.', type: 'error' });
    }
  };

  const canMitigate = hasRole(['Admin', 'Executive']);

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold mb-2">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Cybersecurity Intelligence & SIEM Threat Detection</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">Zero-Trust Cybersecurity & SIEM Studio</h1>
            <p className="text-xs text-slate-400 mt-1">
              Real-time threat monitoring, automated brute-force detection, geo-velocity anomaly alerts, and active containment playbooks.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchCyberData}
              disabled={loading}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Telemetry"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            {canMitigate && (
              <button
                onClick={() => setShowBanModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-rose-600/20 transition-all"
              >
                <Ban className="w-4 h-4" />
                Firewall IP Quarantine
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

        {/* Zero-Trust Posture Gauge & Vector Breakdown */}
        {scorecard && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
            {/* Master Risk Score */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between space-y-3">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                Zero-Trust Risk Posture
              </span>
              <div>
                <div className="flex items-baseline gap-2">
                  <span className="text-4xl font-bold font-mono text-emerald-400">
                    {scorecard.overall_risk_score}
                  </span>
                  <span className="text-xs text-slate-500 font-mono">/ 100</span>
                </div>
                <p className="text-xs font-bold text-emerald-400 mt-1">
                  Status: {scorecard.risk_level} (Low Risk)
                </p>
                <p className="text-[11px] text-slate-400 mt-0.5">
                  {scorecard.active_threats_count} Active incidents under containment
                </p>
              </div>
              <span className="text-[10px] text-slate-500 font-mono">
                Continuous Telemetry Sampling
              </span>
            </div>

            {/* Defense Vectors */}
            <div className="lg:col-span-3 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">
                Defense Vectors & Cryptographic Enforcement
              </span>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
                <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1.5">
                  <div className="flex items-center justify-between font-semibold">
                    <span className="text-slate-300">Auth Entropy & Hash Salt</span>
                    <span className="font-mono text-emerald-400 font-bold">{scorecard.auth_entropy_score}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div style={{ width: `${scorecard.auth_entropy_score}%` }} className="h-full bg-emerald-500" />
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">Bcrypt Salt &ge; 12 &bull; JWT 60-min TTL</span>
                </div>

                <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1.5">
                  <div className="flex items-center justify-between font-semibold">
                    <span className="text-slate-300">RBAC Dependency Enclosure</span>
                    <span className="font-mono text-emerald-400 font-bold">{scorecard.rbac_enclosure_score}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div style={{ width: `${scorecard.rbac_enclosure_score}%` }} className="h-full bg-emerald-500" />
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">100% Endpoint Role Dependency Injection</span>
                </div>

                <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1.5">
                  <div className="flex items-center justify-between font-semibold">
                    <span className="text-slate-300">Data Encryption (TLS 1.3 / AES-256)</span>
                    <span className="font-mono text-emerald-400 font-bold">{scorecard.encryption_score}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div style={{ width: `${scorecard.encryption_score}%` }} className="h-full bg-emerald-500" />
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">Enforced across all relational & NoSQL connectors</span>
                </div>

                <div className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1.5">
                  <div className="flex items-center justify-between font-semibold">
                    <span className="text-slate-300">Intrusion & Anomaly Defense</span>
                    <span className="font-mono text-emerald-400 font-bold">{scorecard.anomaly_defense_score}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-slate-900 rounded-full overflow-hidden">
                    <div style={{ width: `${scorecard.anomaly_defense_score}%` }} className="h-full bg-emerald-500" />
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">Brute-force lockout & geo-velocity scanners</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* SIEM Incident Real-Time Stream */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Terminal className="w-4 h-4 text-rose-500" />
                SIEM Real-Time Incident Stream & Containment Feed
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Live threat event stream correlated across API gateways, authorization checks, and network nodes
              </p>
            </div>

            {/* Severity Filter Pills */}
            <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-2xl border border-slate-800 text-xs">
              {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map((s) => (
                <button
                  key={s}
                  onClick={() => setSeverityFilter(s)}
                  className={`px-3 py-1 rounded-xl font-semibold transition-all ${
                    severityFilter === s
                      ? 'bg-rose-600 text-white shadow-md shadow-rose-600/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-3">
            {loading ? (
              <div className="py-12 text-center text-slate-500">
                <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-rose-500" />
                Sampling SIEM incident telemetry...
              </div>
            ) : incidents.length === 0 ? (
              <div className="py-12 text-center text-slate-500">
                No active security incidents match the selected severity criteria.
              </div>
            ) : (
              incidents.map((inc) => {
                const isWorking = actionLoadingId === inc.id;
                return (
                  <div
                    key={inc.id}
                    className="p-5 bg-slate-950/70 border border-slate-800/80 rounded-2xl space-y-3 text-xs hover:border-slate-700 transition-all"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <span className="font-mono text-slate-500 text-[11px]">{inc.incident_code}</span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                            inc.severity === 'HIGH'
                              ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                              : inc.severity === 'MEDIUM'
                              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                              : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                          }`}
                        >
                          {inc.severity}
                        </span>
                        <span className="font-bold text-white text-xs">{inc.title}</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-slate-900 border border-slate-800 text-slate-300">
                          {inc.status}
                        </span>
                        <span className="text-[10px] font-mono text-slate-500">
                          {new Date(inc.detected_at).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>

                    <p className="text-slate-300 text-xs leading-relaxed">{inc.description}</p>

                    <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-slate-800/80 font-mono text-[10px] text-slate-400">
                      <div className="flex items-center gap-4">
                        <span>Actor IP: <code className="text-rose-400">{inc.actor_ip || 'N/A'}</code></span>
                        <span>User: <code className="text-blue-400">{inc.actor_email || 'System Daemon'}</code></span>
                        <span>Geo: <span className="text-slate-300">{inc.location_country || 'Internal'}</span></span>
                        <span>Events: <span className="text-amber-400 font-bold">{inc.event_count}</span></span>
                      </div>

                      {/* Containment Buttons */}
                      {inc.status === 'OPEN' || inc.status === 'INVESTIGATING' ? (
                        <div className="flex items-center gap-2">
                          {inc.actor_ip && (
                            <button
                              onClick={() => handleRemediation(inc.id, 'BLOCK_IP')}
                              disabled={isWorking || !canMitigate}
                              className="px-2.5 py-1 bg-rose-600/20 hover:bg-rose-600 text-rose-300 hover:text-white rounded-lg text-[10px] font-bold transition-all border border-rose-500/30 flex items-center gap-1 disabled:opacity-40"
                            >
                              <Ban className="w-3 h-3" />
                              Quarantine IP
                            </button>
                          )}
                          <button
                            onClick={() => handleRemediation(inc.id, 'RESOLVE')}
                            disabled={isWorking || !canMitigate}
                            className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg text-[10px] font-bold transition-all border border-slate-700"
                          >
                            Mark Resolved
                          </button>
                        </div>
                      ) : (
                        <span className="text-emerald-400 font-sans font-bold flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Mitigated / Closed
                        </span>
                      )}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Active Perimeter Firewall IP Blocklist */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Ban className="w-4 h-4 text-rose-400" />
                Active Perimeter Firewall IP Blocklist ({blocklist.length})
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Automatically dropped connections at the API gateway layer
              </p>
            </div>
            <span className="text-xs text-slate-400 font-mono">Perimeter Quarantine Active</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950/70 text-slate-400 uppercase font-semibold border-b border-slate-800 text-[10px]">
                <tr>
                  <th className="py-2.5 px-4">Quarantined IP Address</th>
                  <th className="py-2.5 px-4">Security Reason / Incident</th>
                  <th className="py-2.5 px-4">Enforcement</th>
                  <th className="py-2.5 px-4">Quarantine Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {blocklist.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2.5 px-4 font-bold text-rose-400">{b.ip_address}</td>
                    <td className="py-2.5 px-4 text-slate-300 font-sans text-[11px]">{b.reason}</td>
                    <td className="py-2.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                        {b.is_permanent ? 'PERMANENT_BAN' : 'TEMPORARY_24H'}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-slate-400 text-[10px]">
                      {new Date(b.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Manual Ban Modal */}
        {showBanModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Ban className="w-5 h-5 text-rose-500" />
                  Quarantine IP Address
                </h3>
                <button onClick={() => setShowBanModal(false)} className="text-slate-400 hover:text-white font-bold">&times;</button>
              </div>

              <form onSubmit={handleManualBan} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Target IPv4 / IPv6 Address</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. 198.51.100.44"
                    value={banIp}
                    onChange={(e) => setBanIp(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono focus:outline-none focus:border-rose-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Quarantine Justification</label>
                  <textarea
                    required
                    rows={2}
                    placeholder="e.g. Malicious port scan detected by external IDS"
                    value={banReason}
                    onChange={(e) => setBanReason(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-rose-500"
                  />
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowBanModal(false)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl font-semibold shadow-lg shadow-rose-600/20"
                  >
                    Apply Perimeter Ban
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
