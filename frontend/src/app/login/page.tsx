'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { Shield, Lock, Mail, AlertCircle, Loader2, KeyRound, Sparkles, CheckCircle2 } from 'lucide-react';

const DEMO_ACCOUNTS = [
  { role: 'Admin', email: 'admin@aegisiq.com', pass: 'Admin@12345', desc: 'Full System Control & User Management' },
  { role: 'Executive', email: 'executive@aegisiq.com', pass: 'Exec@12345', desc: 'C-Level Strategic Summaries & KPIs' },
  { role: 'Business Analyst', email: 'business.analyst@aegisiq.com', pass: 'Analyst@12345', desc: 'BI Dashboards & Report Generation' },
  { role: 'Data Analyst', email: 'data.analyst@aegisiq.com', pass: 'Data@12345', desc: 'ETL Pipelines & Dataset Ingestion' },
  { role: 'Viewer', email: 'viewer@aegisiq.com', pass: 'Viewer@12345', desc: 'Read-Only BI Reports & Metrics' },
];

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login({ email, password });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed. Please verify credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  const fillDemo = (demoEmail: string, demoPass: string) => {
    setEmail(demoEmail);
    setPassword(demoPass);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background Glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-blue-600/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-10 right-10 w-[400px] h-[300px] bg-indigo-600/10 blur-[100px] rounded-full pointer-events-none" />

      {/* Header / Logo */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center z-10">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 text-white shadow-xl shadow-blue-500/20 mb-4">
          <Shield className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Aegis<span className="text-blue-500">IQ</span>
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Enterprise Decision Intelligence Platform
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-xl z-10 px-4 sm:px-0">
        <div className="bg-slate-900/90 backdrop-blur-xl border border-slate-800 rounded-3xl p-8 shadow-2xl space-y-6">
          <div className="border-b border-slate-800 pb-4">
            <h2 className="text-lg font-semibold text-white">Enterprise Sign In</h2>
            <p className="text-xs text-slate-400">Authenticate with your corporate credentials or choose a demo role</p>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="p-3.5 bg-red-950/50 border border-red-800/80 rounded-xl flex items-start gap-3 text-red-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Corporate Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@enterprise.com"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-800/70 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-xs font-medium text-slate-300">
                  Password
                </label>
                <Link
                  href="/forgot-password"
                  className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
                >
                  Forgot Password?
                </Link>
              </div>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-800/70 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-sm font-semibold transition-all shadow-lg shadow-blue-600/25 flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Authenticating...
                </>
              ) : (
                <>
                  <KeyRound className="w-4 h-4" />
                  Sign In to Platform
                </>
              )}
            </button>
          </form>

          {/* Quick 1-Click Demo Accounts Selector */}
          <div className="pt-4 border-t border-slate-800/80">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                1-Click Demo Enterprise Roles
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {DEMO_ACCOUNTS.map((demo) => (
                <button
                  key={demo.role}
                  type="button"
                  onClick={() => fillDemo(demo.email, demo.pass)}
                  className={`text-left p-2.5 rounded-xl border text-xs transition-all flex flex-col justify-between ${
                    email === demo.email
                      ? 'bg-blue-600/20 border-blue-500/60 text-white'
                      : 'bg-slate-800/40 border-slate-700/60 hover:bg-slate-800 hover:border-slate-600 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1">
                    <span className="font-semibold text-blue-400">{demo.role}</span>
                    {email === demo.email && <CheckCircle2 className="w-3.5 h-3.5 text-blue-400" />}
                  </div>
                  <span className="text-[11px] text-slate-400 line-clamp-1">{demo.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="text-center pt-2 text-xs text-slate-400">
            Don't have an enterprise account?{' '}
            <Link href="/register" className="text-blue-400 hover:text-blue-300 font-semibold underline underline-offset-4">
              Register New Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
