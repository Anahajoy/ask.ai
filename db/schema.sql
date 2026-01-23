-- =============================================
-- Table: schema_version
-- =============================================
CREATE TABLE IF NOT EXISTS schema_version (
    version INT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =============================================
-- Table: skills
-- =============================================
CREATE TABLE IF NOT EXISTS skills (
    skill_id SERIAL PRIMARY KEY,
    skill_name TEXT NOT NULL UNIQUE,
    added_date TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_skill_name ON skills(skill_name);

-- =============================================
-- Table: users
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Table: user_resumes
-- =============================================
CREATE TABLE IF NOT EXISTS user_resumes (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    resume_data JSONB NOT NULL,
    input_method TEXT,
    source TEXT DEFAULT 'user',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================
-- Table: user_templates
-- =============================================
CREATE TABLE IF NOT EXISTS user_templates (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    template_key TEXT NOT NULL,
    template_name TEXT,
    html TEXT NOT NULL,
    css TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_user_template UNIQUE (email, template_key)
);

-- =============================================
-- Table: user_doc_templates
-- =============================================
CREATE TABLE IF NOT EXISTS user_doc_templates (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    template_key TEXT NOT NULL,
    template_name TEXT,
    doc_data BYTEA,
    doc_text TEXT,
    original_filename TEXT,
    uploaded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_user_doc_template UNIQUE (email, template_key)
);

-- =============================================
-- Table: user_ppt_templates
-- =============================================
CREATE TABLE IF NOT EXISTS user_ppt_templates (
    id BIGSERIAL PRIMARY KEY,
    email TEXT NOT NULL,
    template_key TEXT NOT NULL,
    template_name TEXT,
    ppt_data BYTEA NOT NULL,
    heading_shapes JSONB,
    basic_info_shapes JSONB,
    original_filename TEXT,
    uploaded_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT uq_user_ppt_template UNIQUE (email, template_key)
);
