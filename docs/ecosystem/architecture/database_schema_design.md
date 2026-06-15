# Database Schema Design

Comprehensive database schema design for the CTC Research and Structa Cloud ecosystem, including data models, relationships, and optimization strategies.

## 🎯 Database Design Principles

### Core Design Principles
- **Normalization**: Reduce data redundancy and improve data integrity
- **Performance**: Optimize for read and write performance
- **Scalability**: Design for horizontal and vertical scaling
- **Security**: Implement proper access controls and encryption
- **Maintainability**: Clear naming conventions and documentation
- **Flexibility**: Support for future feature additions

### Naming Conventions
- **Tables**: Plural, snake_case (e.g., `users`, `blog_posts`)
- **Columns**: Singular, snake_case (e.g., `first_name`, `created_at`)
- **Primary Keys**: `id` (auto-incrementing integer)
- **Foreign Keys**: `{table_name}_id` (e.g., `user_id`, `post_id`)
- **Indexes**: `idx_{table_name}_{column_name}` (e.g., `idx_users_email`)
- **Constraints**: `{table_name}_{column_name}_{constraint}` (e.g., `users_email_unique`)

## 🏗️ Core Schema Design

### User Management Schema

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    CONSTRAINT users_email_unique UNIQUE (email),
    INDEX idx_users_email (email),
    INDEX idx_users_is_active (is_active),
    INDEX idx_users_date_joined (date_joined)
);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### User Profiles Table
```sql
CREATE TABLE profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    bio TEXT,
    avatar_url VARCHAR(500),
    website VARCHAR(255),
    location VARCHAR(255),
    company VARCHAR(255),
    job_title VARCHAR(255),
    social_links JSONB DEFAULT '{}',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_profiles_user_id (user_id),
    INDEX idx_profiles_location (location),
    INDEX idx_profiles_company (company)
);

CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Blog Management Schema

#### Blog Posts Table
```sql
CREATE TABLE blog_posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    excerpt TEXT,
    content TEXT NOT NULL,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    -- status values: draft, review, published, archived

    featured_image_url VARCHAR(500),
    meta_title VARCHAR(255),
    meta_description TEXT,
    meta_keywords TEXT[],

    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,

    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    CONSTRAINT blog_posts_slug_unique UNIQUE (slug),
    INDEX idx_blog_posts_slug (slug),
    INDEX idx_blog_posts_author_id (author_id),
    INDEX idx_blog_posts_status (status),
    INDEX idx_blog_posts_published_at (published_at),
    INDEX idx_blog_posts_created_at (created_at),
    INDEX idx_blog_posts_view_count (view_count),

    -- Full-text search index
    INDEX idx_blog_posts_search
        ON blog_posts USING gin(
            to_tsvector('english', title || ' ' || excerpt || ' ' || content)
        )
);

CREATE TRIGGER update_blog_posts_updated_at
    BEFORE UPDATE ON blog_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### Blog Tags Table
```sql
CREATE TABLE blog_tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    color VARCHAR(7),  -- Hex color code
    post_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    CONSTRAINT blog_tags_slug_unique UNIQUE (slug),
    INDEX idx_blog_tags_slug (slug),
    INDEX idx_blog_tags_name (name),
    INDEX idx_blog_tags_post_count (post_count)
);

CREATE TRIGGER update_blog_tags_updated_at
    BEFORE UPDATE ON blog_tags
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

#### Blog Post Tags (Many-to-Many)
```sql
CREATE TABLE blog_post_tags (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES blog_tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    CONSTRAINT blog_post_tags_unique UNIQUE (post_id, tag_id),
    INDEX idx_blog_post_tags_post_id (post_id),
    INDEX idx_blog_post_tags_tag_id (tag_id)
);

-- Function to update tag post_count
CREATE OR REPLACE FUNCTION update_tag_post_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE blog_tags
        SET post_count = post_count + 1
        WHERE id = NEW.tag_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE blog_tags
        SET post_count = post_count - 1
        WHERE id = OLD.tag_id;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_tag_post_count_insert
    AFTER INSERT ON blog_post_tags
    FOR EACH ROW
    EXECUTE FUNCTION update_tag_post_count();

CREATE TRIGGER update_tag_post_count_delete
    AFTER DELETE ON blog_post_tags
    FOR EACH ROW
    EXECUTE FUNCTION update_tag_post_count();
```

### Comment System Schema

#### Comments Table
```sql
CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL REFERENCES blog_posts(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES comments(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    is_spam BOOLEAN DEFAULT FALSE,
    like_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,

    ip_address INET,
    user_agent TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_comments_post_id (post_id),
    INDEX idx_comments_author_id (author_id),
    INDEX idx_comments_parent_id (parent_id),
    INDEX idx_comments_is_approved (is_approved),
    INDEX idx_comments_created_at (created_at),
    INDEX idx_comments_post_created (post_id, created_at),

    -- Full-text search for comment content
    INDEX idx_comments_search
        ON comments USING gin(to_tsvector('english', content))
);

CREATE TRIGGER update_comments_updated_at
    BEFORE UPDATE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to update comment reply_count
CREATE OR REPLACE FUNCTION update_comment_reply_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.parent_id IS NOT NULL THEN
        UPDATE comments
        SET reply_count = reply_count + 1
        WHERE id = NEW.parent_id;
    ELSIF TG_OP = 'DELETE' AND OLD.parent_id IS NOT NULL THEN
        UPDATE comments
        SET reply_count = reply_count - 1
        WHERE id = OLD.parent_id;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_comment_reply_count_insert
    AFTER INSERT ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_comment_reply_count();

CREATE TRIGGER update_comment_reply_count_delete
    AFTER DELETE ON comments
    FOR EACH ROW
    EXECUTE FUNCTION update_comment_reply_count();
```

### Media Management Schema

#### Media Files Table
```sql
CREATE TABLE media_files (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    width INTEGER,
    height INTEGER,
    duration INTEGER,  -- For videos, in seconds
    thumbnail_path VARCHAR(500),

    title VARCHAR(255),
    description TEXT,
    alt_text VARCHAR(255),
    caption TEXT,

    uploader_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    upload_ip INET,

    is_public BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,

    view_count INTEGER DEFAULT 0,
    download_count INTEGER DEFAULT 0,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_media_files_file_path (file_path),
    INDEX idx_media_files_uploader_id (uploader_id),
    INDEX idx_media_files_is_public (is_public),
    INDEX idx_media_files_created_at (created_at),
    INDEX idx_media_files_mime_type (mime_type),

    -- Full-text search for media metadata
    INDEX idx_media_files_search
        ON media_files USING gin(
            to_tsvector('english', title || ' ' || description || ' ' || alt_text)
        )
);

CREATE TRIGGER update_media_files_updated_at
    BEFORE UPDATE ON media_files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Notification System Schema

#### Notifications Table
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL,
    -- Types: comment, like, follow, mention, system

    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',

    is_read BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,

    related_object_type VARCHAR(50),
    related_object_id INTEGER,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE,

    -- Indexes
    INDEX idx_notifications_user_id (user_id),
    INDEX idx_notifications_is_read (is_read),
    INDEX idx_notifications_created_at (created_at),
    INDEX idx_notifications_user_read (user_id, is_read),
    INDEX idx_notifications_type (notification_type),
    INDEX idx_notifications_related (related_object_type, related_object_id)
);

-- Function to mark notifications as read
CREATE OR REPLACE FUNCTION mark_notification_read()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_read = TRUE AND OLD.is_read = FALSE THEN
        NEW.read_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER mark_notification_read_trigger
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION mark_notification_read();
```

## 🔄 Data Relationships

### Entity Relationship Diagram
```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│    Users    │◄─────┤   Profiles  │      │  Media      │
└──────┬──────┘      └─────────────┘      │   Files     │
       │                                   └──────┬──────┘
       │                                          │
       │      ┌─────────────┐      ┌─────────────▼──────┐
       └──────┤ Blog Posts  │◄─────┤ Blog Post Tags    │
              └──────┬──────┘      └─────────────┬──────┘
                     │                           │
                     │      ┌─────────────┐      │
                     └──────┤  Comments   │      │
                            └──────┬──────┘      │
                                   │             │
                            ┌──────▼──────┐      │
                            │ Blog Tags   │◄─────┘
                            └─────────────┘
```

### Relationship Types
1. **One-to-One**: Users ↔ Profiles
2. **One-to-Many**: Users → Blog Posts, Blog Posts → Comments
3. **Many-to-Many**: Blog Posts ↔ Blog Tags (via blog_post_tags)
4. **Self-Referential**: Comments → Comments (parent-child relationship)

## 📊 Database Performance Optimization

### Indexing Strategy

#### Primary Indexes
```sql
-- Composite indexes for common query patterns
CREATE INDEX idx_blog_posts_status_published
    ON blog_posts(status, published_at DESC);

CREATE INDEX idx_comments_post_approved
    ON comments(post_id, is_approved, created_at DESC);

CREATE INDEX idx_notifications_user_unread
    ON notifications(user_id, is_read, created_at DESC);

-- Partial indexes for filtered queries
CREATE INDEX idx_blog_posts_published
    ON blog_posts(published_at DESC)
    WHERE status = 'published';

CREATE INDEX idx_comments_approved
    ON comments(created_at DESC)
    WHERE is_approved = TRUE;
```

#### Full-Text Search Indexes
```sql
-- Enable full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Trigram indexes for fuzzy search
CREATE INDEX idx_users_name_trgm
    ON users USING gin(first_name gin_trgm_ops, last_name gin_trgm_ops);

CREATE INDEX idx_blog_posts_title_trgm
    ON blog_posts USING gin(title gin_trgm_ops);

-- Combined search index
CREATE INDEX idx_blog_posts_full_search
    ON blog_posts USING gin(
        to_tsvector('english', title),
        to_tsvector('english', excerpt),
        to_tsvector('english', content)
    );
```

### Partitioning Strategy

#### Time-Based Partitioning
```sql
-- Partition comments table by month
CREATE TABLE comments_y2024m01 PARTITION OF comments
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE comments_y2024m02 PARTITION OF comments
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Partition blog_posts by year
CREATE TABLE blog_posts_y2024 PARTITION OF blog_posts
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

### Materialized Views

#### Popular Content View
```sql
CREATE MATERIALIZED VIEW popular_posts AS
SELECT
    bp.id,
    bp.title,
    bp.slug,
    bp.author_id,
    u.first_name || ' ' || u.last_name AS author_name,
    bp.view_count,
    bp.like_count,
    bp.comment_count,
    bp.published_at,
    ROUND(
        (bp.view_count * 0.3 + bp.like_count * 0.4 + bp.comment_count * 0.3)
        / EXTRACT(EPOCH FROM (NOW() - bp.published_at)) / 3600 * 100, 2
    ) AS popularity_score
FROM blog_posts bp
JOIN users u ON bp.author_id = u.id
WHERE bp.status = 'published'
    AND bp.published_at IS NOT NULL
    AND bp.published_at > NOW() - INTERVAL '30 days'
ORDER BY popularity_score DESC
LIMIT 100;

-- Refresh materialized view daily
CREATE OR REPLACE FUNCTION refresh_popular_posts()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY popular_posts;
END;
$$ LANGUAGE plpgsql;
```

## 🔒 Database Security

### Row-Level Security
```sql
-- Enable RLS
ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY blog_posts_select_policy ON blog_posts
    FOR SELECT USING (
        status = 'published'
        OR author_id = current_user_id()
        OR current_user_is_staff()
    );

CREATE POLICY blog_posts_insert_policy ON blog_posts
    FOR INSERT WITH CHECK (author_id = current_user_id());

CREATE POLICY blog_posts_update_policy ON blog_posts
    FOR UPDATE USING (
        author_id = current_user_id()
        OR current_user_is_staff()
    );

CREATE POLICY blog_posts_delete_policy ON blog_posts
    FOR DELETE USING (
        author_id = current_user_id()
        OR current_user_is_staff()
    );
```

### Data Encryption
```sql
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt sensitive data
CREATE OR REPLACE FUNCTION encrypt_sensitive_data(data TEXT, key TEXT)
RETURNS BYTEA AS $$
BEGIN
    RETURN pgp_sym_encrypt(data, key);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION decrypt_sensitive_data(data BYTEA, key TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN pgp_sym_decrypt(data, key);
END;
$$ LANGUAGE plpgsql;
```

## 📈 Database Monitoring

### Performance Monitoring Queries
```sql
-- Slow queries
SELECT
    query,
    calls,
    total_time,
    mean_time,
    rows,
    100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 20;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Table statistics
SELECT
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

### Maintenance Queries
```sql
-- Vacuum analyze
VACUUM ANALYZE blog_posts;

-- Reindex
REINDEX INDEX CONCURRENTLY idx_blog_posts_search;

-- Update statistics
ANALYZE blog_posts;

-- Check for bloat
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename) - pg_relation_size(schemaname || '.' || tablename)) AS index_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;
```

## 🔄 Database Migration Strategy

### Schema Migration Patterns
```python
# Django migration example
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='view_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddIndex(
            model_name='blogpost',
            index=models.Index(fields=['view_count'], name='idx_view_count'),
        ),
    ]
```

### Zero-Downtime Migrations
```sql
-- Add column with default value
ALTER TABLE blog_posts ADD COLUMN new_column INTEGER DEFAULT 0;

-- Backfill data
UPDATE blog_posts SET new_column = calculated_value;

-- Remove default after backfill
ALTER TABLE blog_posts ALTER COLUMN new_column DROP DEFAULT;

-- Add NOT NULL constraint
ALTER TABLE blog_posts ALTER COLUMN new_column SET NOT NULL;
```

## 📊 Database Sizing Guidelines

### Table Size Estimates
```sql
-- Estimate table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename) - pg_relation_size(schemaname || '.' || tablename)) AS index_size,
    n_live_tup AS row_count
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC;
```

### Growth Projections
- **Users**: 10,000/year
- **Blog Posts**: 1,000/year
- **Comments**: 10,000/year
- **Media Files**: 5,000/year (avg 1MB each = 5GB/year)

## 🚀 Database Scaling Strategies

### Read Replicas
```sql
-- Configure read replica
-- In postgresql.conf on replica
hot_standby = on

-- In recovery.conf on replica
standby_mode = 'on'
primary_conninfo = 'host=primary_host port=5432 user=replication password=secret'
```

### Connection Pooling
```sql
-- Configure PgBouncer
[databases]
ctc_research = host=localhost port=5432 dbname=ctc_research

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

### Sharding Strategy
```sql
-- Shard by user_id range
CREATE TABLE users_shard_1 (
    CHECK (user_id >= 1 AND user_id < 10000)
) INHERITS (users);

CREATE TABLE users_shard_2 (
    CHECK (user_id >= 10000 AND user_id < 20000)
) INHERITS (users);
```

## 📚 Related Documentation

- [System Architecture Overview](system_architecture_overview.md) - Overall system design
- [Technology Stack](technology_stack.md) - Technology choices
- [API Reference](../api/api_reference.md) - API endpoints
- [Deployment Guide](../deployment/docker_setup.md) - Deployment procedures
- [Performance Optimization](../performance/optimization_guide.md) - Performance tuning

---

*This database schema design provides a robust foundation for the CTC Research and Structa Cloud ecosystem. The design balances normalization with performance considerations and includes comprehensive security and monitoring features.*

*Last updated: 2024-12-19 | Version: 2.0.0*
