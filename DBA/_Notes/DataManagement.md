# Data Management

## Table of Contents

- [Data Management](#data-management)
  - [Table of Contents](#table-of-contents)
  - [1. Database Management](#1-database-management)
    - [1.1 PostgreSQL Specific](#11-postgresql-specific)
      - [Postgres MVCC (Multi-Version Concurrency Control)](#postgres-mvcc-multi-version-concurrency-control)
      - [Postgres Indexing Best Practices](#postgres-indexing-best-practices)
      - [Postgres VACUUM](#postgres-vacuum)
      - [Postgres Race Conditions](#postgres-race-conditions)
    - [1.2 Database Performance](#12-database-performance)
      - [Methods for Finding Postgres Queries' Historical Latency Distribution](#methods-for-finding-postgres-queries-historical-latency-distribution)
      - [ACID vs Two-Phase Commit](#acid-vs-two-phase-commit)
    - [1.3 SQL Optimization for Analytics](#13-sql-optimization-for-analytics)
      - [Window Functions](#window-functions)
      - [CTEs vs Subqueries](#ctes-vs-subqueries)
      - [Query Performance Patterns](#query-performance-patterns)
      - [Set-Based Thinking](#set-based-thinking)
  - [2. Data Quality & Modeling](#2-data-quality--modeling)
    - [2.1 Schema Management & Evolution](#21-schema-management--evolution)
      - [Schema Evolution](#schema-evolution)
      - [Backward Compatible ETL](#backward-compatible-etl)
      - [Blue-Green Deployment in Schema Evolution](#blue-green-deployment-in-schema-evolution)
      - [Schema Contract Validation](#schema-contract-validation)
      - [Data Contracts](#data-contracts)
      - [API Versioning for Data](#api-versioning-for-data)
    - [2.2 Data Quality & Validation](#22-data-quality--validation)
      - [Data Quality Frameworks: Deequ vs Great Expectations vs Custom](#data-quality-frameworks-deequ-vs-great-expectations-vs-custom)
      - [Data Drift Detection](#data-drift-detection)
      - [Soft DELETE and Alternative Strategies](#soft-delete-and-alternative-strategies)
      - [Data Testing Strategies](#data-testing-strategies)
      - [Data Governance & Lineage](#data-governance--lineage)
    - [2.3 Data Modeling](#23-data-modeling)
      - [Slow Changing Dimension Type 2](#slow-changing-dimension-type-2)
      - [All SCD Types Overview](#all-scd-types-overview)
      - [Snapshot Tables](#snapshot-tables)
      - [Deduplication Strategies](#deduplication-strategies)

## 1. Database Management

### 1.1 PostgreSQL Specific

#### Postgres MVCC (Multi-Version Concurrency Control)
**Definition**: Concurrency mechanism where transactions read from snapshots, enabling concurrent reads/writes without traditional locking.

**External Resources**:
- https://www.postgresql.org/docs/current/mvcc.html
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://www.youtube.com/watch?v=Tup3k4Pjf9w

#### Postgres Indexing Best Practices
**Definition**: Strategies for creating efficient indexes (B-tree, Hash, GIST, GIN) and query optimization through index usage.

**Index Types and When to Use**:

| Index Type | Best For | Example Use Case |
| --- | --- | --- |
| B-tree | Equality, range queries, sorting | `WHERE id = 5`, `WHERE date > '2024-01-01'`, `ORDER BY` |
| Hash | Equality only (rarely used) | `WHERE code = 'ABC'` (B-tree usually better) |
| GIN | Full-text search, arrays, JSONB | `WHERE tags @> '{urgent}'`, `WHERE doc @@ 'search'` |
| GiST | Geometric, range types, full-text | `WHERE location <-> point`, `WHERE range && '[1,10]'` |
| BRIN | Very large tables, naturally ordered | Time-series data, append-only logs |
| SP-GiST | Non-balanced structures, phone numbers | Radix trees, quad-trees |

---

**Index Creation Best Practices**:

```sql
-- Create indexes CONCURRENTLY to avoid blocking writes (production-safe)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Partial index: only index rows matching condition (smaller, faster)
CREATE INDEX idx_orders_pending ON orders(created_at)
WHERE status = 'pending';

-- Covering index: include columns to enable index-only scans
CREATE INDEX idx_orders_user ON orders(user_id)
INCLUDE (total_amount, status);

-- Expression index: index computed values
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- Multi-column index: order matters! Most selective column first
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);

-- GIN index for JSONB queries
CREATE INDEX idx_events_data ON events USING GIN(data jsonb_path_ops);

-- BRIN for time-series (tiny index, huge tables)
CREATE INDEX idx_logs_timestamp ON logs USING BRIN(timestamp);
```

---

**Query Analysis Guidelines**:

```sql
-- Always use EXPLAIN ANALYZE for real execution stats
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = 123;

-- Key metrics to watch:
-- - Seq Scan on large tables = missing index
-- - High "Rows Removed by Filter" = index not selective enough
-- - "Buffers: shared read" = data not cached, disk I/O
-- - "Index Cond" vs "Filter" = what index handles vs post-filtering
```

**EXPLAIN Output Patterns**:

| Pattern | Problem | Solution |
| --- | --- | --- |
| Seq Scan on large table | No usable index | Add appropriate index |
| Index Scan + Filter | Index partially used | Create more specific index |
| Bitmap Heap Scan | Multiple index conditions | Consider composite index |
| Sort + Limit (no index) | Missing index for ORDER BY | Add index matching sort order |
| Nested Loop (high rows) | Inefficient join | Add index on join column |

---

**Column Order in Composite Indexes**:

```sql
-- Index on (a, b, c) can satisfy:
-- ✅ WHERE a = ?
-- ✅ WHERE a = ? AND b = ?
-- ✅ WHERE a = ? AND b = ? AND c = ?
-- ✅ WHERE a = ? ORDER BY b
-- ❌ WHERE b = ?  (must have leading column)
-- ❌ WHERE a = ? AND c = ?  (gap in columns, c not used)
-- ⚠️ WHERE a = ? AND b > ? AND c = ?  (c not used after range on b)

-- Rule: Equality columns first, then range/sort columns
CREATE INDEX idx_good ON orders(user_id, status, created_at DESC);
-- Supports: WHERE user_id = ? AND status = ? ORDER BY created_at DESC
```

---

**Index Maintenance**:

```sql
-- Check index usage (drop unused indexes)
SELECT
    schemaname, tablename, indexname,
    idx_scan,        -- Number of index scans
    idx_tup_read,    -- Tuples read via index
    idx_tup_fetch,   -- Tuples fetched via index
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0   -- Unused indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- Check for duplicate/redundant indexes
SELECT
    pg_size_pretty(sum(pg_relation_size(idx))::bigint) as size,
    (array_agg(idx))[1] as idx1, (array_agg(idx))[2] as idx2
FROM (
    SELECT indexrelid::regclass as idx,
           (indrelid::text || E'\n' || indclass::text || E'\n' ||
            indkey::text || E'\n' || coalesce(indexprs::text,'') ||
            E'\n' || coalesce(indpred::text,'')) as key
    FROM pg_index
) sub
GROUP BY key HAVING count(*) > 1;

-- Rebuild bloated indexes (CONCURRENTLY for production)
REINDEX INDEX CONCURRENTLY idx_orders_user;

-- Check index bloat estimate
SELECT
    schemaname, tablename, indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    round(100 * idx_scan / greatest(seq_scan + idx_scan, 1), 2) as idx_scan_pct
FROM pg_stat_user_indexes
JOIN pg_index USING (indexrelid)
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

**Anti-Patterns to Avoid**:

1. **Over-indexing**: Each index slows writes and consumes storage
   ```sql
   -- Bad: Index on every column
   CREATE INDEX idx_a ON t(a);
   CREATE INDEX idx_b ON t(b);
   CREATE INDEX idx_c ON t(c);

   -- Better: One composite index if queries use multiple columns
   CREATE INDEX idx_abc ON t(a, b, c);
   ```

2. **Indexing low-cardinality columns alone**:
   ```sql
   -- Bad: Boolean/status columns have few distinct values
   CREATE INDEX idx_active ON users(is_active);  -- Only 2 values!

   -- Better: Partial index or composite
   CREATE INDEX idx_active_users ON users(created_at) WHERE is_active = true;
   ```

3. **Wrong column order in composite index**:
   ```sql
   -- Bad: Range column first prevents using equality column
   CREATE INDEX idx_bad ON orders(created_at, user_id);
   -- Query: WHERE user_id = ? AND created_at > ? -- Poor performance

   -- Good: Equality column first
   CREATE INDEX idx_good ON orders(user_id, created_at);
   ```

4. **Not using INCLUDE for covering indexes**:
   ```sql
   -- Query: SELECT email, name FROM users WHERE user_id = ?

   -- Bad: Requires table lookup after index scan
   CREATE INDEX idx_users_id ON users(user_id);

   -- Good: Index-only scan, no table access
   CREATE INDEX idx_users_id ON users(user_id) INCLUDE (email, name);
   ```

5. **Ignoring expression indexes**:
   ```sql
   -- Query uses LOWER() but index is on raw column
   SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

   -- Index on email won't be used! Need expression index:
   CREATE INDEX idx_users_lower_email ON users(LOWER(email));
   ```

---

**Special Index Strategies**:

**JSONB Indexing**:
```sql
-- GIN for flexible key/value queries
CREATE INDEX idx_data_gin ON events USING GIN(data);
-- Supports: data ? 'key', data @> '{"key": "value"}'

-- jsonb_path_ops for containment only (smaller, faster)
CREATE INDEX idx_data_path ON events USING GIN(data jsonb_path_ops);
-- Supports: data @> '{"key": "value"}'  (not ? operator)

-- Expression index for specific key
CREATE INDEX idx_data_type ON events((data->>'type'));
-- Supports: WHERE data->>'type' = 'click'
```

**Array Indexing**:
```sql
CREATE INDEX idx_tags ON articles USING GIN(tags);
-- Supports: tags @> ARRAY['postgres'], tags && ARRAY['db', 'sql']
```

**Full-Text Search**:
```sql
-- Create tsvector column or expression index
CREATE INDEX idx_fts ON articles USING GIN(to_tsvector('english', title || ' ' || body));
-- Query: WHERE to_tsvector('english', title || ' ' || body) @@ to_tsquery('postgres & index')
```

---

**Index Size vs Performance Trade-offs**:

| Scenario | Recommendation |
| --- | --- |
| Read-heavy, write-light | More indexes acceptable |
| Write-heavy (OLTP) | Minimal indexes, composite over multiple single |
| Large tables (>10GB) | Consider BRIN for naturally ordered data |
| Frequent range queries | B-tree with proper column order |
| Complex JSONB queries | GIN with jsonb_path_ops |
| Infrequent queries | May not justify index maintenance cost |

**Index Size Estimation**:
```sql
-- Estimate index size before creation
SELECT pg_size_pretty(
    pg_relation_size('tablename') * 0.3  -- Rough: 20-40% of table size
) as estimated_index_size;

-- Check actual sizes
SELECT
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE tablename = 'orders'
ORDER BY pg_relation_size(indexrelid) DESC;
```

**External Resources**:

- <https://www.postgresql.org/docs/current/indexes.html>
- <https://use-the-index-luke.com/>
- <https://www.pgmustard.com/blog/hypothetical-indexes-postgresql>
- <https://www.cybertec-postgresql.com/en/postgresql-indexing-index-scan-vs-bitmap-scan-vs-sequential-scan/>
- <https://pganalyze.com/blog/postgres-index-bloat>

#### Postgres VACUUM
**Definition**: Maintenance operation removing dead tuples and reclaiming storage space, essential for performance maintenance in PostgreSQL.

**External Resources**:
- https://www.postgresql.org/docs/current/sql-vacuum.html
- https://wiki.postgresql.org/wiki/Bloat
- https://www.youtube.com/watch?v=WfcZVVFhXds

#### Postgres Race Conditions
**Definition**: Concurrent access issues where transaction isolation levels are insufficient, leading to dirty reads, non-repeatable reads, or phantom reads.

**External Resources**:
- https://www.postgresql.org/docs/current/transaction-iso.html
- https://en.wikipedia.org/wiki/Race_condition
- https://www.postgresql.org/docs/current/explicit-locking.html

### 1.2 Database Performance

#### Methods for Finding Postgres Queries' Historical Latency Distribution
**Definition**: Techniques using pg_stat_statements, query logs, and monitoring tools to analyze query execution history and identify performance issues.

**Key Analysis Techniques**:
- **pg_stat_statements Extension**: Query the `pg_stat_statements` table to retrieve aggregated statistics (mean, max, min, stddev execution time) for each normalized query since last reset
- **Query Execution Time Sorting**: Order results by `mean_exec_time` or `max_exec_time` to identify slowest queries; calculate `total_time = calls × mean_exec_time` to find high-impact queries
- **Percentile Calculation**: Use `PERCENT_RANK()` window function on `mean_exec_time` to identify queries at p50, p95, p99 latency thresholds
- **Standard Deviation Analysis**: Compare `stddev_exec_time` to identify highly variable queries (indicators of resource contention or parameter-dependent performance)
- **Time-Series Analysis with pg_stat_statements_history**: Use historical snapshots (if extension installed) to track latency trends over hours/days and identify performance degradation
- **Query Log Analysis (CSV Format)**: Enable `log_statement` and `log_duration` to capture actual execution times in PostgreSQL logs; parse CSV logs to calculate quantiles
- **JSON Format Logging**: Enable `log_line_prefix` with JSON format to structure query logs for easier parsing and aggregation in external tools
- **pgBadger Log Parser**: Use pgBadger utility to parse PostgreSQL logs and generate HTML reports with latency distribution, slow queries, and trend analysis
- **Auto Explain Module**: Enable `auto_explain` extension to capture EXPLAIN plans for slow queries automatically, revealing execution plan issues
- **Query History Retention**: Archive `pg_stat_statements` snapshots periodically (e.g., hourly) to external table to maintain historical trends beyond session resets
- **Histogram Generation**: Collect execution times into buckets (e.g., <10ms, 10-50ms, 50-100ms, 100-500ms, >500ms) to visualize latency distribution shape
- **Correlation Analysis**: Cross-reference slow queries with system metrics (CPU, memory, disk I/O) at time of execution to identify resource bottlenecks
- **Parameter Value Tracking**: Use `log_parameter_max_length` to capture bind parameters of slow queries, revealing parameter-dependent performance differences
- **Index Usage Statistics**: Query `pg_stat_user_indexes` to correlate index scans/tuples with query times; identify missing indexes for slow queries
- **Sequential Scan Detection**: Identify queries causing sequential table scans using `pg_stat_user_tables` and correlate with slow query logs
- **Vacuum and Analyze Impact**: Track `last_vacuum`, `last_autovacuum`, `last_analyze` timestamps and correlate with latency spikes (bloat causes slowdown)
- **Connection Pooling Metrics**: Monitor connection pool metrics (active/idle connections) when analyzing latency; high connection count can increase contention
- **Lock Wait Analysis**: Check `pg_locks` and `pg_stat_activity` at time of slow queries to detect lock contention causing latency
- **Transaction Isolation Level Assessment**: Analyze whether queries experience higher latency at specific isolation levels (SERIALIZABLE slower than READ COMMITTED)
- **External Monitoring Tools Integration**: Send query metrics to Prometheus, Grafana, or DataDog for advanced visualization, alerting, and historical trending

**Practical Analysis Workflow**:
1. **Enable pg_stat_statements**: Ensure extension is installed and `shared_preload_libraries` includes it
2. **Baseline Collection**: Query pg_stat_statements to identify slowest queries (top 10-20 by total_time)
3. **Historical Snapshots**: Create periodic snapshots of pg_stat_statements data to table for trend analysis
4. **Percentile Calculation**: Calculate p50, p95, p99 latency for each query using SQL window functions
5. **Log Analysis**: Run pgBadger on PostgreSQL logs to generate visual reports and identify outliers
6. **Correlation Investigation**: Compare slow query times with system metrics and lock/vacuum events
7. **Root Cause Analysis**: Use EXPLAIN ANALYZE on slow queries to identify execution plan issues
8. **Monitoring Alert Setup**: Create alerts on p95 latency exceeding baseline × 2x threshold

**External Resources**:
- https://www.postgresql.org/docs/current/pgstatstatements.html
- https://pgbadger.darold.net/
- https://pganalyze.com/

#### ACID vs Two-Phase Commit
**Definition**: ACID properties guarantee transaction correctness within a single database; Two-Phase Commit (2PC) is a coordination protocol ensuring distributed transactions across multiple databases maintain consistency.

**ACID Properties Breakdown**:

| Property | Definition | Example | Guarantee Level |
|---|---|---|---|
| **Atomicity** | Transaction either completes fully or rolls back entirely; no partial state | Transfer $100: debit account A AND credit account B (both succeed or both fail) | Single database |
| **Consistency** | Database moves from valid state to valid state; all constraints maintained | Foreign key constraints, check constraints, NOT NULL always enforced | Single database |
| **Isolation** | Concurrent transactions don't interfere; reads don't see uncommitted writes | Two concurrent transfers to same account don't corrupt balance | Single database (varying levels) |
| **Durability** | Once committed, data persists despite failures (crashes, power loss) | Committed transaction survives database restart | Disk-based persistence |

**Isolation Levels (Weakest to Strongest)**:
- **READ UNCOMMITTED**: Allows dirty reads (reading uncommitted data); almost no isolation
- **READ COMMITTED**: Only sees committed data; default in PostgreSQL; prevents dirty reads
- **REPEATABLE READ**: Consistent view within transaction; prevents non-repeatable reads
- **SERIALIZABLE**: Full isolation; equivalent to sequential execution; prevents all anomalies

**Two-Phase Commit (2PC) Protocol**:

**Phase 1 (Prepare/Voting)**:
1. Coordinator sends "prepare" request to all participants
2. Each participant locks resources, validates transaction, and responds with "YES" (can commit) or "NO" (cannot commit)
3. Coordinator collects all responses

**Phase 2 (Commit/Abort)**:
1. If all participants voted "YES": Coordinator sends "commit" to all; all participants release locks and commit
2. If any participant voted "NO": Coordinator sends "abort" to all; all participants rollback and release locks
3. All participants acknowledge completion

**Key Differences**:

| Aspect | ACID | Two-Phase Commit |
|---|---|---|
| **Scope** | Single database transaction | Distributed transactions across multiple databases/systems |
| **Participants** | One DBMS | Multiple DBMSs or systems |
| **Coordination** | Built-in within database engine | External coordinator orchestrates protocol |
| **Latency** | Milliseconds (single system) | Seconds (network round-trips, waiting for slowest participant) |
| **Failure Tolerance** | Handles single system failures | Vulnerable to coordinator failures; blocking protocol |
| **Implementation** | Native database feature | Requires two-phase commit driver/middleware |
| **Use Case** | Local transactions in one DB | Cross-database consistency (e.g., payment + inventory sync) |

**ACID Guarantees Provided by PostgreSQL**:
- **Atomicity**: All-or-nothing; uses Write-Ahead Logging (WAL)
- **Consistency**: Enforces constraints, triggers, foreign keys
- **Isolation**: MVCC (Multi-Version Concurrency Control) enables non-blocking reads
- **Durability**: fsync to disk; survives server crash; WAL recovery

**Two-Phase Commit Limitations**:
- **Blocking**: Resources locked until Phase 2 completion; reduces concurrency
- **Coordinator Failure**: If coordinator crashes after Phase 1, participants remain in prepared state indefinitely (heuristic decisions required)
- **Network Dependency**: Requires reliable communication; network partitions cause deadlock
- **Performance Penalty**: Multiple round-trips = higher latency (50-100ms vs <1ms for single DB)
- **Complexity**: Requires timeout handling, retry logic, heuristic completion decisions
- **Not Partition Tolerant**: Fails in CAP theorem trade-off (sacrifices availability for consistency)

**When to Use ACID** (Single Database):
- Financial transactions (transfers between accounts in same database)
- Inventory updates with order placement (same database)
- User registration with profile creation (same database)
- Any multi-step transaction within single system

**When to Use Two-Phase Commit** (Distributed):
- Payment system (debit in Bank A, credit in Bank B) requires both to succeed
- Microservices coordination (update Order service AND Payment service atomically)
- Multi-database consistency (legacy systems that cannot be merged)
- Regulatory compliance requiring cross-system consistency (e.g., PCI DSS requirements)

**Modern Alternatives to 2PC** (Due to 2PC Limitations):
- **Saga Pattern**: Break distributed transaction into local transactions with compensation logic (if step 2 fails, rollback step 1)
- **Event Sourcing**: Record all events; allow eventual consistency between systems
- **Message Queues**: Async messaging with retry logic (Kafka, RabbitMQ) instead of synchronous coordination
- **CRDTs**: Conflict-free replicated data types for eventual consistency without coordination
- **Consensus Algorithms**: Raft, Paxos for distributed consensus without blocking

**PostgreSQL 2PC Implementation**:
- Uses `PREPARE TRANSACTION` to create prepared state (locked resources)
- Uses `COMMIT PREPARED` or `ROLLBACK PREPARED` for final decision
- Coordinator must track prepared transactions and ensure completion (even after restart)
- Suitable for internal system coordination; not recommended for public-facing APIs (too slow)

**External Resources**:
- https://en.wikipedia.org/wiki/ACID
- https://en.wikipedia.org/wiki/Two-phase_commit_protocol
- https://www.postgresql.org/docs/current/sql-prepare-transaction.html

### 1.3 SQL Optimization for Analytics

#### Window Functions
**Definition**: SQL functions performing calculations across rows related to the current row, enabling ranking, running totals, and moving averages without self-joins.

**Common Window Functions**:
- **Ranking**: ROW_NUMBER(), RANK(), DENSE_RANK(), NTILE()
- **Aggregation**: SUM(), AVG(), COUNT(), MIN(), MAX() OVER()
- **Navigation**: LEAD(), LAG(), FIRST_VALUE(), LAST_VALUE()
- **Partitioning**: PARTITION BY divides rows into groups for window calculations

**External Resources**:
- https://mode.com/sql-tutorial/sql-window-functions/
- https://www.postgresql.org/docs/current/tutorial-window.html
- https://www.sqlshack.com/overview-of-sql-rank-functions/

#### CTEs vs Subqueries
**Definition**: Common Table Expressions (CTEs) are named temporary result sets defined with WITH clause, offering better readability and reusability compared to nested subqueries.

**CTE Advantages**:
- **Readability**: Named intermediate results improve code clarity
- **Recursion**: Support recursive queries for hierarchical data
- **Multiple References**: CTE can be referenced multiple times in main query
- **Debugging**: Easier to test intermediate steps independently

**When to Use Subqueries**:
- Simple, one-time filtering operations
- Performance-critical queries where CTE optimization varies by database

**External Resources**:
- https://www.postgresql.org/docs/current/queries-with.html
- https://mode.com/sql-tutorial/sql-cte/
- https://www.essentialsql.com/introduction-common-table-expressions-ctes/

#### Query Performance Patterns
**Definition**: Best practices for writing efficient analytical queries including filter pushdown, join optimization, and avoiding common anti-patterns.

**Optimization Techniques**:
- **Filter Early**: Apply WHERE clauses before joins to reduce data volume
- **Avoid SELECT ***: Only select needed columns to reduce I/O
- **Use EXISTS vs IN**: EXISTS short-circuits on first match (faster for large datasets)
- **Proper JOIN Order**: Filter heavily first, join to larger tables later
- **Partition Pruning**: Filter on partitioned columns to skip entire partitions
- **Aggregate Before Join**: Pre-aggregate data before expensive joins

**Common Anti-Patterns**:
- **SELECT DISTINCT on large datasets**: Often indicates poor data modeling
- **NOT IN with nullable columns**: Can produce incorrect results
- **Correlated subqueries**: Often rewritable as JOINs for better performance
- **Functions on indexed columns**: WHERE YEAR(date_column) = 2024 prevents index use

**External Resources**:
- https://use-the-index-luke.com/
- https://mode.com/sql-tutorial/sql-performance-tuning/
- https://www.sisense.com/blog/8-ways-fine-tune-sql-queries-production-databases/

#### Set-Based Thinking
**Definition**: SQL paradigm focusing on operating on entire datasets at once rather than row-by-row processing, leveraging database optimizer for efficiency.

**Set-Based Principles**:
- Avoid cursors and loops in SQL (use set operations instead)
- Use UNION, INTERSECT, EXCEPT for combining sets
- Leverage GROUP BY for aggregations across sets
- Think in terms of transforming entire tables, not individual rows

**External Resources**:
- https://www.red-gate.com/simple-talk/databases/sql-server/t-sql-programming-sql-server/set-based-vs-procedural-approaches/
- https://www.sqlservercentral.com/articles/thinking-in-sets
- https://www.essentialsql.com/get-ready-to-learn-sql-server-set-based-vs-procedural-approaches/

---

## 2. Data Quality & Modeling

### 2.1 Schema Management & Evolution

#### Schema Evolution
**Definition**: Process of modifying data schemas (adding, removing, or changing columns/types) while maintaining compatibility with existing data and avoiding breaking changes.

**External Resources**:
- https://docs.confluent.io/kafka/schema-registry/schema-evolution.html
- https://delta.io/blog/2022-11-16-delta-lake-schema-inference/
- https://databricks.com/blog/2022/04/07/frequently-asked-questions-in-delta-lake.html

#### Backward Compatible ETL
**Definition**: ETL processes designed to handle incoming data with unknown or evolving schemas, gracefully accommodating new fields and data types without failing downstream systems.

**External Resources**:
- https://docs.confluent.io/kafka/schema-registry/schema-evolution.html
- https://iceberg.apache.org/docs/latest/schema-evolution/
- https://databricks.com/blog/2022/04/07/frequently-asked-questions-in-delta-lake.html

#### Blue-Green Deployment in Schema Evolution
**Definition**: Strategy where two identical production environments (blue and green) allow seamless schema changes by switching traffic to the updated environment while keeping the original running.

**External Resources**:
- https://martinfowler.com/bliki/BlueGreenDeployment.html
- https://docs.databricks.com/en/delta/versioning.html
- https://delta.io/blog/2022-01-25-delta-lake-as-a-data-archival-tool/

#### Schema Contract Validation
**Definition**: Validation mechanism ensuring incoming data conforms to predefined schema contracts before processing, catching data quality issues early.

**External Resources**:
- https://docs.confluent.io/kafka/schema-registry/schema-validation.html
- https://dbt.com/docs/guides/sl-overview
- https://greatexpectations.io/

#### Data Contracts
**Definition**: Formal agreements between data producers and consumers defining data structure, semantics, quality expectations, and SLAs for data products.

**Contract Components**:
- **Schema Definition**: Column names, types, nullability, constraints
- **Semantic Definitions**: Business meaning of each field
- **Quality Expectations**: Freshness, completeness, validity rules
- **SLAs**: Delivery time, availability guarantees
- **Ownership**: Data steward, support contacts

**Enforcement Approaches**:
- Schema Registry (Confluent, AWS Glue)
- Contract testing in CI/CD
- dbt model contracts
- Custom validation frameworks

**External Resources**:
- https://www.datamesh-architecture.com/data-mesh-principles/data-contracts
- https://docs.getdbt.com/docs/build/model-contracts
- https://datacontract.com/

#### API Versioning for Data
**Definition**: Strategies for evolving data APIs and schemas while maintaining backwards compatibility with existing consumers.

**Versioning Strategies**:
- **Semantic Versioning**: MAJOR.MINOR.PATCH for breaking/non-breaking changes
- **URI Versioning**: /v1/data, /v2/data for API endpoints
- **Header Versioning**: Accept-Version header for schema selection
- **Schema Compatibility Modes**: BACKWARD, FORWARD, FULL in Schema Registry

**Backwards Compatibility Rules**:
- Adding optional fields is always safe
- Removing or renaming fields breaks compatibility
- Changing field types breaks compatibility
- Adding default values for new required fields

**External Resources**:
- https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html
- https://semver.org/
- https://cloud.google.com/apis/design/versioning

### 2.2 Data Quality & Validation

#### Data Quality Frameworks: Deequ vs Great Expectations vs Custom
**Definition**: Data quality frameworks for detecting anomalies and validation. Deequ (Scala/PySpark) runs on Spark; Great Expectations (Python) provides flexible, testable data validation; custom validators offer specific business logic.

**External Resources**:
- https://github.com/awslabs/deequ
- https://greatexpectations.io/
- https://aws.amazon.com/blogs/big-data/test-data-quality-at-scale-with-deequ/

#### Data Drift Detection
**Definition**: Techniques and metrics to identify when data distributions or patterns change unexpectedly from their baseline, indicating potential data quality issues or model degradation.

**External Resources**:
- https://www.evidentlyai.com/blog/data-drift-detection
- https://greatexpectations.io/
- https://docs.seldon.io/projects/alibi-detect/en/latest/

#### Soft DELETE and Alternative Strategies
**Definition**: Soft delete marks records as deleted using flags rather than physical removal, preserving history. Alternatives include versioning, temporal tables, and ledger tables for audit trails.

**External Resources**:
- https://en.wikipedia.org/wiki/Soft_delete
- https://use-the-index-luke.com/sql/dml/delete/soft-delete
- https://docs.microsoft.com/en-us/sql/relational-databases/tables/temporal-tables

#### Data Testing Strategies
**Definition**: Testing approaches ensuring data pipeline correctness, including unit tests for transformations, integration tests for end-to-end flows, and data quality tests for outputs.

**Testing Types**:
- **Unit Tests**: Test individual transformations (SQL logic, Python functions)
- **Integration Tests**: Test complete pipeline flows with test data
- **Contract Tests**: Verify schema and data format agreements
- **Data Quality Tests**: Validate output data meets expectations
- **Regression Tests**: Ensure changes don't break existing behavior

**Testing Approaches**:
- **Snapshot Testing**: Compare output to known-good baseline
- **Property-Based Testing**: Verify invariants (e.g., row counts, null constraints)
- **Golden Dataset Testing**: Run pipelines against curated test datasets
- **Shadow Pipelines**: Run new logic in parallel with production

**External Resources**:
- https://docs.getdbt.com/docs/build/tests
- https://docs.greatexpectations.io/docs/tutorials/getting_started/
- https://www.testcontainers.org/

#### Data Governance & Lineage
**Definition**: Practices and technologies for managing data as an organizational asset, including tracking data flow, enforcing policies, and maintaining metadata.

**Data Governance Components**:
- **Data Catalog**: Searchable inventory of data assets (Alation, Atlan, DataHub)
- **Data Lineage**: Visual tracking of data flow from source to destination
- **Metadata Management**: Technical and business metadata storage
- **Access Control**: Who can access which data and how
- **Data Classification**: Sensitivity levels (PII, confidential, public)

**Data Lineage Levels**:
- **Table-Level**: Which tables feed into which downstream tables
- **Column-Level**: How specific columns propagate through transformations
- **Row-Level**: Tracking individual record provenance (for compliance)

**Benefits**:
- Impact analysis before making changes
- Root cause analysis when data issues occur
- Compliance audit trails (GDPR, CCPA)
- Data discovery for analysts

**External Resources**:
- https://www.datahubproject.io/
- https://www.alation.com/
- https://www.atlan.com/

### 2.3 Data Modeling

#### Slow Changing Dimension Type 2
**Definition**: Dimensional modeling technique tracking historical changes by adding version numbers and valid date ranges, enabling point-in-time analysis.

**External Resources**:
- https://en.wikipedia.org/wiki/Slowly_changing_dimension
- https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimension-tables/slowly-changing-dimensions/
- https://www.youtube.com/watch?v=m9YngFlwlSo

#### All SCD Types Overview
**Definition**: Comprehensive overview of Slowly Changing Dimension strategies for handling attribute changes in dimensional models.

**SCD Type Comparison**:

| Type | Behavior | History | Use Case |
|------|----------|---------|----------|
| **Type 0** | Never update | None | Static attributes (birth date, original signup date) |
| **Type 1** | Overwrite | None | Non-critical attributes, current state only |
| **Type 2** | Add new row | Full history | Critical attributes requiring historical analysis |
| **Type 3** | Add column | Limited (1 prior) | Only need current + previous value |
| **Type 4** | Separate history table | Full history | Performance optimization, large dimensions |
| **Type 6** | Hybrid (1+2+3) | Full + current | Need both historical and current-state queries |

**SCD Type 0 (Retain Original)**:
- Never change the value once set
- Use for immutable attributes
- Example: Customer original_signup_date

**SCD Type 1 (Overwrite)**:
- Simply update in place, losing history
- Simplest implementation
- Use when history doesn't matter

**SCD Type 3 (Add Column)**:
- Store current and previous value in separate columns
- Example: current_address, previous_address
- Limited history (only one previous value)

**SCD Type 4 (History Table)**:
- Keep current values in main dimension table
- Store all historical changes in separate history table
- Better query performance for current-state queries

**SCD Type 6 (Hybrid)**:
- Combines Type 1 + Type 2 + Type 3
- Maintains full history rows (Type 2) plus current value column (Type 1)
- Enables both historical and current-state analysis efficiently

**External Resources**:
- https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-2-slow-change-dimensions/
- https://en.wikipedia.org/wiki/Slowly_changing_dimension
- https://www.sqlshack.com/implementing-slowly-changing-dimensions-scds-in-data-warehouses/

#### Snapshot Tables
**Definition**: Point-in-time captures of data at regular intervals (daily, hourly), enabling historical analysis without full SCD complexity.

**Use Cases**:
- Daily balance snapshots for financial reporting
- Periodic state captures for trend analysis
- Simplifying queries that need "as of" views

**Implementation Patterns**:
- Append-only with snapshot_date partition
- Store full state at each snapshot interval
- Delete old snapshots based on retention policy

**External Resources**:
- https://docs.getdbt.com/docs/build/snapshots
- https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/periodic-snapshot-fact-table/
- https://delta.io/blog/2022-09-08-time-travel-delta-lake/

#### Deduplication Strategies
**Definition**: Techniques for identifying and removing duplicate records in data pipelines while preserving data integrity.

**Deduplication Approaches**:
- **Exact Match**: Hash all columns, group by hash, keep one
- **Fuzzy Match**: Similarity algorithms for near-duplicates
- **Business Key**: Dedupe on natural keys (email, customer_id)
- **Temporal**: Keep latest/earliest record per key

**SQL Patterns**:
- ROW_NUMBER() OVER (PARTITION BY key ORDER BY timestamp DESC)
- QUALIFY clause for window function filtering
- DISTINCT ON (PostgreSQL)
- MERGE statement for upserts

**External Resources**:
- https://docs.getdbt.com/blog/how-to-deduplicate-data-in-sql
- https://www.sqlshack.com/different-ways-to-find-and-remove-duplicate-records-in-sql-server-tables/
- https://docs.databricks.com/en/delta/merge.html

---
