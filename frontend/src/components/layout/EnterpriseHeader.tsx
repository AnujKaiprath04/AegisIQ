'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Menu, Search, Bell, Activity } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface EnterpriseHeaderProps {
  onToggleSidebar: () => void;
}

export const EnterpriseHeader: React.FC<EnterpriseHeaderProps> = ({ onToggleSidebar }) => {
  const [systemOnline, setSystemOnline] = useState<boolean>(true);
  const [unreadCount, setUnreadCount] = useState<number>(0);

  useEffect(() => {
    const checkTelemetry = async () => {
      try {
        const [hRes, uRes] = await Promise.all([
          apiClient.get('/system/health'),
          apiClient.get('/notifications/unread-count'),
        ]);
        setSystemOnline(hRes.data.status === 'online');
        setUnreadCount(uRes.data.unread_count || 0);
      } catch {
        setSystemOnline(false);
      }
    };
    checkTelemetry();
    const interval = setInterval(checkTelemetry, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="sticky top-0 z-30 h-16 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg lg:hidden"
          aria-label="Toggle Sidebar"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search Bar */}
        <div className="relative hidden md:block w-72 lg:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search datasets, reports, KPIs, users..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-slate-800/80 border border-slate-700/80 rounded-lg text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
          />
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* System Health Indicator */}
        <div className="flex items-center gap-2 px-3 py-1 bg-slate-800/60 rounded-full border border-slate-700/50 text-xs">
          <span
            className={`w-2 h-2 rounded-full ${
              systemOnline ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'
            }`}
          />
          <Activity className="w-3.5 h-3.5 text-slate-400" />
          <span className="text-slate-300 font-medium text-[11px] hidden sm:inline">
            {systemOnline ? 'AegisIQ Core Online' : 'Core Offline'}
          </span>
        </div>

        {/* Notification Bell */}
        <Link
          href="/notifications"
          className="relative p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          title="Notification & Alerting Hub"
        >
          <Bell className="w-4 h-4" />
          {unreadCount > 0 && (
            <span className="absolute -top-0.5 -right-0.5 min-w-4 h-4 px-1 bg-rose-500 text-white rounded-full text-[9px] font-bold flex items-center justify-center font-mono animate-pulse">
              {unreadCount}
            </span>
          )}
        </Link>
      </div>
    </header>
  );
};

