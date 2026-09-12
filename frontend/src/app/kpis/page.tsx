'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import { KPIMetric } from '@/types/platform';
import {
  TrendingUp,
  Target,
  Calculator,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Edit2,
  Sparkles,
  RefreshCw,
  Sliders,
  DollarSign,
  PieChart,
  Percent,
} from 'lucide-react';

export default function KPIsPage() {
  const { hasRole } = useAuth();
  const [kpis, setKpis] = useState<KPIMetric[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  // Edit target modal
  const [editingKpi, setEditingKpi] = useState<KPIMetric | null>(null);
  const [targetInput, setTargetInput] = useState<number>(0);
  const [periodInput, setPeriodInput] = useState<string>('Q1 2026');

  // Custom calculation simulator
  const [calcFormula, setCalcFormula] = useState<string>('GROSS_MARGIN');
  const [calcParams, setCalcParams] = useState<Record<string, number>>({
    revenue: 5000000,
    cogs: 1600000,
  });
  const [calcResult, setCalcResult] = useState<any>(null);
  const [calculating, setCalculating] = useState(false);

  const fetchKpis = async () => {
    setLoading(true);
    try {
      let endpoint = '/kpis';
      if (selectedCategory !== 'ALL') endpoint += `?category=${selectedCategory}`;
      const res = await apiClient.get<KPIMetric[]>(endpoint);
      setKpis(res.data || []);
    } catch (err) {
      console.error('Error fetching KPIs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKpis();
  }, [selectedCategory]);

  const handleUpdateTarget = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingKpi) return;

    try {
      await apiClient.put(`/kpis/${editingKpi.id}/target`, {
        target_value: targetInput,
        period: periodInput,
      });
      setEditingKpi(null);
      fetchKpis();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to update target threshold.');
    }
  };

  const handleRunCalculation = async (e: React.FormEvent) => {
    e.preventDefault();
    setCalculating(true);
    try {
      const res = await apiClient.post('/kpis/calculate', {
        formula_type: calcFormula,
        parameters: calcParams,
      });
      setCalcResult(res.data);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Calculation error.');
    } finally {
      setCalculating(false);
    }
  };

  const openTargetModal = (kpi: KPIMetric) => {
    setEditingKpi(kpi);
    setTargetInput(kpi.target_value);
    setPeriodInput(kpi.period);
  };

  const canEditTargets = hasRole(['Admin', 'Executive', 'Business Analyst']);

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold mb-2">
              <TrendingUp className="w-3.5 h-3.5" />
              <span>Enterprise KPI Formula & Variance Engine</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise KPI Engine</h1>
            <p className="text-xs text-slate-400 mt-1">
              Automated mathematical evaluation of corporate metrics, benchmark comparisons, and real-time target variance scoring.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={fetchKpis}
              disabled={loading}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh KPIs"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap items-center gap-2 bg-slate-950/60 p-1.5 rounded-2xl border border-slate-800/80">
          {['ALL', 'FINANCIAL', 'SALES', 'OPERATIONS', 'CUSTOMERS'].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              {cat === 'ALL' ? 'All Metric Categories' : cat.charAt(0) + cat.slice(1).toLowerCase()}
            </button>
          ))}
        </div>

        {/* KPI Scorecards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {loading ? (
            <div className="col-span-3 py-16 text-center text-slate-500 bg-slate-900/40 rounded-3xl border border-slate-800">
              <RefreshCw className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-500" />
              Evaluating KPI equations and calculating variances...
            </div>
          ) : kpis.length === 0 ? (
            <div className="col-span-3 py-12 text-center text-slate-500 bg-slate-900/40 rounded-3xl border border-slate-800">
              No KPI metrics found for this category.
            </div>
          ) : (
            kpis.map((k) => (
              <div
                key={k.id}
                className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl flex flex-col justify-between space-y-4 hover:border-slate-700 transition-all"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase font-mono">
                      {k.category}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold ${
                          k.status === 'ON_TRACK'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : k.status === 'WARNING'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}
                      >
                        {k.status === 'ON_TRACK' ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
                        {k.status.replace('_', ' ')}
                      </span>
                      {canEditTargets && (
                        <button
                          onClick={() => openTargetModal(k)}
                          className="p-1 hover:bg-slate-800 text-slate-400 hover:text-white rounded-lg transition-colors"
                          title="Edit Target Threshold"
                        >
                          <Edit2 className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  </div>

                  <h3 className="text-base font-bold text-white mb-1">{k.name}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed mb-4">{k.description}</p>

                  <div className="grid grid-cols-2 gap-3 p-3 bg-slate-950/60 rounded-2xl border border-slate-800/80">
                    <div>
                      <p className="text-[10px] text-slate-500 font-medium">Actual Value</p>
                      <p className="text-lg font-bold text-white font-mono">
                        {k.unit === '$' ? `$${k.current_value.toLocaleString()}` : `${k.current_value}${k.unit}`}
                      </p>
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-500 font-medium">Target ({k.period})</p>
                      <p className="text-lg font-bold text-slate-300 font-mono">
                        {k.unit === '$' ? `$${k.target_value.toLocaleString()}` : `${k.target_value}${k.unit}`}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono">
                  <span className="text-slate-500">Formula: <code className="text-slate-400">{k.formula_expression || 'Standard'}</code></span>
                  <span className={`font-bold ${k.variance_pct >= 0 ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {k.variance_pct > 0 ? `+${k.variance_pct}%` : `${k.variance_pct}%`} vs target
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Dynamic Formula Evaluator & Simulator */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Calculator className="w-5 h-5 text-blue-500" />
                Dynamic KPI Formula Calculator & Simulator
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Simulate mathematical formulas on custom financial and operational parameters
              </p>
            </div>
            <span className="px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 text-xs font-mono font-bold">
              Mathematical Engine Active
            </span>
          </div>

          <form onSubmit={handleRunCalculation} className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="space-y-3 text-xs">
              <label className="block text-slate-400 font-semibold">Select Target Equation</label>
              <select
                value={calcFormula}
                onChange={(e) => {
                  const f = e.target.value;
                  setCalcFormula(f);
                  if (f === 'GROSS_MARGIN') setCalcParams({ revenue: 5000000, cogs: 1600000 });
                  else if (f === 'CAC') setCalcParams({ sales_marketing_expenses: 600000, new_customers: 40 });
                  else if (f === 'LTV_CAC') setCalcParams({ customer_ltv: 120000, cac: 22000 });
                  else if (f === 'QUICK_RATIO') setCalcParams({ cash_and_equivalents: 4500000, receivables: 1200000, current_liabilities: 1800000 });
                  else if (f === 'EBITDA_MARGIN') setCalcParams({ ebitda: 2800000, revenue: 8000000 });
                }}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500 font-medium"
              >
                <option value="GROSS_MARGIN">Gross Profit Margin % (((Revenue - COGS) / Revenue) * 100)</option>
                <option value="CAC">Customer Acquisition Cost (Sales & Mktg / New Customers)</option>
                <option value="LTV_CAC">LTV to CAC Ratio (Customer LTV / CAC)</option>
                <option value="QUICK_RATIO">Quick Liquidity Ratio ((Cash + Receivables) / Liabilities)</option>
                <option value="EBITDA_MARGIN">EBITDA Margin % ((EBITDA / Revenue) * 100)</option>
              </select>

              <button
                type="submit"
                disabled={calculating}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold shadow-lg shadow-blue-600/20 transition-all flex items-center justify-center gap-2"
              >
                {calculating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Calculator className="w-4 h-4" />}
                Compute Metric Yield
              </button>
            </div>

            {/* Parameter Inputs */}
            <div className="space-y-3 bg-slate-950/60 p-4 rounded-2xl border border-slate-800 text-xs">
              <span className="text-slate-400 font-semibold block">Input Parameters</span>
              {Object.keys(calcParams).map((k) => (
                <div key={k}>
                  <label className="block text-[11px] text-slate-500 uppercase font-mono mb-1">{k.replace(/_/g, ' ')}</label>
                  <input
                    type="number"
                    value={calcParams[k]}
                    onChange={(e) => setCalcParams({ ...calcParams, [k]: Number(e.target.value) })}
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-xl text-white font-mono"
                  />
                </div>
              ))}
            </div>

            {/* Calculation Output Card */}
            <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 flex flex-col justify-between text-xs">
              <div>
                <span className="text-slate-400 font-semibold block mb-2">Simulated Yield Result</span>
                {calcResult ? (
                  <div className="space-y-2">
                    <p className="text-2xl font-bold text-emerald-400 font-mono">{calcResult.formatted_value}</p>
                    <p className="text-white font-semibold">{calcResult.name}</p>
                    <p className="text-[11px] text-slate-400 leading-relaxed">{calcResult.interpretation}</p>
                  </div>
                ) : (
                  <p className="text-slate-500 pt-6 text-center">Click 'Compute Metric Yield' to evaluate equation.</p>
                )}
              </div>
              {calcResult && (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 w-fit">
                  STATUS: {calcResult.status}
                </span>
              )}
            </div>
          </form>
        </div>

        {/* Target Edit Modal */}
        {editingKpi && (
          <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl space-y-6">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <h3 className="text-base font-bold text-white">Update Target: {editingKpi.name}</h3>
                <button onClick={() => setEditingKpi(null)} className="text-slate-400 hover:text-white font-bold">&times;</button>
              </div>

              <form onSubmit={handleUpdateTarget} className="space-y-4 text-xs">
                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Target Value ({editingKpi.unit})</label>
                  <input
                    type="number"
                    step="any"
                    required
                    value={targetInput}
                    onChange={(e) => setTargetInput(Number(e.target.value))}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500 font-mono"
                  />
                </div>

                <div>
                  <label className="block text-slate-400 font-semibold mb-1">Target Period Horizon</label>
                  <input
                    type="text"
                    required
                    value={periodInput}
                    onChange={(e) => setPeriodInput(e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                  <button
                    type="button"
                    onClick={() => setEditingKpi(null)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold shadow-lg shadow-blue-600/20"
                  >
                    Save Target
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
