# PostgreSQL CRUD Operations Optimization Guide

## Table Design Fundamentals

### 1. Proper Data Types

```sql
-- Bad: Using varchar for fixed-length data
CREATE TABLE users (
    phone_number varchar(50)
);

-- Good: Using appropriate data types
CREATE TABLE users (
    phone_number char(10)  -- For US phone numbers
);
```

### 2. Indexing Strategies

```sql
-- B-tree index for exact matches and ranges
CREATE INDEX idx_users_email ON users(email);

-- Partial index for filtered queries
CREATE INDEX idx_active_users ON users(last_login) 
WHERE status = 'active';

-- Multi-column index for compound queries
CREATE INDEX idx_users_location ON users(country, city, status);
```

## CREATE Operations Optimization

### 1. Bulk Inserts

```sql
-- Instead of multiple INSERTs
INSERT INTO users (name, email) 
SELECT unnest(ARRAY['John', 'Jane']),
       unnest(ARRAY['john@email.com', 'jane@email.com']);

-- Using COPY for large datasets
\COPY users(name, email) FROM 'users.csv' WITH (FORMAT csv);
```

### 2. Disable Indexes During Bulk Load

```sql
-- Temporarily disable indexes
ALTER INDEX idx_users_email SET (maintenance_work_mem = '1GB');
ALTER TABLE users SET UNLOGGED;

-- After bulk load
ALTER TABLE users SET LOGGED;
REINDEX TABLE users;
```

## READ Operations Optimization

### 1. Query Optimization

```sql
-- Bad: Using SELECT *
SELECT * FROM users WHERE status = 'active';

-- Good: Select only needed columns
SELECT id, name, email 
FROM users 
WHERE status = 'active';

-- Use EXPLAIN ANALYZE
EXPLAIN ANALYZE
SELECT * FROM users WHERE email LIKE '%@gmail.com';
```

### 2. Materialized Views

```sql
-- Create materialized view for expensive queries
CREATE MATERIALIZED VIEW user_stats AS
SELECT 
    country,
    COUNT(*) as user_count,
    AVG(age) as avg_age
FROM users
GROUP BY country;

-- Refresh view
REFRESH MATERIALIZED VIEW user_stats;
```

## UPDATE Operations Optimization

### 1. Batch Updates

```sql
-- Instead of multiple updates
UPDATE users
SET status = 
    CASE 
        WHEN last_login < NOW() - INTERVAL '30 days' THEN 'inactive'
        WHEN last_login < NOW() - INTERVAL '90 days' THEN 'dormant'
        ELSE status
    END
WHERE status = 'active';
```

### 2. Concurrent Updates

```sql
-- Use advisory locks for coordination
SELECT pg_advisory_xact_lock(id) FROM users WHERE id = 1;
UPDATE users SET status = 'active' WHERE id = 1;
```

## DELETE Operations Optimization

### 1. Batch Deletes

```sql
-- Delete in batches to avoid table bloat
DO $$
DECLARE
    batch_size INTEGER := 10000;
BEGIN
    WHILE EXISTS (SELECT 1 FROM users WHERE created_at < '2020-01-01') LOOP
        DELETE FROM users 
        WHERE id IN (
            SELECT id 
            FROM users 
            WHERE created_at < '2020-01-01'
            LIMIT batch_size
        );
        COMMIT;
    END LOOP;
END $$;
```

### 2. Soft Deletes

```sql
-- Add soft delete column
ALTER TABLE users ADD COLUMN deleted_at timestamp;

-- Instead of DELETE
UPDATE users SET deleted_at = NOW() WHERE id = 1;

-- Query excluding deleted
SELECT * FROM users WHERE deleted_at IS NULL;
```

## Performance Monitoring

### 1. Track Query Performance

```sql
-- Enable query tracking
ALTER SYSTEM SET track_activities = on;
ALTER SYSTEM SET track_counts = on;
ALTER SYSTEM SET track_io_timing = on;

-- Query statistics
SELECT query, calls, total_time, rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### 2. Index Usage Statistics

```sql
-- Monitor index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Maintenance Tasks

### 1. Regular VACUUM

```sql
-- Automated vacuum
ALTER TABLE users SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);

-- Manual vacuum
VACUUM (VERBOSE, ANALYZE) users;
```

### 2. Index Maintenance

```sql
-- Rebuild indexes
REINDEX TABLE users;

-- Remove unused indexes
SELECT * FROM pg_stat_user_indexes 
WHERE idx_scan = 0 AND idx_tup_read = 0;
```

## Best Practices Summary

1. Use appropriate data types
2. Create targeted indexes
3. Implement batch operations
4. Monitor query performance
5. Regular maintenance
6. Use EXPLAIN ANALYZE
7. Implement soft deletes
8. Use materialized views for complex queries
9. Regular VACUUM and ANALYZE
10. Monitor and remove unused indexes
