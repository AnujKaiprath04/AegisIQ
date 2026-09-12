export type EnterpriseRole = 'Admin' | 'Executive' | 'Business Analyst' | 'Data Analyst' | 'Viewer';

export interface Role {
  id: number;
  name: EnterpriseRole;
  description: string;
  permissions?: string;
  created_at: string;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  job_title?: string;
  department?: string;
  phone_number?: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  roles: Role[];
  created_at: string;
  last_login_at?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface ActivityLog {
  id: number;
  user_id?: number;
  user_email?: string;
  action: string;
  ip_address?: string;
  user_agent?: string;
  details?: string;
  status: 'SUCCESS' | 'FAILED' | 'WARNING';
  created_at: string;
}
