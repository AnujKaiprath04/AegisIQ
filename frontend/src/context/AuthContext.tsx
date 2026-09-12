'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { User, TokenResponse, EnterpriseRole } from '@/types/auth';
import { apiClient } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  roles: string[];
  isAuthenticated: boolean;
  isLoading: boolean;
  hasRole: (allowedRoles: EnterpriseRole[] | string[]) => boolean;
  login: (credentials: { email: string; password: string }) => Promise<void>;
  register: (payload: {
    email: string;
    password: string;
    full_name: string;
    job_title?: string;
    department?: string;
    role_name?: string;
  }) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  // Load session from localStorage on initial mount
  useEffect(() => {
    const initAuth = async () => {
      try {
        const savedToken = localStorage.getItem('aegisiq_access_token');
        const savedUser = localStorage.getItem('aegisiq_user');

        if (savedToken && savedUser) {
          setUser(JSON.parse(savedUser));
          // Refresh profile in background to ensure sync
          try {
            const res = await apiClient.get<User>('/auth/me');
            setUser(res.data);
            localStorage.setItem('aegisiq_user', JSON.stringify(res.data));
          } catch (e) {
            console.warn('Silent token check failed or expired');
          }
        }
      } catch (err) {
        console.error('Failed to initialize auth state', err);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const roles = user?.roles ? user.roles.map((r) => r.name) : [];

  const hasRole = (allowedRoles: EnterpriseRole[] | string[]): boolean => {
    if (!user) return false;
    if (user.is_superuser) return true;
    return roles.some((role) => allowedRoles.includes(role as any));
  };

  const login = async (credentials: { email: string; password: string }) => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<TokenResponse>('/auth/login', credentials);
      const { access_token, refresh_token, user: loggedInUser } = res.data;

      localStorage.setItem('aegisiq_access_token', access_token);
      localStorage.setItem('aegisiq_refresh_token', refresh_token);
      localStorage.setItem('aegisiq_user', JSON.stringify(loggedInUser));

      setUser(loggedInUser);
      router.push('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (payload: {
    email: string;
    password: string;
    full_name: string;
    job_title?: string;
    department?: string;
    role_name?: string;
  }) => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<TokenResponse>('/auth/register', payload);
      const { access_token, refresh_token, user: registeredUser } = res.data;

      localStorage.setItem('aegisiq_access_token', access_token);
      localStorage.setItem('aegisiq_refresh_token', refresh_token);
      localStorage.setItem('aegisiq_user', JSON.stringify(registeredUser));

      setUser(registeredUser);
      router.push('/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiClient.post('/auth/logout');
    } catch (e) {
      console.warn('Logout notification error:', e);
    } finally {
      localStorage.removeItem('aegisiq_access_token');
      localStorage.removeItem('aegisiq_refresh_token');
      localStorage.removeItem('aegisiq_user');
      setUser(null);
      router.push('/login');
    }
  };

  const refreshProfile = async () => {
    try {
      const res = await apiClient.get<User>('/auth/me');
      setUser(res.data);
      localStorage.setItem('aegisiq_user', JSON.stringify(res.data));
    } catch (err) {
      console.error('Failed to refresh profile', err);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        roles,
        isAuthenticated: !!user,
        isLoading,
        hasRole,
        login,
        register,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
