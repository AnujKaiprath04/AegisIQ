'use client';

import React, { useState, useEffect } from 'react';
import { EnterpriseShell } from '@/components/layout/EnterpriseShell';
import { useAuth } from '@/context/AuthContext';
import { apiClient } from '@/lib/api';
import {
  BarChart3,
  TrendingUp,
  DollarSign,
  Users,
  Package,
  ArrowUpRight,
  ArrowDownRight,
  Sparkles,
  Calendar,
  Layers,
  RefreshCw,
  PieChart as PieChartIcon,
  Activity,
  Globe,
  Award,
} from 'lucide-react';

export default function BIPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'overview' | 'finance' | 'sales' | 'customers' | 'inventory'>('overview');
  const [dateRange, setDateRange] = useState('YTD');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchDomainData = async (domain: string, range: string) => {
    setLoading(true);
    try {
      let endpoint = `/bi/${domain}`;
      if (domain === 'overview') endpoint += `?date_range=${range}`;
      const res = await apiClient.get(endpoint);
      setData(res.data);
    } catch (err) {
      console.error(`Error loading BI data for ${domain}:`, err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDomainData(activeTab, dateRange);
  }, [activeTab, dateRange]);

  return (
    <EnterpriseShell>
      <div className="space-y-6">
        {/* Banner */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold mb-2">
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Executive BI & Analytics</span>
            </div>

            <h1 className="text-2xl font-bold text-white tracking-tight">Business Intelligence Suite</h1>
            <p className="text-xs text-slate-400 mt-1">
              Multi-dimensional corporate intelligence, financial health, sales pipeline, cohort retention, and supply chain telemetry.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="bg-transparent text-white focus:outline-none cursor-pointer"
              >
                <option value="MTD" className="bg-slate-900">Month-to-Date (MTD)</option>
                <option value="QTD" className="bg-slate-900">Quarter-to-Date (QTD)</option>
                <option value="YTD" className="bg-slate-900">Year-to-Date (YTD)</option>
                <option value="1Y" className="bg-slate-900">Trailing 12 Months</option>
              </select>
            </div>

            <button
              onClick={() => fetchDomainData(activeTab, dateRange)}
              disabled={loading}
              className="p-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl border border-slate-700 transition-colors"
              title="Refresh Analytics"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Domain Navigation Tabs */}
        <div className="flex flex-wrap items-center gap-2 bg-slate-950/60 p-1.5 rounded-2xl border border-slate-800/80">
          {[
            { id: 'overview', label: 'Executive Overview', icon: Activity },
            { id: 'finance', label: 'Financial Health', icon: DollarSign },
            { id: 'sales', label: 'Sales & Revenue', icon: TrendingUp },
            { id: 'customers', label: 'Customers & Churn', icon: Users },
            { id: 'inventory', label: 'Supply Chain & Stock', icon: Package },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                activeTab === t.id
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <t.icon className="w-3.5 h-3.5" />
              {t.label}
            </button>
          ))}
        </div>

        {/* Content Area */}
        {loading ? (
          <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-16 text-center text-slate-500">
            <RefreshCw className="w-8 h-8 animate-spin mx-auto mb-3 text-blue-500" />
            Computing multi-dimensional BI aggregations...
          </div>
        ) : !data ? (
          <div className="bg-slate-900/40 border border-slate-800 rounded-3xl p-12 text-center text-slate-500">
            No analytics records available.
          </div>
        ) : (
          <div className="space-y-6">
            {/* Metric KPI Cards */}
            {data.summary_metrics || data.kpis ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {(data.summary_metrics || data.kpis).map((m: any, idx: number) => (
                  <div key={idx} className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-slate-400">{m.label}</span>
                      <span
                        className={`inline-flex items-center text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          m.trend === 'up'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}
                      >
                        {m.trend === 'up' ? <ArrowUpRight className="w-3 h-3 mr-0.5" /> : <ArrowDownRight className="w-3 h-3 mr-0.5" />}
                        {m.change_pct > 0 ? `+${m.change_pct}%` : `${m.change_pct}%`}
                      </span>
                    </div>
                    <p className="text-2xl font-bold text-white font-mono">{m.value}</p>
                    <p className="text-[11px] text-slate-400">{m.subtext}</p>
                  </div>
                ))}
              </div>
            ) : null}

            {/* Overview Domain View */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Revenue Trend Visual Bar Chart */}
                <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-bold text-white flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-blue-400" />
                      Quarterly Revenue vs Target Performance ($ Millions)
                    </h3>
                    <span className="text-[11px] text-slate-400 font-mono">18.4% YoY Growth</span>
                  </div>

                  <div className="h-64 flex items-end justify-between gap-4 pt-8 pb-4 px-2">
                    {data.revenue_trend?.map((item: any) => {
                      const maxVal = 10.0;
                      const revHeight = (item.revenue / maxVal) * 100;
                      const targetHeight = (item.target / maxVal) * 100;
                      return (
                        <div key={item.date} className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                          <div className="w-full flex items-end justify-center gap-1.5 h-full">
                            {/* Revenue Bar */}
                            <div
                              className="w-full max-w-[28px] bg-gradient-to-t from-blue-600 to-indigo-500 rounded-t-lg transition-all group-hover:brightness-125 relative"
                              style={{ height: `${revHeight}%` }}
                            >
                              <div className="opacity-0 group-hover:opacity-100 absolute -top-8 left-1/2 -translate-x-1/2 bg-slate-950 border border-slate-700 px-2 py-0.5 rounded text-[10px] text-white font-mono whitespace-nowrap shadow-lg pointer-events-none transition-opacity">
                                Rev: ${item.revenue}M
                              </div>
                            </div>
                            {/* Target Bar */}
                            <div
                              className="w-full max-w-[12px] bg-slate-800 border border-slate-700 rounded-t-md transition-all relative"
                              style={{ height: `${targetHeight}%` }}
                            />
                          </div>
                          <span className="text-[10px] font-mono text-slate-400 truncate w-full text-center">
                            {item.date}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Category Revenue Distribution */}
                <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <PieChartIcon className="w-4 h-4 text-purple-400" />
                    Revenue by Business Line
                  </h3>

                  <div className="space-y-3 pt-2">
                    {data.category_distribution?.map((c: any) => (
                      <div key={c.category} className="space-y-1.5">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-300 font-medium">{c.category}</span>
                          <span className="text-slate-400 font-mono">${c.value}M ({c.percentage}%)</span>
                        </div>
                        <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden">
                          <div className="h-2 rounded-full" style={{ width: `${c.percentage}%`, backgroundColor: c.color }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Regional Territory Breakdown */}
                <div className="lg:col-span-3 bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl">
                  <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                    <Globe className="w-4 h-4 text-emerald-400" />
                    Global Enterprise Territory Performance
                  </h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                    {data.regional_breakdown?.map((r: any) => (
                      <div key={r.region} className="bg-slate-950/60 border border-slate-800 rounded-2xl p-4 space-y-2">
                        <p className="text-xs font-bold text-white">{r.region}</p>
                        <p className="text-xl font-bold text-blue-400 font-mono">${r.sales}M</p>
                        <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono pt-2 border-t border-slate-800">
                          <span className="text-emerald-400">+{r.growth_pct}% YoY</span>
                          <span>{r.units_sold} Accounts</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Finance View */}
            {activeTab === 'finance' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h3 className="text-sm font-bold text-white">Monthly Cash Inflow vs Outflow ($ Millions)</h3>
                  <div className="space-y-3 pt-2">
                    {data.cash_flow_trend?.map((cf: any) => (
                      <div key={cf.month} className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                        <span className="font-bold text-white font-mono">{cf.month} 2026</span>
                        <div className="flex items-center gap-4 font-mono text-[11px]">
                          <span className="text-emerald-400">In: ${cf.inflow}M</span>
                          <span className="text-red-400">Out: ${cf.outflow}M</span>
                          <span className="text-blue-400 font-bold">Net: +${cf.net}M</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h3 className="text-sm font-bold text-white">Operating Expense Allocations</h3>
                  <div className="space-y-3 pt-2">
                    {data.expense_breakdown?.map((e: any) => (
                      <div key={e.category} className="space-y-1.5">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-slate-300 font-medium">{e.category}</span>
                          <span className="text-slate-400 font-mono">${e.value}M ({e.percentage}%)</span>
                        </div>
                        <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden">
                          <div className="h-2 rounded-full" style={{ width: `${e.percentage}%`, backgroundColor: e.color }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Sales View */}
            {activeTab === 'sales' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Funnel */}
                <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h3 className="text-sm font-bold text-white">Enterprise Deal Pipeline Funnel</h3>
                  <div className="space-y-2 pt-2">
                    {data.pipeline_funnel?.map((f: any, idx: number) => (
                      <div key={f.stage} className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                        <span className="text-slate-300 font-medium">{idx + 1}. {f.stage}</span>
                        <div className="flex items-center gap-3 font-mono text-[11px]">
                          <span className="text-slate-400">{f.count} Deals</span>
                          <span className="text-blue-400 font-bold">${f.value}M Value</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Rep Leaderboard */}
                <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Award className="w-4 h-4 text-amber-400" />
                    Top Sales Performance Leaderboard
                  </h3>
                  <div className="space-y-2 pt-2">
                    {data.sales_rep_leaderboard?.map((rep: any) => (
                      <div key={rep.name} className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                        <div>
                          <p className="font-bold text-white">{rep.name}</p>
                          <p className="text-[10px] text-slate-400">{rep.region} &bull; {rep.deals_closed} closed</p>
                        </div>
                        <div className="text-right font-mono">
                          <p className="text-emerald-400 font-bold">{rep.quota_attainment}</p>
                          <p className="text-[10px] text-slate-400">{rep.revenue}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Customers View */}
            {activeTab === 'customers' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h3 className="text-sm font-bold text-white">Cohort Retention Matrix (%)</h3>
                  <div className="overflow-x-auto border border-slate-800 rounded-2xl">
                    <table className="w-full text-left text-xs font-mono">
                      <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                        <tr>
                          <th className="py-2.5 px-3">Cohort</th>
                          <th className="py-2.5 px-3">Month 0</th>
                          <th className="py-2.5 px-3">Month 3</th>
                          <th className="py-2.5 px-3">Month 6</th>
                          <th className="py-2.5 px-3">Month 9</th>
                          <th className="py-2.5 px-3">Month 12</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-800">
                        {data.retention_cohorts?.map((c: any) => (
                          <tr key={c.cohort} className="hover:bg-slate-800/40">
                            <td className="py-2.5 px-3 font-sans font-semibold text-white">{c.cohort}</td>
                            <td className="py-2.5 px-3 text-emerald-400">{c.m0}%</td>
                            <td className="py-2.5 px-3 text-emerald-400">{c.m3}%</td>
                            <td className="py-2.5 px-3 text-emerald-400">{c.m6}%</td>
                            <td className="py-2.5 px-3 text-emerald-400">{c.m9}%</td>
                            <td className="py-2.5 px-3 text-emerald-400">{c.m12}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h3 className="text-sm font-bold text-white">Accounts Churn Risk Stratification</h3>
                  <div className="space-y-3 pt-2">
                    {data.churn_risk_distribution?.map((cr: any) => (
                      <div key={cr.tier} className="p-4 bg-slate-950/60 rounded-2xl border border-slate-800 space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-white">{cr.tier}</span>
                          <span className="text-slate-400 font-mono">{cr.percentage}% of Accounts</span>
                        </div>
                        <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-1">
                          <span>{cr.accounts} Client Organizations</span>
                          <span className="text-blue-400 font-bold">{cr.arr} ARR</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Inventory View */}
            {activeTab === 'inventory' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h3 className="text-sm font-bold text-white">Hardware Stock & Reorder Levels</h3>
                  <div className="space-y-2 pt-2">
                    {data.stock_levels?.map((s: any) => (
                      <div key={s.sku} className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                        <div>
                          <p className="font-bold text-white">{s.name}</p>
                          <p className="text-[10px] text-slate-400 font-mono">SKU: {s.sku}</p>
                        </div>
                        <div className="text-right font-mono">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              s.status === 'HEALTHY'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            }`}
                          >
                            {s.stock} / {s.min_required} (min)
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-xl space-y-4">
                  <h3 className="text-sm font-bold text-white">Vendor Fulfillment Lead Times</h3>
                  <div className="space-y-2 pt-2">
                    {data.supplier_lead_times?.map((sup: any) => (
                      <div key={sup.supplier} className="p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 flex items-center justify-between text-xs">
                        <div>
                          <p className="font-bold text-white">{sup.supplier}</p>
                          <p className="text-[10px] text-emerald-400 font-mono">On-Time: {sup.on_time_rate}</p>
                        </div>
                        <div className="text-right font-mono">
                          <p className="text-slate-200 font-bold">{sup.lead_time_days} Days Lead</p>
                          <p className="text-[10px] text-blue-400">Rating: {sup.rating}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </EnterpriseShell>
  );
}
