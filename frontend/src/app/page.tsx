'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { Shield, ArrowRight, BarChart3, Database, Lock, Activity, Sparkles, CheckCircle2 } from 'lucide-react';
import Link from 'next/link';

export default function LandingPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isLoading, isAuthenticated, router]);

  return (
    <div className="min-h-screen bg-slate-950 text-white selection:bg-blue-500 selection:text-white relative overflow-hidden flex flex-col justify-between">
      {/* Dynamic Background Elements */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-b from-blue-600/15 via-indigo-600/5 to-transparent blur-[140px] pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-[600px] h-[400px] bg-indigo-500/10 blur-[150px] pointer-events-none" />

      {/* Top Navigation */}
      <nav className="relative z-20 max-w-7xl w-full mx-auto px-6 h-20 flex items-center justify-between border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
            <Shield className="w-5 h-5" />
          </div>
          <span className="font-bold text-xl tracking-tight">
            Aegis<span className="text-blue-500">IQ</span>
          </span>
        </div>

        <div className="flex items-center gap-4">
          <Link
            href="/login"
            className="text-xs font-semibold text-slate-300 hover:text-white px-4 py-2 rounded-xl transition-colors"
          >
            Sign In
          </Link>
          <Link
            href="/register"
            className="text-xs font-semibold text-white bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-xl transition-all shadow-md shadow-blue-600/20"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 max-w-5xl mx-auto px-6 py-20 text-center flex-1 flex flex-col items-center justify-center">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-6 shadow-sm">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Enterprise Decision Intelligence & AI Platform</span>
        </div>


        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-tight sm:leading-tight mb-6">
          Enterprise Intelligence.{' '}
          <span className="bg-gradient-to-r from-blue-400 via-indigo-300 to-blue-500 bg-clip-text text-transparent">
            Secure, Scalable & Driven by Data.
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-400 max-w-2xl mx-auto mb-10 leading-relaxed">
          Unify enterprise datasets, automate ETL pipelines, compute financial KPIs, and deliver executive-grade business intelligence with zero-trust role-based security.
        </p>

        <div className="flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto mb-16">
          <Link
            href="/login"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-sm font-semibold rounded-2xl shadow-xl shadow-blue-600/25 transition-all"
          >
            Launch Platform Console
            <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/register"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-slate-900/80 hover:bg-slate-800 border border-slate-700 text-slate-300 text-sm font-semibold rounded-2xl transition-all"
          >
            Create Enterprise Account
          </Link>
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-left w-full max-w-4xl">
          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center mb-4">
              <Lock className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white mb-1">5-Tier Enterprise RBAC</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Granular permission gating for Admin, Executive, Business Analyst, Data Analyst, and Viewer roles.
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm">
            <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-4">
              <Database className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white mb-1">Automated ETL & Quality</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Ingest CSV, Excel, and JSON datasets with automatic cleaning, schema validation, and outlier detection.
            </p>
          </div>

          <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 backdrop-blur-sm">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4">
              <BarChart3 className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white mb-1">Executive BI & Reports</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Interactive multi-dimensional charts, dynamic formula KPI computation, and PDF/Excel report export.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-slate-800/80 py-6 text-center text-xs text-slate-500">
        AegisIQ Enterprise Decision Intelligence Platform &copy; 2026. Built with FastAPI, Next.js & PostgreSQL.
      </footer>
    </div>
  );
}
