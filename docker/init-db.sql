-- Initialize database for Job Agent System
-- This script runs when the PostgreSQL container starts

-- Create database if not exists (handled by POSTGRES_DB)
-- Create extensions needed for the application
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database user with permissions (handled by environment variables)
-- GRANT ALL PRIVILEGES ON DATABASE job_agent_db TO job_agent_user;

-- Create schema for the application
CREATE SCHEMA IF NOT EXISTS app;

-- Set search path
ALTER DATABASE job_agent_db SET search_path TO app, public;

-- Create table for storing migrations info
CREATE TABLE IF NOT EXISTS app.alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Insert initial alembic version
INSERT INTO app.alembic_version (version_num) VALUES ('0001_initial')
ON CONFLICT (version_num) DO NOTHING;

-- Create initial admin user (optional)
-- This can be used for initial setup
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'admin') THEN
        CREATE ROLE admin LOGIN PASSWORD 'admin_password';
        GRANT ALL PRIVILEGES ON DATABASE job_agent_db TO admin;
        GRANT ALL ON SCHEMA app TO admin;
        GRANT ALL ON ALL TABLES IN SCHEMA app TO admin;
        GRANT ALL ON ALL SEQUENCES IN SCHEMA app TO admin;
    END IF;
END $$;

-- Create read-only role for analytics
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics') THEN
        CREATE ROLE analytics LOGIN PASSWORD 'analytics_password';
        GRANT CONNECT ON DATABASE job_agent_db TO analytics;
        GRANT USAGE ON SCHEMA app TO analytics;
        GRANT SELECT ON ALL TABLES IN SCHEMA app TO analytics;
        GRANT SELECT ON ALL SEQUENCES IN SCHEMA app TO analytics;
    END IF;
END $$;

-- Set up row-level security (RLS)
ALTER DATABASE job_agent_db SET row_security = on;

-- Create function for updating updated_at timestamp
CREATE OR REPLACE FUNCTION app.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create function for generating UUIDs
CREATE OR REPLACE FUNCTION app.generate_uuid()
RETURNS UUID AS $$
BEGIN
    RETURN uuid_generate_v4();
END;
$$ LANGUAGE plpgsql;

-- Create function for soft delete
CREATE OR REPLACE FUNCTION app.soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    NEW.deleted_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permissions to application user
GRANT EXECUTE ON FUNCTION app.update_updated_at_column() TO job_agent_user;
GRANT EXECUTE ON FUNCTION app.generate_uuid() TO job_agent_user;
GRANT EXECUTE ON FUNCTION app.soft_delete() TO job_agent_user;

-- Create indexes for common queries
-- These will be created by Alembic migrations, but we can add some basic ones here

-- Index for user email
CREATE INDEX IF NOT EXISTS idx_users_email ON app.users(email);

-- Index for job listings
CREATE INDEX IF NOT EXISTS idx_job_listings_active ON app.job_listings(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_job_listings_posted_at ON app.job_listings(posted_at DESC);

-- Index for CVs
CREATE INDEX IF NOT EXISTS idx_cvs_user_id ON app.cvs(user_id);
CREATE INDEX IF NOT EXISTS idx_cvs_active ON app.cvs(is_active) WHERE is_active = true;

-- Index for job matches
CREATE INDEX IF NOT EXISTS idx_job_matches_user_id ON app.job_matches(user_id);
CREATE INDEX IF NOT EXISTS idx_job_matches_score ON app.job_matches(match_score DESC);

-- Create full-text search indexes
CREATE INDEX IF NOT EXISTS idx_job_listings_search ON app.job_listings USING gin(
    to_tsvector('spanish', title || ' ' || description || ' ' || COALESCE(requirements, ''))
);

-- Create table for storing application settings
CREATE TABLE IF NOT EXISTS app.settings (
    id UUID PRIMARY KEY DEFAULT app.generate_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default settings
INSERT INTO app.settings (key, value, description) VALUES
    ('app_name', 'Job Agent System', 'Application name'),
    ('app_version', '1.0.0', 'Application version'),
    ('max_file_size', '10485760', 'Maximum file size in bytes'),
    ('allowed_extensions', 'pdf,doc,docx', 'Allowed file extensions'),
    ('job_search_limit', '50', 'Maximum job search results'),
    ('recommendation_limit', '10', 'Maximum skill recommendations')
ON CONFLICT (key) DO UPDATE SET
    value = EXCLUDED.value,
    description = EXCLUDED.description,
    updated_at = NOW();

-- Create table for audit logging
CREATE TABLE IF NOT EXISTS app.audit_logs (
    id UUID PRIMARY KEY DEFAULT app.generate_uuid(),
    user_id UUID,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON app.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON app.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON app.audit_logs(created_at);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA app TO job_agent_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA app TO job_agent_user;

-- Vacuum analyze for better performance
ANALYZE;

-- Output completion message
DO $$
BEGIN
    RAISE NOTICE 'Database initialization completed successfully!';
    RAISE NOTICE 'Database: job_agent_db';
    RAISE NOTICE 'User: job_agent_user';
    RAISE NOTICE 'Schema: app';
END $$;