-- ==============================================================================
-- AegisIQ Supabase S3-Compatible Object Storage Provisioning
-- Buckets: datasets, ml-artifacts, compliance-reports, system-backups
-- Security: Row Level Security (RLS) & Bucket Policies
-- ==============================================================================

-- 1. Create Enterprise Storage Buckets
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES 
  ('aegisiq-datasets', 'aegisiq-datasets', false, 104857600, ARRAY['text/csv', 'application/json', 'application/parquet']),
  ('aegisiq-ml-artifacts', 'aegisiq-ml-artifacts', false, 524288000, ARRAY['application/octet-stream', 'application/x-pickle', 'application/json']),
  ('aegisiq-reports', 'aegisiq-reports', false, 52428800, ARRAY['application/pdf', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']),
  ('aegisiq-backups', 'aegisiq-backups', false, 1073741824, ARRAY['application/gzip', 'application/zip', 'application/octet-stream'])
ON CONFLICT (id) DO UPDATE SET 
  file_size_limit = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- 2. Enable Row Level Security on Objects
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- 3. Access Policy: Authenticated Enterprise Users can read compliance reports
CREATE POLICY "Authenticated users can read reports"
ON storage.objects FOR SELECT
TO authenticated
USING (bucket_id = 'aegisiq-reports');

-- 4. Access Policy: Admins & Data Engineers can manage datasets and ML artifacts
CREATE POLICY "Admin full access to storage"
ON storage.objects FOR ALL
TO authenticated
USING (auth.jwt() ->> 'role' IN ('SUPER_ADMIN', 'DATA_ENGINEER', 'SECURITY_ADMIN'));
