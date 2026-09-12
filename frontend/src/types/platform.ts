import { EnterpriseRole } from './auth';

export interface EnterpriseUser {
  id: number;
  email: string;
  full_name: string;
  job_title: string;
  department: string;
  phone_number?: string;
  is_active: boolean;
  is_superuser: boolean;
  roles: { id: number; name: EnterpriseRole; description?: string }[];
  created_at: string;
  updated_at?: string;
  last_login_at?: string;
}

export interface ColumnMetadata {
  name: string;
  data_type: 'numeric' | 'text' | 'datetime' | 'boolean';
  null_count: number;
  null_percentage: number;
  unique_count: number;
  sample_values: any[];
  min_value?: any;
  max_value?: any;
  mean_value?: number;
}

export interface DatasetSummary {
  id: number;
  name: string;
  description?: string;
  file_format: string;
  file_size_bytes: number;
  row_count: number;
  column_count: number;
  source_type: string;
  quality_score: number;
  created_at: string;
  updated_at?: string;
}

export interface DatasetDetail extends DatasetSummary {
  schema_json?: string;
  columns: ColumnMetadata[];
}

export interface DatasetPreview {
  id: number;
  name: string;
  columns: string[];
  rows: Record<string, any>[];
  total_rows: number;
  preview_limit: number;
}

export interface ETLRun {
  id: number;
  dataset_id: number;
  run_name: string;
  status: string;
  rows_before: number;
  rows_after: number;
  execution_duration_ms: number;
  log_output?: string;
  created_at: string;
}

export interface PillarScore {
  score: number;
  status: 'EXCELLENT' | 'GOOD' | 'WARNING' | 'CRITICAL';
  issues_found: number;
  details: string;
}

export interface DataQualityReport {
  dataset_id: number;
  dataset_name: string;
  overall_score: number;
  completeness: PillarScore;
  uniqueness: PillarScore;
  validity: PillarScore;
  consistency: PillarScore;
  columns_analyzed: number;
  rows_analyzed: number;
  generated_at: string;
  column_breakdown: Array<{
    name: string;
    data_type: string;
    null_pct: number;
    unique_count: number;
    status: string;
  }>;
}

export interface MetricCard {
  label: string;
  value: string;
  numeric_value: number;
  change_pct: number;
  trend: 'up' | 'down' | 'neutral';
  subtext: string;
}

export interface KPIMetric {
  id: number;
  code: string;
  name: string;
  category: 'FINANCIAL' | 'SALES' | 'OPERATIONS' | 'CUSTOMERS';
  description?: string;
  formula_expression?: string;
  unit: string;
  current_value: number;
  target_value: number;
  benchmark_value?: number;
  variance_pct: number;
  trend_direction: 'UP' | 'DOWN' | 'NEUTRAL';
  status: 'ON_TRACK' | 'WARNING' | 'CRITICAL';
  period: string;
  updated_at?: string;
}

export interface GeneratedReport {
  id: number;
  title: string;
  report_type: string;
  format: 'PDF' | 'EXCEL' | 'CSV';
  file_size_bytes: number;
  parameters_json?: string;
  created_at: string;
  download_url: string;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  user_email?: string;
  action: string;
  ip_address?: string;
  user_agent?: string;
  details?: string;
  status: string;
  created_at: string;
}
