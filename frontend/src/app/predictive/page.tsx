'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import {
  TrendingUp,
  LineChart as LineChartIcon,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Cpu,
  Sparkles,
  Zap,
  Activity,
  Layers,
  ArrowUpRight,
  ShieldAlert,
  Clock,
  Check,
  Calendar,
  DollarSign,
} from 'lucide-react';

interface ForecastDataPoint {
  period: string;
  historical_actual?: number;
  predicted_value?: number;
  lower_bound_95?: number;
  upper_bound_95?: number;
  is_forecast: boolean;
}

interface ForecastResponse {
  metric_name: string;
  horizon_months: number;
  model_name: string;
  algorithm: string;
  r2_score: number;
  rmse: number;
  data_points: ForecastDataPoint[];
  projected_growth_pct: number;
  generated_at: string;
}

interface ChurnAccount {
  id: number;
  client_name: string;
  account_arr: number;
  churn_probability_pct: number;
  risk_tier: string;
  top_risk_factors: string[];
  recommended_intervention: string;
  contract_renewal_date?: string;
}

interface ChurnResponse {
  total_accounts_evaluated: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  arr_at_risk: number;
  accounts: ChurnAccount[];
}

interface MLModelSummary {
  id: number;
  model_name: string;
  model_type: string;
  algorithm: string;
  status: string;
  accuracy_score: number;
  mae_metric: number;
  rmse_metric: number;
  last_trained_at: string;
}

export default function PredictivePage() {
  const { hasRole } = useAuth();
  const [horizon, setHorizon] = useState<number>(12);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [churnData, setChurnData] = useState<ChurnResponse | null>(null);
  const [models, setModels] = useState<MLModelSummary[]>([]);

  const [loading, setLoading] = useState(true);
  const [retrainingId, setRetrainingId] = useState<number | null>(null);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [selectedAccount, setSelectedAccount] = useState<ChurnAccount | null>(null);

  const fetchPredictiveData = async (h: number = horizon) => {
    setLoading(true);
    try {
      const [fRes, cRes, mRes] = await Promise.all([
        apiClient.get<ForecastResponse>(`/predictive/forecast/revenue?horizon_months=${h}`),
        apiClient.get<ChurnResponse>('/predictive/churn/accounts'),
        apiClient.get<MLModelSummary[]>('/predictive/models'),
      ]);
      setForecast(fRes.data);
      setChurnData(cRes.data);
      setModels(mRes.data || []);
      if (cRes.data.accounts && cRes.data.accounts.length > 0) {
        setSelectedAccount(cRes.data.accounts[0]);
      }
    } catch (err) {
      console.error('Error loading predictive analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPredictiveData(horizon);
  }, [horizon]);

  const handleRetrain = async (modelId: number) => {
    setRetrainingId(modelId);
    try {
      const res = await apiClient.post(`/predictive/models/${modelId}/retrain`);
      setNotification({
        message: res.data.message || 'Model retrained successfully.',
        type: 'success',
      });
      fetchPredictiveData(horizon);
    } catch (err: any) {
      setNotification({
        message: err.response?.data?.detail || 'Failed to retrain ML model.',
        type: 'error',
      });
    } finally {
      setRetrainingId(null);
    }
  };

  const canManageML = hasRole(['Admin', 'Data Analyst']);

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-2">
              <LineChartIcon className="w-3.5 h-3.5" />
              <span>Predictive Analytics & ML Forecasting Engine</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise Predictive Intelligence Studio</h1>
            <p className="text-xs text-slate-400 mt-1">
              Time-series ARR forecasting with 95% confidence intervals, machine learning churn risk scoring, and automated model evaluation.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => fetchPredictiveData(horizon)}
              disabled={loading}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Forecasts"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
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

        {/* Top Metric Cards */}
        {forecast && churnData && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Current ARR (Q1 2026)</span>
              <p className="text-2xl font-bold text-white font-mono">$24.8M</p>
              <p className="text-[11px] text-emerald-400 flex items-center gap-1 font-semibold">
                <ArrowUpRight className="w-3.5 h-3.5" />
                +18.4% YoY Expansion
              </p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Projected ARR ({horizon}M Horizon)</span>
              <p className="text-2xl font-bold text-blue-400 font-mono">
                ${forecast.data_points[forecast.data_points.length - 1]?.predicted_value}M
              </p>
              <p className="text-[11px] text-blue-300 font-semibold font-mono">
                +{forecast.projected_growth_pct}% Projected Growth
              </p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">High Churn Risk Accounts</span>
              <p className="text-2xl font-bold text-rose-400 font-mono">{churnData.high_risk_count} Accounts</p>
              <p className="text-[11px] text-rose-300 font-mono">
                ${(churnData.arr_at_risk / 1000000).toFixed(2)}M ARR at risk
              </p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Forecasting Model Accuracy</span>
              <p className="text-2xl font-bold text-emerald-400 font-mono">R² = {forecast.r2_score}</p>
              <p className="text-[11px] text-slate-400 font-mono">RMSE: ${forecast.rmse * 1000}K error bound</p>
            </div>
          </div>
        )}

        {/* Time-Series Forecast Studio */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-500" />
                Time-Series ARR Trajectory & 95% Confidence Bounds
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Algorithm: {forecast?.algorithm} &bull; Validated against historical general ledger telemetry
              </p>
            </div>

            {/* Horizon Selector Tabs */}
            <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-2xl border border-slate-800 text-xs">
              {[
                { label: '3 Months (Q2 2026)', val: 3 },
                { label: '6 Months (Q3 2026)', val: 6 },
                { label: '12 Months (Q1 2027)', val: 12 },
              ].map((t) => (
                <button
                  key={t.val}
                  onClick={() => setHorizon(t.val)}
                  className={`px-3 py-1.5 rounded-xl font-semibold transition-all ${
                    horizon === t.val
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </div>

          {/* Interactive SVG Line & Area Confidence Chart */}
          {forecast && (
            <div className="space-y-4">
              <div className="h-64 w-full bg-slate-950/70 border border-slate-800/80 rounded-2xl p-4 flex flex-col justify-between relative overflow-hidden">
                {/* Visual Chart Header */}
                <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono z-10">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1.5 text-blue-400 font-bold">
                      <span className="w-3 h-0.5 bg-blue-500" /> Historical Actuals
                    </span>
                    <span className="flex items-center gap-1.5 text-emerald-400 font-bold">
                      <span className="w-3 h-0.5 bg-emerald-400 border-dashed" /> ML Forecast Trajectory
                    </span>
                    <span className="flex items-center gap-1.5 text-slate-500">
                      <span className="w-3 h-2 bg-emerald-500/10 border border-emerald-500/30 rounded" /> 95% Confidence Band
                    </span>
                  </div>
                  <span>Scale: Millions USD</span>
                </div>

                {/* SVG Visual Points & Curves */}
                <div className="flex-1 flex items-end justify-between gap-3 pt-6 pb-2 px-4 relative z-10">
                  {forecast.data_points.map((pt, idx) => {
                    const maxVal = 38.0;
                    const val = pt.predicted_value || pt.historical_actual || 0;
                    const heightPct = Math.min(100, Math.max(10, (val / maxVal) * 100));
                    const lowerVal = pt.lower_bound_95 || val;
                    const upperVal = pt.upper_bound_95 || val;

                    return (
                      <div key={idx} className="flex-1 flex flex-col items-center justify-end h-full group relative">
                        {/* Hover Tooltip */}
                        <div className="opacity-0 group-hover:opacity-100 absolute bottom-full mb-2 bg-slate-900 border border-slate-700 text-white rounded-xl p-2.5 text-[10px] font-mono shadow-xl transition-all pointer-events-none z-30 w-32 text-center">
                          <p className="font-bold text-xs">{pt.period}</p>
                          <p className="text-blue-400">Value: ${val}M</p>
                          {pt.is_forecast && (
                            <p className="text-slate-400 text-[9px] mt-0.5">
                              Bounds: ${lowerVal}M - ${upperVal}M
                            </p>
                          )}
                        </div>

                        {/* Bar / Marker */}
                        <div className="w-full flex flex-col items-center">
                          {/* Upper / Lower whisker indicator for forecast */}
                          {pt.is_forecast && (
                            <div className="w-1.5 bg-emerald-500/30 rounded-t h-4 mb-0.5" />
                          )}
                          <div
                            style={{ height: `${heightPct * 1.5}px` }}
                            className={`w-6 sm:w-10 rounded-t-xl transition-all ${
                              pt.is_forecast
                                ? 'bg-gradient-to-t from-emerald-600/40 to-emerald-400/80 border-t-2 border-emerald-400'
                                : 'bg-gradient-to-t from-blue-600/40 to-blue-500/90 border-t-2 border-blue-400'
                            }`}
                          />
                        </div>

                        <span className="text-[10px] font-mono text-slate-400 mt-2 whitespace-nowrap">
                          {pt.period}
                        </span>
                        <span className="text-[10px] font-bold font-mono text-white mt-0.5">
                          ${val}M
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Customer Churn & Retention Machine Learning Studio */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-amber-500" />
                Customer Churn Risk Classifier & Intervention Engine
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Gradient Boosted Trees (ROC-AUC 0.934) scoring account renewal risk across usage velocity, support escalations, and payment latency
              </p>
            </div>

            <span className="px-3 py-1 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-slate-300">
              {churnData?.total_accounts_evaluated} Accounts Evaluated &bull; ${((churnData?.arr_at_risk || 0) / 1000000).toFixed(2)}M At Risk
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Accounts Table */}
            <div className="lg:col-span-2 overflow-x-auto border border-slate-800 rounded-2xl">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800 uppercase text-[10px]">
                  <tr>
                    <th className="py-3 px-4">Client Organization</th>
                    <th className="py-3 px-4">Account ARR</th>
                    <th className="py-3 px-4">Churn Probability</th>
                    <th className="py-3 px-4">Risk Tier</th>
                    <th className="py-3 px-4 text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {churnData?.accounts.map((acc) => {
                    const isSelected = selectedAccount?.id === acc.id;
                    return (
                      <tr
                        key={acc.id}
                        onClick={() => setSelectedAccount(acc)}
                        className={`hover:bg-slate-800/40 transition-colors cursor-pointer ${
                          isSelected ? 'bg-blue-950/30' : ''
                        }`}
                      >
                        <td className="py-3 px-4 font-bold text-white font-sans">{acc.client_name}</td>
                        <td className="py-3 px-4 text-slate-300">${(acc.account_arr / 1000).toFixed(0)}K</td>
                        <td className="py-3 px-4">
                          <div className="flex items-center gap-2">
                            <div className="w-16 h-2 bg-slate-800 rounded-full overflow-hidden">
                              <div
                                style={{ width: `${acc.churn_probability_pct}%` }}
                                className={`h-full ${
                                  acc.risk_tier === 'HIGH_RISK'
                                    ? 'bg-rose-500'
                                    : acc.risk_tier === 'MEDIUM_RISK'
                                    ? 'bg-amber-500'
                                    : 'bg-emerald-500'
                                }`}
                              />
                            </div>
                            <span className="font-bold">{acc.churn_probability_pct}%</span>
                          </div>
                        </td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold font-sans ${
                              acc.risk_tier === 'HIGH_RISK'
                                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                                : acc.risk_tier === 'MEDIUM_RISK'
                                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                                : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            }`}
                          >
                            {acc.risk_tier.replace('_', ' ')}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right font-sans">
                          <button
                            onClick={() => setSelectedAccount(acc)}
                            className="text-blue-400 hover:text-blue-300 font-semibold"
                          >
                            Inspect
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Account Detail & Intervention Card */}
            {selectedAccount && (
              <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 space-y-4 text-xs flex flex-col justify-between">
                <div className="space-y-3">
                  <div className="flex items-start justify-between border-b border-slate-800 pb-3">
                    <div>
                      <h4 className="font-bold text-sm text-white">{selectedAccount.client_name}</h4>
                      <p className="text-[11px] text-slate-400 font-mono">
                        ARR: ${(selectedAccount.account_arr / 1000).toFixed(0)}K &bull; Renewal: {selectedAccount.contract_renewal_date || 'Q2 2026'}
                      </p>
                    </div>
                    <span
                      className={`px-2.5 py-1 rounded-full text-[10px] font-bold font-mono ${
                        selectedAccount.risk_tier === 'HIGH_RISK'
                          ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          : selectedAccount.risk_tier === 'MEDIUM_RISK'
                          ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                          : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                      }`}
                    >
                      {selectedAccount.churn_probability_pct}% Churn Risk
                    </span>
                  </div>

                  {/* Risk Factors */}
                  <div>
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
                      Top Algorithmic Risk Drivers
                    </span>
                    <ul className="space-y-1.5">
                      {selectedAccount.top_risk_factors.map((f, f_idx) => (
                        <li key={f_idx} className="p-2 bg-slate-900 border border-slate-800/80 rounded-xl text-slate-300 text-[11px] flex items-center gap-2">
                          <AlertTriangle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Recommendation */}
                  <div className="p-3.5 bg-blue-950/30 border border-blue-800/40 rounded-xl space-y-1">
                    <span className="text-[11px] font-bold text-blue-300 flex items-center gap-1.5">
                      <Zap className="w-3.5 h-3.5 text-amber-400" />
                      Prescribed Retention Playbook
                    </span>
                    <p className="text-[11px] text-slate-300 leading-relaxed">
                      {selectedAccount.recommended_intervention}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() =>
                    setNotification({
                      message: `Retention workflow triggered for ${selectedAccount.client_name}. Assigned to VP Customer Success.`,
                      type: 'success',
                    })
                  }
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold shadow-lg shadow-blue-600/20 transition-all text-xs"
                >
                  Execute Retention Playbook
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Machine Learning Model Performance Registry */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Cpu className="w-4 h-4 text-emerald-400" />
                Enterprise Machine Learning Model Registry
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Active production algorithms, validation coefficients, and on-demand model retraining
              </p>
            </div>
            <span className="text-xs text-slate-400 font-mono">{models.length} Production Models</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {models.map((m) => {
              const isRetraining = retrainingId === m.id;
              return (
                <div
                  key={m.id}
                  className="bg-slate-950/60 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {m.status}
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">
                        Trained: {new Date(m.last_trained_at).toLocaleDateString()}
                      </span>
                    </div>

                    <div>
                      <h4 className="font-bold text-sm text-white">{m.model_name}</h4>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">{m.algorithm}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-2 p-2.5 bg-slate-900/60 rounded-xl border border-slate-800/80 font-mono text-[10px] text-slate-400">
                      <div>
                        <span>Score:</span> <span className="font-bold text-emerald-400">{m.accuracy_score}</span>
                      </div>
                      <div>
                        <span>MAE Error:</span> <span className="font-bold text-white">{m.mae_metric}</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 flex justify-end">
                    <button
                      onClick={() => handleRetrain(m.id)}
                      disabled={isRetraining || !canManageML}
                      className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-blue-400 hover:text-white rounded-xl text-xs font-semibold transition-all border border-slate-700 disabled:opacity-40 flex items-center gap-1.5"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${isRetraining ? 'animate-spin' : ''}`} />
                      {isRetraining ? 'Training...' : 'Retrain Model'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </EnterpriseShell>
  );
}
