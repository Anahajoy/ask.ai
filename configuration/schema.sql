IF NOT EXISTS (
    SELECT * FROM sys.objects
    WHERE object_id = OBJECT_ID(N'[dbo].[schema_version]')
      AND type = 'U'
)
BEGIN
    CREATE TABLE dbo.schema_version (
        version INT NOT NULL PRIMARY KEY,
        applied_at DATETIME2(7) NOT NULL DEFAULT SYSDATETIME()
    )
END

-- =============================================
-- Table: skills
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[skills]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[skills](
        [skill_id] [int] IDENTITY(1,1) NOT NULL,
        [skill_name] [nvarchar](100) NOT NULL,
        [added_date] [datetime2](7) NULL,
        PRIMARY KEY CLUSTERED ([skill_id] ASC),
        UNIQUE NONCLUSTERED ([skill_name] ASC)
    )

    ALTER TABLE [dbo].[skills] ADD DEFAULT (getdate()) FOR [added_date]
    
    CREATE INDEX idx_skill_name ON skills(skill_name)
    
    PRINT '✅ Skills table created successfully'
END
ELSE
    PRINT '⚠️ Skills table already exists'

-- =============================================
-- Table: users
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[users]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[users](
        [id] [bigint] IDENTITY(1,1) NOT NULL,
        [email] [nvarchar](255) NOT NULL,
        [password_hash] [nvarchar](255) NOT NULL,
        [name] [nvarchar](255) NOT NULL,
        [created_at] [datetime2](7) NULL,
        PRIMARY KEY CLUSTERED ([id] ASC),
        UNIQUE NONCLUSTERED ([email] ASC)
    )

    ALTER TABLE [dbo].[users] ADD DEFAULT (sysdatetime()) FOR [created_at]
    
    PRINT '✅ Users table created successfully'
END
ELSE
    PRINT '⚠️ Users table already exists'

-- =============================================
-- Table: user_resumes
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_resumes]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[user_resumes](
        [id] [bigint] IDENTITY(1,1) NOT NULL,
        [email] [nvarchar](255) NOT NULL,
        [resume_data] [nvarchar](max) NOT NULL,
        [input_method] [nvarchar](50) NULL,
        [source] [nvarchar](50) NULL,
        [created_at] [datetime2](7) NULL,
        [updated_at] [datetime2](7) NULL,
        PRIMARY KEY CLUSTERED ([id] ASC),
        UNIQUE NONCLUSTERED ([email] ASC)
    )

    ALTER TABLE [dbo].[user_resumes] ADD DEFAULT ('user') FOR [source]
    ALTER TABLE [dbo].[user_resumes] ADD DEFAULT (sysdatetime()) FOR [created_at]
    ALTER TABLE [dbo].[user_resumes] ADD DEFAULT (sysdatetime()) FOR [updated_at]
    
    ALTER TABLE [dbo].[user_resumes] WITH CHECK 
    ADD CONSTRAINT [chk_resume_json] CHECK ((isjson([resume_data])=(1)))
    
    ALTER TABLE [dbo].[user_resumes] CHECK CONSTRAINT [chk_resume_json]
    
    PRINT '✅ User_resumes table created successfully'
END
ELSE
    PRINT '⚠️ User_resumes table already exists'

-- =============================================
-- Table: user_templates
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_templates]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[user_templates](
        [id] [bigint] IDENTITY(1,1) NOT NULL,
        [email] [nvarchar](255) NOT NULL,
        [template_key] [nvarchar](255) NOT NULL,
        [template_name] [nvarchar](255) NULL,
        [html] [nvarchar](max) NOT NULL,
        [css] [nvarchar](max) NULL,
        [created_at] [datetime2](7) NULL,
        [updated_at] [datetime2](7) NULL,
        PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [uq_user_template] UNIQUE NONCLUSTERED ([email] ASC, [template_key] ASC)
    )

    ALTER TABLE [dbo].[user_templates] ADD DEFAULT (sysdatetime()) FOR [created_at]
    ALTER TABLE [dbo].[user_templates] ADD DEFAULT (sysdatetime()) FOR [updated_at]
    
    PRINT '✅ User_templates table created successfully'
END
ELSE
    PRINT '⚠️ User_templates table already exists'

-- =============================================
-- Table: user_doc_templates
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_doc_templates]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[user_doc_templates](
        [id] [bigint] IDENTITY(1,1) NOT NULL,
        [email] [nvarchar](255) NOT NULL,
        [template_key] [nvarchar](255) NOT NULL,
        [template_name] [nvarchar](255) NULL,
        [doc_data] [varbinary](max) NULL,
        [doc_text] [nvarchar](max) NULL,
        [original_filename] [nvarchar](255) NULL,
        [uploaded_at] [datetime2](7) NULL,
        [created_at] [datetime2](7) NULL,
        [updated_at] [datetime2](7) NULL,
        PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [uq_user_doc_template] UNIQUE NONCLUSTERED ([email] ASC, [template_key] ASC)
    )

    ALTER TABLE [dbo].[user_doc_templates] ADD DEFAULT (sysdatetime()) FOR [created_at]
    ALTER TABLE [dbo].[user_doc_templates] ADD DEFAULT (sysdatetime()) FOR [updated_at]
    
    PRINT '✅ User_doc_templates table created successfully'
END
ELSE
    PRINT '⚠️ User_doc_templates table already exists'

-- =============================================
-- Table: user_ppt_templates
-- =============================================
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[user_ppt_templates]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[user_ppt_templates](
        [id] [bigint] IDENTITY(1,1) NOT NULL,
        [email] [nvarchar](255) NOT NULL,
        [template_key] [nvarchar](255) NOT NULL,
        [template_name] [nvarchar](255) NULL,
        [ppt_data] [varbinary](max) NOT NULL,
        [heading_shapes] [nvarchar](max) NULL,
        [basic_info_shapes] [nvarchar](max) NULL,
        [original_filename] [nvarchar](255) NULL,
        [uploaded_at] [datetime2](7) NULL,
        [created_at] [datetime2](7) NULL,
        [updated_at] [datetime2](7) NULL,
        PRIMARY KEY CLUSTERED ([id] ASC),
        CONSTRAINT [uq_user_ppt_template] UNIQUE NONCLUSTERED ([email] ASC, [template_key] ASC)
    )

    ALTER TABLE [dbo].[user_ppt_templates] ADD DEFAULT (sysdatetime()) FOR [created_at]
    ALTER TABLE [dbo].[user_ppt_templates] ADD DEFAULT (sysdatetime()) FOR [updated_at]
    
    ALTER TABLE [dbo].[user_ppt_templates] WITH CHECK 
    ADD CONSTRAINT [chk_heading_shapes_json] 
    CHECK (([heading_shapes] IS NULL OR isjson([heading_shapes])=(1)))
    
    ALTER TABLE [dbo].[user_ppt_templates] CHECK CONSTRAINT [chk_heading_shapes_json]
    
    ALTER TABLE [dbo].[user_ppt_templates] WITH CHECK 
    ADD CONSTRAINT [chk_basic_info_shapes_json] 
    CHECK (([basic_info_shapes] IS NULL OR isjson([basic_info_shapes])=(1)))
    
    ALTER TABLE [dbo].[user_ppt_templates] CHECK CONSTRAINT [chk_basic_info_shapes_json]
    
    PRINT '✅ User_ppt_templates table created successfully'
END
ELSE
    PRINT '⚠️ User_ppt_templates table already exists'

PRINT ''
PRINT '=========================================='
PRINT 'Database schema initialization complete!'
PRINT '=========================================='