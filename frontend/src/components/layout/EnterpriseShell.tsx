'use client';

import React, { useState } from 'react';
import { EnterpriseSidebar } from './EnterpriseSidebar';
import { EnterpriseHeader } from './EnterpriseHeader';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { EnterpriseRole } from '@/types/auth';

interface EnterpriseShellProps {
  children: React.ReactNode;
  allowedRoles?: (EnterpriseRole | string)[];
}

export const EnterpriseShell: React.FC<EnterpriseShellProps> = ({
  children,
  allowedRoles,
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ProtectedRoute allowedRoles={allowedRoles}>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col antialiased">
        {/* Sidebar */}
        <EnterpriseSidebar
          isOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />

        {/* Backdrop for mobile */}
        {sidebarOpen && (
          <div
            className="fixed inset-0 z-30 bg-black/60 backdrop-blur-sm lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* Main Content Area */}
        <div className="lg:pl-72 flex flex-col flex-1 min-w-0">
          <EnterpriseHeader onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
          <main className="flex-1 p-6 sm:p-8 max-w-7xl w-full mx-auto">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
};
