-- ==============================================================================
-- DCA: Document & Contract Analysis - PostgreSQL Schema Initialization
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------------------------
-- 1. Users & Authentication
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'reviewer', -- 'admin', 'reviewer', 'stakeholder'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- ------------------------------------------------------------------------------
-- 2. Documents
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    storage_path TEXT NOT NULL,
    file_hash CHAR(64) NOT NULL, -- SHA-256 for integrity & deduplication
    mime_type VARCHAR(100) DEFAULT 'application/pdf',
    page_count INT DEFAULT 0,
    document_type VARCHAR(100) DEFAULT 'contract', -- 'nda', 'msa', 'sla', 'lease', 'invoice', etc.
    status VARCHAR(50) NOT NULL DEFAULT 'UPLOADED', 
    -- Status lifecycle: 'UPLOADED' -> 'PARSING' -> 'ANALYZING' -> 'NEEDS_REVIEW' -> 'APPROVED' -> 'FAILED'
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_file_hash ON documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);

-- ------------------------------------------------------------------------------
-- 3. Document Pages (Layout & Text storage per page)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INT NOT NULL,
    raw_text TEXT,
    layout_data JSONB DEFAULT '{}'::jsonb, -- Bounding boxes, word coordinates
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_document_page UNIQUE (document_id, page_number)
);

CREATE INDEX IF NOT EXISTS idx_document_pages_doc_id ON document_pages(document_id);

-- ------------------------------------------------------------------------------
-- 4. Extracted Entities & Clause Fields
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS document_extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    field_key VARCHAR(100) NOT NULL,              -- e.g. 'party_a', 'effective_date', 'indemnification_cap'
    field_label VARCHAR(150) NOT NULL,            -- e.g. 'First Party Name', 'Effective Date'
    field_value TEXT,                             -- The extracted value
    field_category VARCHAR(100) DEFAULT 'general',-- 'general', 'financial', 'compliance', 'legal', 'risk'
    data_type VARCHAR(50) DEFAULT 'string',       -- 'string', 'date', 'currency', 'boolean', 'list'
    confidence_score NUMERIC(5, 4) DEFAULT 1.0,   -- 0.0000 to 1.0000
    source_page INT,                              -- Reference page number in PDF
    source_quote TEXT,                            -- Verbatim quote from PDF for grounding
    source_bounding_box JSONB,                    -- { "x0": .., "y0": .., "x1": .., "y1": .. }
    is_corrected BOOLEAN DEFAULT FALSE,
    validation_status VARCHAR(50) DEFAULT 'VALID',-- 'VALID', 'WARNING', 'INVALID', 'NEEDS_VERIFICATION'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_extractions_doc_id ON document_extractions(document_id);
CREATE INDEX IF NOT EXISTS idx_extractions_field_key ON document_extractions(field_key);
CREATE INDEX IF NOT EXISTS idx_extractions_confidence ON document_extractions(confidence_score);

-- ------------------------------------------------------------------------------
-- 5. Human-In-The-Loop (HITL) Audit Trail
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS extraction_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    extraction_id UUID NOT NULL REFERENCES document_extractions(id) ON DELETE CASCADE,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    previous_value TEXT,
    new_value TEXT NOT NULL,
    reason TEXT,
    corrected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_extraction_id ON extraction_audit_logs(extraction_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_doc_id ON extraction_audit_logs(document_id);

-- ------------------------------------------------------------------------------
-- 6. Business Stakeholder Reports
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS generated_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) NOT NULL,            -- 'SUMMARY_CSV', 'RISK_EXECUTIVE_PDF'
    filters_applied JSONB DEFAULT '{}'::jsonb,
    storage_path TEXT NOT NULL,
    file_size_bytes BIGINT DEFAULT 0,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ------------------------------------------------------------------------------
-- Trigger: Auto-update updated_at timestamp
-- ------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_extractions_updated_at
    BEFORE UPDATE ON document_extractions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ------------------------------------------------------------------------------
-- Seed Default Admin User (Password: admin123 - bcrypt hash)
-- ------------------------------------------------------------------------------
INSERT INTO users (email, password_hash, full_name, role)
VALUES (
    'admin@dca.local',
    '$2a$12$e80yq5E76kYVevTj4k8ZgeN7KzP83F/0b5Xw2j9zUjQ8y5eY9gZ3K',
    'System Administrator',
    'admin'
) ON CONFLICT (email) DO NOTHING;

