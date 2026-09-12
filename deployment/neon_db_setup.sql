-- ==============================================================================
-- AegisIQ Enterprise Production Database Setup (Neon Serverless PostgreSQL)
-- Target: PostgreSQL 16+ with PgBouncer Connection Pooling
-- SSL: Mandatory (require / verify-full)
-- ==============================================================================

-- 1. Enable Required Enterprise Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- 2. Create Custom Production Schema
CREATE SCHEMA IF NOT EXISTS aegisiq_core;
SET search_path TO aegisiq_core, public;

-- 3. Production Connection Pooling & Role Hardening
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'aegisiq_app_user') THEN
      CREATE ROLE aegisiq_app_user WITH LOGIN PASSWORD 'SecureAppPassword2026!';
   END IF;
END
$$;

GRANT USAGE ON SCHEMA aegisiq_core TO aegisiq_app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA aegisiq_core TO aegisiq_app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA aegisiq_core TO aegisiq_app_user;

-- 4. Serverless Auto-Suspend and Timeout Optimizations
ALTER ROLE aegisiq_app_user SET statement_timeout = '30s';
ALTER ROLE aegisiq_app_user SET idle_in_transaction_session_timeout = '60s';

-- 5. Audit Trail Verification View
CREATE OR REPLACE VIEW aegisiq_core.v_system_health_audit AS
SELECT 
    current_database() AS database_name,
    current_user AS connected_user,
    version() AS pg_version,
    inet_server_addr() AS server_ip,
    inet_server_port() AS server_port,
    now() AS verified_at;
