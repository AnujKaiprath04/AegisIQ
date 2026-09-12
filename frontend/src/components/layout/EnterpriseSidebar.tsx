'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import {
  LayoutDashboard,
  Users,
  Database,
  Layers,
  Workflow,
  BarChart3,
  Sparkles,
  BookOpen,
  LineChart,
  SearchCode,
  ShieldAlert,
  BellRing,
  TrendingUp,
  FileSpreadsheet,
  ShieldCheck,
  Activity,
  Shield,
  LogOut,
  ChevronRight,
} from 'lucide-react';






import { cn } from '@/lib/utils';
import { EnterpriseRole } from '@/types/auth';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  roles?: EnterpriseRole[];
}

const NAV_ITEMS: NavItem[] = [
  {
    name: 'Executive Overview',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'User Management',
    href: '/users',
    icon: Users,
    roles: ['Admin'],
  },
  {
    name: 'Data Integration Hub',
    href: '/integration',
    icon: Database,
    roles: ['Admin', 'Data Analyst', 'Business Analyst'],
  },
  {
    name: 'Enterprise Datasets',
    href: '/datasets',
    icon: Layers,
    roles: ['Admin', 'Data Analyst', 'Business Analyst'],
  },
  {
    name: 'ETL Pipeline',
    href: '/etl',
    icon: Workflow,
    roles: ['Admin', 'Data Analyst'],
  },
  {
    name: 'BI Dashboards',
    href: '/bi',
    icon: BarChart3,
  },
  {
    name: 'AI Executive Assistant',
    href: '/assistant',
    icon: Sparkles,
  },
  {
    name: 'Knowledge Base (RAG)',
    href: '/knowledge',
    icon: BookOpen,
  },
  {
    name: 'Predictive Analytics',
    href: '/predictive',
    icon: LineChart,
    roles: ['Admin', 'Executive', 'Data Analyst', 'Business Analyst'],
  },
  {
    name: 'Explainable AI (XAI)',
    href: '/xai',
    icon: SearchCode,
    roles: ['Admin', 'Executive', 'Data Analyst', 'Business Analyst'],
  },
  {
    name: 'Cybersecurity SIEM',
    href: '/cybersecurity',
    icon: ShieldAlert,
    roles: ['Admin', 'Executive'],
  },
  {
    name: 'Notification Hub',
    href: '/notifications',
    icon: BellRing,
  },
  {
    name: 'KPI Engine',
    href: '/kpis',
    icon: TrendingUp,
    roles: ['Admin', 'Executive', 'Business Analyst'],
  },
  {
    name: 'Report Generator',
    href: '/reports',
    icon: FileSpreadsheet,
  },
  {
    name: 'Security & Audit Logs',
    href: '/audit',
    icon: ShieldCheck,
    roles: ['Admin'],
  },
  {
    name: 'System Telemetry & APM',
    href: '/telemetry',
    icon: Activity,
    roles: ['Admin'],
  },
];


export const EnterpriseSidebar: React.FC<{ isOpen: boolean; onClose: () => void }> = ({
  isOpen,
}) => {
  const pathname = usePathname();
  const { user, hasRole, logout } = useAuth();

  const primaryRole = user?.roles?.[0]?.name || 'Viewer';

  return (
    <aside
      className={cn(
        'fixed top-0 left-0 z-40 h-screen w-72 bg-slate-900 border-r border-slate-800 transition-transform duration-300 ease-in-out flex flex-col',
        !isOpen && '-translate-x-full lg:translate-x-0'
      )}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center gap-3 px-6 border-b border-slate-800 bg-slate-950/50">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
          <Shield className="w-5 h-5" />
        </div>
        <div>
          <span className="font-bold text-lg text-white tracking-tight flex items-center gap-1.5">
            Aegis<span className="text-blue-500">IQ</span>
            <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              v1.0
            </span>
          </span>
          <p className="text-[11px] text-slate-400 font-medium">Enterprise Intelligence</p>
        </div>
      </div>

      {/* Role Badge Chip */}
      <div className="px-5 py-4 border-b border-slate-800/80">
        <div className="p-3 bg-slate-800/60 rounded-xl border border-slate-700/50 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400 font-medium">Current Role</p>
            <p className="text-sm font-semibold text-blue-400">{primaryRole}</p>
          </div>
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Active
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto custom-scrollbar">
        <div className="px-3 pb-2 text-[11px] font-semibold tracking-wider text-slate-400 uppercase">
          Navigation
        </div>

        {NAV_ITEMS.map((item) => {
          const isAllowed = !item.roles || hasRole(item.roles);
          const isActive = pathname === item.href;

          if (!isAllowed) {
            return null;
          }

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'group flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                  : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
              )}
            >
              <div className="flex items-center gap-3">
                <item.icon
                  className={cn(
                    'w-4 h-4 transition-colors',
                    isActive ? 'text-white' : 'text-slate-400 group-hover:text-blue-400'
                  )}
                />
                <span>{item.name}</span>
              </div>
              {isActive && <ChevronRight className="w-3.5 h-3.5 opacity-80" />}
            </Link>
          );
        })}
      </nav>

      {/* Bottom User Profile Section */}
      <div className="p-4 border-t border-slate-800 bg-slate-950/40">
        <div className="flex items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-semibold text-white truncate">{user?.full_name || 'User'}</p>
              <p className="text-[11px] text-slate-400 truncate">{user?.email}</p>
            </div>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-slate-800 hover:bg-red-500/10 hover:text-red-400 text-slate-300 rounded-lg text-xs font-medium transition-colors border border-slate-700 hover:border-red-500/30"
        >
          <LogOut className="w-3.5 h-3.5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};
