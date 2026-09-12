'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { EnterpriseRole } from '@/types/auth';
import { ShieldAlert, Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: (EnterpriseRole | string)[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles,
}) => {
  const { user, isAuthenticated, isLoading, hasRole } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-slate-200">
        <Loader2 className="w-10 h-10 animate-spin text-blue-500 mb-4" />
        <p className="text-sm font-medium tracking-wide text-slate-400">
          Authenticating AegisIQ Session...
        </p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect via useEffect
  }

  // Check role authorization
  if (allowedRoles && allowedRoles.length > 0 && !hasRole(allowedRoles)) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-white dark:bg-slate-800 border border-red-200 dark:border-red-900/50 rounded-2xl p-8 shadow-xl text-center">
          <div className="w-16 h-16 bg-red-100 dark:bg-red-950/60 text-red-600 dark:text-red-400 rounded-full flex items-center justify-center mx-auto mb-5">
            <ShieldAlert className="w-8 h-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
            Access Restricted
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 leading-relaxed">
            Your current enterprise role (
            <span className="font-semibold text-slate-800 dark:text-slate-200">
              {user?.roles?.map((r) => r.name).join(', ') || 'No Role'}
            </span>
            ) does not have authorization to view this module.
          </p>
          <div className="bg-slate-50 dark:bg-slate-900/60 rounded-lg p-3 text-xs text-slate-500 dark:text-slate-400 mb-6 border border-slate-200 dark:border-slate-800 text-left">
            <span className="font-semibold block mb-1">Required Permissions:</span>
            One of: {allowedRoles.join(', ')}
          </div>
          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return <>{children}</>;
};
