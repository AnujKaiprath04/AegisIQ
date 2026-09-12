'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import {
  BellRing,
  Bell,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ShieldAlert,
  TrendingUp,
  Workflow,
  CheckCheck,
  Send,
  Zap,
  RefreshCw,
  Plus,
  Radio,
  Sliders,
  ExternalLink,
  MessageSquare,
  Clock,
  Check,
  Globe,
} from 'lucide-react';

interface NotificationItem {
  id: number;
  title: string;
  message: string;
  category: string;
  severity: string;
  is_read: boolean;
  action_url?: string;
  delivery_channel: string;
  created_at: string;
}

interface AlertRule {
  id: number;
  name: string;
  trigger_event: string;
  threshold_condition: string;
  severity: string;
  channel_in_app: boolean;
  channel_email: boolean;
  channel_webhook: boolean;
  webhook_url?: string;
  is_active: boolean;
  created_at: string;
}

export default function NotificationsPage() {
  const { hasRole } = useAuth();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [unreadOnly, setUnreadOnly] = useState(false);
  const [loading, setLoading] = useState(true);

  // Webhook Simulator State
  const [webhookUrl, setWebhookUrl] = useState('https://hooks.slack.com/services/T123/B456/7890');
  const [webhookChannel, setWebhookChannel] = useState('Slack Enterprise Security Channel');
  const [webhookResult, setWebhookResult] = useState<any>(null);
  const [dispatching, setDispatching] = useState(false);

  // Create Rule Modal
  const [showRuleModal, setShowRuleModal] = useState(false);
  const [ruleName, setRuleName] = useState('');
  const [triggerEvent, setTriggerEvent] = useState('KPI_VARIANCE_BREACH');
  const [thresholdCondition, setThresholdCondition] = useState('Variance <= -8.0%');
  const [ruleSeverity, setRuleSeverity] = useState('HIGH');
  const [chanInApp, setChanInApp] = useState(true);
  const [chanEmail, setChanEmail] = useState(true);
  const [chanWebhook, setChanWebhook] = useState(false);
  const [ruleWebhookUrl, setRuleWebhookUrl] = useState('');

  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const fetchNotificationData = async () => {
    setLoading(true);
    try {
      let queryUrl = '/notifications';
      const params: string[] = [];
      if (categoryFilter !== 'ALL') params.push(`category=${categoryFilter}`);
      if (unreadOnly) params.push('unread_only=true');
      if (params.length > 0) queryUrl += `?${params.join('&')}`;

      const [nRes, rRes] = await Promise.all([
        apiClient.get<NotificationItem[]>(queryUrl),
        apiClient.get<AlertRule[]>('/notifications/rules'),
      ]);
      setNotifications(nRes.data || []);
      setRules(rRes.data || []);
    } catch (err) {
      console.error('Error fetching notification hub data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotificationData();
  }, [categoryFilter, unreadOnly]);

  const handleMarkRead = async (id: number) => {
    try {
      await apiClient.post(`/notifications/${id}/read`);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch (err) {
      console.error('Failed to mark read:', err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      const res = await apiClient.post('/notifications/mark-all-read');
      setNotification({ message: res.data.message, type: 'success' });
      fetchNotificationData();
    } catch (err) {
      console.error('Failed to mark all read:', err);
    }
  };

  const handleToggleRule = async (ruleId: number) => {
    try {
      const res = await apiClient.post(`/notifications/rules/${ruleId}/toggle`);
      setRules((prev) => prev.map((r) => (r.id === ruleId ? res.data : r)));
    } catch (err) {
      console.error('Failed to toggle rule:', err);
    }
  };

  const handleTestWebhook = async (e: React.FormEvent) => {
    e.preventDefault();
    setDispatching(true);
    try {
      const res = await apiClient.post('/notifications/webhook/test', {
        webhook_url: webhookUrl,
        channel_name: webhookChannel,
      });
      setWebhookResult(res.data);
      setNotification({ message: 'Webhook test payload acknowledged successfully.', type: 'success' });
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Webhook dispatch failed.', type: 'error' });
    } finally {
      setDispatching(false);
    }
  };

  const handleCreateRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/notifications/rules', {
        name: ruleName,
        trigger_event: triggerEvent,
        threshold_condition: thresholdCondition,
        severity: ruleSeverity,
        channel_in_app: chanInApp,
        channel_email: chanEmail,
        channel_webhook: chanWebhook,
        webhook_url: chanWebhook ? ruleWebhookUrl : null,
      });
      setNotification({ message: `Alert Rule '${ruleName}' configured successfully.`, type: 'success' });
      setShowRuleModal(false);
      setRuleName('');
      fetchNotificationData();
    } catch (err: any) {
      setNotification({ message: err.response?.data?.detail || 'Failed to create rule.', type: 'error' });
    }
  };

  const canConfigure = hasRole(['Admin', 'Executive']);

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-2">
              <BellRing className="w-3.5 h-3.5" />
              <span>Real-time Multi-Channel Notification & Alerting Hub</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise Multi-Channel Alert Hub</h1>
            <p className="text-xs text-slate-400 mt-1">
              Automated event triggers, KPI variance breaches, SIEM security alerts, and live Slack / Teams webhook dispatching.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchNotificationData}
              disabled={loading}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Feeds"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={handleMarkAllRead}
              className="inline-flex items-center gap-2 px-3.5 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs font-semibold border border-slate-700 transition-colors"
            >
              <CheckCheck className="w-4 h-4 text-emerald-400" />
              Mark All Read
            </button>
            {canConfigure && (
              <button
                onClick={() => setShowRuleModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-semibold shadow-lg shadow-blue-600/20 transition-all"
              >
                <Plus className="w-4 h-4" />
                New Alert Rule
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

        {/* Top Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
            <span className="text-xs font-medium text-slate-400">Total Feed Items</span>
            <p className="text-2xl font-bold text-white font-mono">{notifications.length}</p>
            <p className="text-[11px] text-slate-400">Aggregated platform events</p>
          </div>


          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
            <span className="text-xs font-medium text-slate-400">Unread Alert Queue</span>
            <p className="text-2xl font-bold text-rose-400 font-mono">
              {notifications.filter((n) => !n.is_read).length} Unread
            </p>
            <p className="text-[11px] text-rose-300">Requires executive review</p>
          </div>

          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
            <span className="text-xs font-medium text-slate-400">Active Alert Trigger Rules</span>
            <p className="text-2xl font-bold text-blue-400 font-mono">
              {rules.filter((r) => r.is_active).length} Rules
            </p>
            <p className="text-[11px] text-blue-300">Automated multi-channel routing</p>
          </div>

          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
            <span className="text-xs font-medium text-slate-400">Webhook Dispatch Relay</span>
            <p className="text-2xl font-bold text-emerald-400 font-mono">200 OK</p>
            <p className="text-[11px] text-slate-400 font-mono">Avg Relay Latency: 38.4ms</p>
          </div>
        </div>

        {/* In-App Notification Feed */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Bell className="w-4 h-4 text-blue-500" />
                Live Notification Stream
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Real-time incident dispatches and metric variance announcements
              </p>
            </div>

            {/* Category Filter Pills & Unread Checkbox */}
            <div className="flex flex-wrap items-center gap-3">
              <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
                <input
                  type="checkbox"
                  checked={unreadOnly}
                  onChange={(e) => setUnreadOnly(e.target.checked)}
                  className="rounded accent-blue-500"
                />
                <span>Unread Only</span>
              </label>

              <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-2xl border border-slate-800 text-xs">
                {['ALL', 'SECURITY', 'CHURN_ALERT', 'FINANCIAL', 'DATA_QUALITY'].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setCategoryFilter(cat)}
                    className={`px-3 py-1 rounded-xl font-semibold transition-all ${
                      categoryFilter === cat
                        ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    {cat.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-3">
            {loading ? (
              <div className="py-12 text-center text-slate-500">
                <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-500" />
                Sampling notification telemetry...
              </div>
            ) : notifications.length === 0 ? (
              <div className="py-12 text-center text-slate-500">
                No notifications found matching the selected filter criteria.
              </div>
            ) : (
              notifications.map((item) => (
                <div
                  key={item.id}
                  className={`p-4 rounded-2xl border transition-all text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                    item.is_read
                      ? 'bg-slate-950/40 border-slate-800/60 opacity-80'
                      : 'bg-slate-950/90 border-blue-500/30 shadow-lg shadow-blue-950/20'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-9 h-9 rounded-xl flex items-center justify-center shrink-0 ${
                        item.severity === 'CRITICAL'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          : item.severity === 'HIGH'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                      }`}
                    >
                      {item.category === 'SECURITY' ? (
                        <ShieldAlert className="w-4 h-4" />
                      ) : item.category === 'CHURN_ALERT' ? (
                        <AlertTriangle className="w-4 h-4" />
                      ) : item.category === 'FINANCIAL' ? (
                        <TrendingUp className="w-4 h-4" />
                      ) : (
                        <Workflow className="w-4 h-4" />
                      )}
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        {!item.is_read && (
                          <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                        )}
                        <span className="font-bold text-white text-xs">{item.title}</span>
                        <span className="px-2 py-0.2 rounded text-[9px] font-mono font-bold bg-slate-900 border border-slate-800 text-slate-400">
                          {item.category}
                        </span>
                      </div>
                      <p className="text-slate-300 leading-relaxed text-[11px]">{item.message}</p>
                      <span className="text-[10px] text-slate-500 font-mono block">
                        {new Date(item.created_at).toLocaleString()} &bull; Channel: {item.delivery_channel}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 self-end sm:self-center shrink-0">
                    {item.action_url && (
                      <Link
                        href={item.action_url}
                        className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-blue-400 hover:text-white rounded-xl text-xs font-semibold transition-all border border-slate-700 flex items-center gap-1.5"
                      >
                        <ExternalLink className="w-3 h-3" />
                        Take Action
                      </Link>
                    )}
                    {!item.is_read && (
                      <button
                        onClick={() => handleMarkRead(item.id)}
                        className="p-1.5 text-slate-400 hover:text-emerald-400 hover:bg-slate-800 rounded-lg transition-colors"
                        title="Mark as Read"
                      >
                        <Check className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Automated Alert Rules & Webhook Relay Simulator */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Rules Configurator */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-emerald-400" />
                  Automated Alert Rules ({rules.length})
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Threshold triggers across platform subsystems</p>
              </div>
            </div>

            <div className="space-y-3">
              {rules.map((r) => (
                <div
                  key={r.id}
                  className="p-4 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span
                        className={`w-2 h-2 rounded-full ${
                          r.is_active ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'
                        }`}
                      />
                      <span className="font-bold text-white text-xs">{r.name}</span>
                    </div>

                    <button
                      onClick={() => handleToggleRule(r.id)}
                      disabled={!canConfigure}
                      className={`px-2.5 py-0.5 rounded text-[10px] font-bold font-mono transition-all ${
                        r.is_active
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20'
                          : 'bg-slate-800 text-slate-500 border border-slate-700 hover:bg-slate-700'
                      }`}
                    >
                      {r.is_active ? 'ENABLED' : 'PAUSED'}
                    </button>
                  </div>

                  <div className="p-2 bg-slate-900/60 rounded-xl border border-slate-800/80 font-mono text-[10px] text-slate-300 flex items-center justify-between">
                    <span>Condition: <code className="text-amber-400">{r.threshold_condition}</code></span>
                    <span className="text-slate-500">Trigger: {r.trigger_event}</span>
                  </div>

                  {/* Channel Badges */}
                  <div className="flex items-center gap-2 pt-1 font-mono text-[9px]">
                    <span className="text-slate-500">Channels:</span>
                    {r.channel_in_app && (
                      <span className="px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        IN_APP
                      </span>
                    )}
                    {r.channel_email && (
                      <span className="px-1.5 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                        EMAIL
                      </span>
                    )}
                    {r.channel_webhook && (
                      <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        WEBHOOK
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Webhook Dispatch Simulator */}
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Send className="w-4 h-4 text-blue-400" />
                  Enterprise Webhook Dispatch Simulator
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">Test real-time JSON webhook payloads to Slack / Teams</p>
              </div>
            </div>

            <form onSubmit={handleTestWebhook} className="space-y-3 text-xs">
              <div>
                <label className="block text-slate-400 font-semibold mb-1">Target Webhook Receptor URL</label>
                <input
                  type="text"
                  required
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-slate-400 font-semibold mb-1">Channel Label</label>
                <input
                  type="text"
                  required
                  value={webhookChannel}
                  onChange={(e) => setWebhookChannel(e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={dispatching || !canConfigure}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold shadow-lg shadow-blue-600/20 transition-all flex items-center justify-center gap-2 disabled:opacity-40"
              >
                <Send className={`w-3.5 h-3.5 ${dispatching ? 'animate-spin' : ''}`} />
                {dispatching ? 'Dispatching Payload...' : 'Send Test Webhook Alert'}
              </button>
            </form>

            {/* Test Result Box */}
            {webhookResult && (
              <div className="p-3.5 bg-slate-950 border border-emerald-800/40 rounded-2xl space-y-1.5 text-xs font-mono">
                <div className="flex items-center justify-between text-emerald-400 font-bold">
                  <span className="flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    HTTP {webhookResult.response_status_code} OK
                  </span>
                  <span className="text-slate-400 text-[10px]">{webhookResult.latency_ms}ms Latency</span>
                </div>
                <p className="text-[11px] text-slate-300">{webhookResult.response_body}</p>
              </div>
            )}
          </div>
        </div>

        {/* Create Rule Modal */}
        {showRuleModal && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Plus className="w-5 h-5 text-blue-500" />
                  Configure New Alert Rule
                </h3>
                <button onClick={() => setShowRuleModal(false)} className="text-slate-400 hover:text-white font-bold">&times;</button>
              </div>

              <form onSubmit={handleCreateRule} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Rule Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Executive Margin Alert"
                    value={ruleName}
                    onChange={(e) => setRuleName(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Trigger Event</label>
                  <select
                    value={triggerEvent}
                    onChange={(e) => setTriggerEvent(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="KPI_VARIANCE_BREACH">KPI Metric Variance Breach</option>
                    <option value="SECURITY_INCIDENT_HIGH">SIEM High/Critical Security Threat</option>
                    <option value="HIGH_CHURN_RISK">Customer Churn Escalation</option>
                    <option value="ETL_QUALITY_DROP">ETL Quality Score Degradation</option>
                    <option value="REPORT_READY">Scheduled Executive Brief Generated</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Threshold Condition</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Variance <= -8.0%"
                    value={thresholdCondition}
                    onChange={(e) => setThresholdCondition(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div className="space-y-2 pt-2 border-t border-slate-800">
                  <span className="block text-slate-400 font-semibold">Delivery Channels</span>
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={chanInApp}
                        onChange={(e) => setChanInApp(e.target.checked)}
                        className="rounded accent-blue-500"
                      />
                      <span>In-App</span>
                    </label>
                    <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={chanEmail}
                        onChange={(e) => setChanEmail(e.target.checked)}
                        className="rounded accent-blue-500"
                      />
                      <span>Email</span>
                    </label>
                    <label className="flex items-center gap-1.5 text-slate-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={chanWebhook}
                        onChange={(e) => setChanWebhook(e.target.checked)}
                        className="rounded accent-blue-500"
                      />
                      <span>Webhook</span>
                    </label>
                  </div>
                </div>

                {chanWebhook && (
                  <div>
                    <label className="block text-slate-400 font-semibold mb-1">Webhook URL</label>
                    <input
                      type="text"
                      placeholder="https://hooks.slack.com/..."
                      value={ruleWebhookUrl}
                      onChange={(e) => setRuleWebhookUrl(e.target.value)}
                      className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white font-mono focus:outline-none focus:border-blue-500"
                    />
                  </div>
                )}

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setShowRuleModal(false)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-600/20"
                  >
                    Save Alert Rule
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
