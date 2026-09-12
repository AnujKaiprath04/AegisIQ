'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import {
  SearchCode,
  Sliders,
  ShieldCheck,
  Zap,
  TrendingUp,
  AlertTriangle,
  ArrowRight,
  RefreshCw,
  Layers,
  Sparkles,
  BarChart3,
  CheckCircle2,
  Info,
  SlidersHorizontal,
  ChevronRight,
  Shield,
} from 'lucide-react';

interface GlobalFeature {
  feature_name: string;
  mean_shap_value: number;
  relative_importance_pct: number;
  primary_impact: string;
  description: string;
}

interface GlobalImportanceResponse {
  model_name: string;
  model_type: string;
  base_value: number;
  features: GlobalFeature[];
}

interface LocalContribution {
  feature_name: string;
  feature_value: string;
  shap_value: number;
  contribution_direction: string;
  importance_rank: number;
}

interface WaterfallResponse {
  session_id: number;
  entity_name: string;
  model_type: string;
  base_value: number;
  predicted_value: number;
  explanation_method: string;
  contributions: LocalContribution[];
  executive_summary: string;
}

interface FairnessResponse {
  disparate_impact_ratio: number;
  equal_opportunity_difference: number;
  demographic_parity_score: number;
  fairness_verdict: string;
  cohort_parity_breakdown: Record<string, number>;
  audit_timestamp: string;
}

export default function XAIPage() {
  const { user } = useAuth();
  const [globalData, setGlobalData] = useState<GlobalImportanceResponse | null>(null);
  const [waterfallData, setWaterfallData] = useState<WaterfallResponse | null>(null);
  const [fairnessData, setFairnessData] = useState<FairnessResponse | null>(null);
  const [loading, setLoading] = useState(true);

  // What-If Simulation State
  const [activeSeatsPct, setActiveSeatsPct] = useState<number>(85);
  const [overdueDays, setOverdueDays] = useState<number>(0);
  const [supportTickets, setSupportTickets] = useState<number>(0);
  const [contractMonths, setContractMonths] = useState<number>(24);
  const [simResult, setSimResult] = useState<any>(null);
  const [simulating, setSimulating] = useState(false);

  const fetchXAIData = async () => {
    setLoading(true);
    try {
      const [gRes, wRes, fRes] = await Promise.all([
        apiClient.get<GlobalImportanceResponse>('/xai/global-importance'),
        apiClient.get<WaterfallResponse>('/xai/explain'),
        apiClient.get<FairnessResponse>('/xai/fairness'),
      ]);
      setGlobalData(gRes.data);
      setWaterfallData(wRes.data);
      setFairnessData(fRes.data);
    } catch (err) {
      console.error('Error loading XAI data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRunSimulation = async () => {
    setSimulating(true);
    try {
      const res = await apiClient.post('/xai/what-if', {
        weekly_active_seats_pct: activeSeatsPct,
        invoice_overdue_days: overdueDays,
        support_ticket_count: supportTickets,
        contract_length_months: contractMonths,
      });
      setSimResult(res.data);
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setSimulating(false);
    }
  };

  useEffect(() => {
    fetchXAIData();
    handleRunSimulation();
  }, []);

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-2">
              <SearchCode className="w-3.5 h-3.5" />
              <span>Explainable AI (XAI) & Model Transparency Studio</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">Explainable AI & Algorithmic Transparency</h1>
            <p className="text-xs text-slate-400 mt-1">
              Global SHAP feature importance rankings, local instance waterfall decision breakdowns, and interactive counterfactual what-if simulations.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchXAIData}
              disabled={loading}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Explainability Metrics"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Top Metric Cards */}
        {globalData && waterfallData && fairnessData && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Baseline Expectation E[f(x)]</span>
              <p className="text-2xl font-bold text-white font-mono">{(globalData.base_value * 100).toFixed(1)}%</p>
              <p className="text-[11px] text-slate-400">Population mean baseline risk</p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Leading Risk Driver</span>
              <p className="text-2xl font-bold text-rose-400 font-mono">Active Seats (34.2%)</p>
              <p className="text-[11px] text-rose-300">Highest predictive sensitivity</p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Algorithmic Fairness Status</span>
              <p className="text-2xl font-bold text-emerald-400 font-mono">Certified Fair</p>
              <p className="text-[11px] text-emerald-300 font-mono">Disparate Impact: {fairnessData.disparate_impact_ratio}</p>
            </div>

            <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-1">
              <span className="text-xs font-medium text-slate-400">Demographic Parity Score</span>
              <p className="text-2xl font-bold text-blue-400 font-mono">{fairnessData.demographic_parity_score}%</p>
              <p className="text-[11px] text-slate-400 font-mono">Zero cohort demographic bias</p>
            </div>
          </div>
        )}

        {/* Global SHAP Feature Importance Ranking */}
        {globalData && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-blue-500" />
                  Global SHAP Feature Importance Rankings
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">{globalData.model_name}</p>
              </div>
              <span className="text-xs text-slate-400 font-mono">Mean Absolute SHAP Magnitude</span>
            </div>

            <div className="space-y-3">
              {globalData.features.map((feat, idx) => (
                <div key={idx} className="p-3.5 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center font-bold text-[10px] font-mono">
                        #{idx + 1}
                      </span>
                      <span className="font-bold text-white font-sans">{feat.feature_name}</span>
                    </div>

                    <div className="flex items-center gap-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                          feat.primary_impact === 'PROTECTIVE_DRIVER'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                        }`}
                      >
                        {feat.primary_impact.replace('_', ' ')}
                      </span>
                      <span className="font-mono font-bold text-white text-xs">{feat.relative_importance_pct}%</span>
                    </div>
                  </div>

                  {/* Horizontal Bar */}
                  <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                    <div
                      style={{ width: `${feat.relative_importance_pct * 2.5}%` }}
                      className={`h-full rounded-full ${
                        feat.primary_impact === 'PROTECTIVE_DRIVER' ? 'bg-emerald-500' : 'bg-rose-500'
                      }`}
                    />
                  </div>

                  <p className="text-[11px] text-slate-400 leading-relaxed">{feat.description}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Local Instance Decision Explainer (Waterfall Progression) */}
        {waterfallData && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-400" />
                  Local Instance Waterfall Decision Explainer: {waterfallData.entity_name}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Method: {waterfallData.explanation_method} &bull; Exact additive feature attribution breakdown
                </p>
              </div>
              <span className="px-3 py-1 bg-slate-950 border border-slate-800 rounded-xl text-xs font-mono text-rose-400 font-bold">
                Final Prediction: {waterfallData.predicted_value}% Churn Probability
              </span>
            </div>

            {/* Waterfall Steps Visual Progression */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-3 pt-2">
              {/* Step 0: Baseline E[f(x)] */}
              <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-2xl flex flex-col justify-between space-y-2">
                <span className="text-[10px] font-mono font-bold text-slate-400 uppercase">Base Expectation</span>
                <div>
                  <p className="text-xl font-bold font-mono text-white">{waterfallData.base_value}%</p>
                  <p className="text-[10px] text-slate-500">Population Mean</p>
                </div>
                <span className="text-[9px] font-mono text-slate-600">Start Point E[f(x)]</span>
              </div>

              {/* Step Contributions */}
              {waterfallData.contributions.map((c, idx) => (
                <div
                  key={idx}
                  className={`p-3.5 rounded-2xl border flex flex-col justify-between space-y-2 ${
                    c.shap_value > 0
                      ? 'bg-rose-950/20 border-rose-800/60'
                      : 'bg-emerald-950/20 border-emerald-800/60'
                  }`}
                >
                  <span className="text-[10px] font-mono font-bold text-slate-400 uppercase truncate">
                    {c.feature_name}
                  </span>
                  <div>
                    <p
                      className={`text-xl font-bold font-mono ${
                        c.shap_value > 0 ? 'text-rose-400' : 'text-emerald-400'
                      }`}
                    >
                      {c.shap_value > 0 ? `+${c.shap_value}%` : `${c.shap_value}%`}
                    </p>
                    <p className="text-[10px] text-slate-300 truncate">{c.feature_value}</p>
                  </div>
                  <span
                    className={`text-[9px] font-mono font-bold ${
                      c.shap_value > 0 ? 'text-rose-400' : 'text-emerald-400'
                    }`}
                  >
                    {c.shap_value > 0 ? 'Pushes Risk Up' : 'Protective Factor'}
                  </span>
                </div>
              ))}

              {/* Final Output */}
              <div className="p-3.5 bg-rose-950/40 border border-rose-600 rounded-2xl flex flex-col justify-between space-y-2 shadow-lg shadow-rose-950/30">
                <span className="text-[10px] font-mono font-bold text-rose-300 uppercase">Final Output</span>
                <div>
                  <p className="text-xl font-bold font-mono text-rose-400">{waterfallData.predicted_value}%</p>
                  <p className="text-[10px] text-rose-200">High Churn Risk</p>
                </div>
                <span className="text-[9px] font-mono text-rose-300">Model Output f(x)</span>
              </div>
            </div>

            {/* Plain English Summary */}
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-2xl text-xs text-slate-300 leading-relaxed">
              <span className="text-white font-bold block mb-1">Executive Decision Interpretation:</span>
              <div
                dangerouslySetInnerHTML={{
                  __html: waterfallData.executive_summary
                    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white">$1</strong>'),
                }}
              />
            </div>
          </div>
        )}

        {/* Counterfactual What-If Scenario Simulator */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <SlidersHorizontal className="w-4 h-4 text-blue-500" />
                Interactive Counterfactual What-If Simulator
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Simulate executive interventions by dynamically adjusting account attributes and observing updated risk trajectories
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Sliders Area */}
            <div className="space-y-4 bg-slate-950/60 border border-slate-800 p-5 rounded-2xl text-xs">
              <div>
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span className="text-slate-300">Weekly Active Seat Engagement</span>
                  <span className="font-mono text-blue-400 font-bold">{activeSeatsPct}%</span>
                </div>
                <input
                  type="range"
                  min={10}
                  max={100}
                  value={activeSeatsPct}
                  onChange={(e) => {
                    setActiveSeatsPct(Number(e.target.value));
                    handleRunSimulation();
                  }}
                  className="w-full accent-blue-500 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span className="text-slate-300">Invoice Overdue Latency</span>
                  <span className="font-mono text-rose-400 font-bold">{overdueDays} Days</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={60}
                  value={overdueDays}
                  onChange={(e) => {
                    setOverdueDays(Number(e.target.value));
                    handleRunSimulation();
                  }}
                  className="w-full accent-rose-500 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span className="text-slate-300">Open Support Ticket Escalations</span>
                  <span className="font-mono text-amber-400 font-bold">{supportTickets} Tickets</span>
                </div>
                <input
                  type="range"
                  min={0}
                  max={10}
                  value={supportTickets}
                  onChange={(e) => {
                    setSupportTickets(Number(e.target.value));
                    handleRunSimulation();
                  }}
                  className="w-full accent-amber-500 cursor-pointer"
                />
              </div>

              <div>
                <div className="flex items-center justify-between font-semibold mb-1">
                  <span className="text-slate-300">Contract Length Commitment</span>
                  <span className="font-mono text-emerald-400 font-bold">{contractMonths} Months</span>
                </div>
                <input
                  type="range"
                  min={6}
                  max={36}
                  step={6}
                  value={contractMonths}
                  onChange={(e) => {
                    setContractMonths(Number(e.target.value));
                    handleRunSimulation();
                  }}
                  className="w-full accent-emerald-500 cursor-pointer"
                />
              </div>
            </div>

            {/* Simulation Result Card */}
            {simResult && (
              <div className="bg-slate-950 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between space-y-4">
                <div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                    Counterfactual Trajectory Comparison
                  </span>

                  <div className="grid grid-cols-2 gap-3 p-3 bg-slate-900/60 rounded-xl border border-slate-800">
                    <div>
                      <span className="text-[10px] text-slate-500 block">Original Risk</span>
                      <span className="text-xl font-bold font-mono text-rose-400">
                        {simResult.original_churn_probability_pct}%
                      </span>
                    </div>
                    <div>
                      <span className="text-[10px] text-slate-500 block">Simulated Risk</span>
                      <span className="text-xl font-bold font-mono text-emerald-400">
                        {simResult.simulated_churn_probability_pct}%
                      </span>
                    </div>
                  </div>

                  <div className="mt-3 p-3 bg-blue-950/30 border border-blue-800/40 rounded-xl">
                    <span className="text-[11px] font-bold text-blue-300 flex items-center gap-1.5 mb-1">
                      <Zap className="w-3.5 h-3.5 text-amber-400" />
                      Prescribed Executive Takeaway
                    </span>
                    <p className="text-[11px] text-slate-300 leading-relaxed">{simResult.recommendation}</p>
                  </div>
                </div>

                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">Net Risk Delta:</span>
                  <span
                    className={`font-bold ${
                      simResult.delta_pct < 0 ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {simResult.delta_pct}%
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Model Fairness & Bias Auditor */}
        {fairnessData && (
          <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  Algorithmic Fairness & Bias Governance Audit
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Validates model predictions across geographic cohorts to prevent discriminatory or disparate bias
                </p>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                {fairnessData.fairness_verdict.replace('_', ' ')}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {Object.entries(fairnessData.cohort_parity_breakdown).map(([cohort, score]) => (
                <div key={cohort} className="p-3 bg-slate-950/60 border border-slate-800 rounded-2xl space-y-1">
                  <span className="text-[10px] text-slate-400 truncate block">{cohort}</span>
                  <p className="text-base font-bold font-mono text-emerald-400">{(score * 100).toFixed(1)}%</p>
                  <span className="text-[9px] text-slate-500 font-mono">Parity Ratio</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </EnterpriseShell>
  );
}
