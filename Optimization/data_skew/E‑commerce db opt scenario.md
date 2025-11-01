# Questions to Ask (E‑commerce analytical Postgres DW)

Below are targeted questions, expected answer examples, and how each expected answer shapes the optimization plan.

1. **Business goals & SLAs**  
   - Expected answer: "Ad hoc analytics with sub-5s dashboard queries; nightly ETL completes by 02:00; p99 query latency <10s for slices."  
   - How it helps: Prioritizes optimizations (query latency vs ETL throughput), defines acceptable tradeoffs (e.g., materialized views vs fresh data), and sets SLO targets.

2. **Workload profile (read vs write, query shapes)**
   - Expected answer: "Mostly reads from dashboards and BI tools, heavy aggregations on orders/line_items; bulk loads nightly; occasional ad‑hoc joins."  
   - How it helps: Guides partitioning (time-based for orders), indexing and materialization strategy (pre-aggregate order metrics), and resource allocation between OLAP reads and ETL writes.

3. **Query patterns and hot queries**
   - Expected answer: "Top 20 queries account for 70% of cost: multi-join order lifetime, customer LTV, cohort analysis."  
   - How it helps: Focus tuning on expensive queries (optimizer hints, rewrite, specialized materialized views), and plans for query-level caching.

4. **Data volume, growth rate and retention policy**  
   - Expected answer: "Current 2 TB, +30%/yr; orders retained 5 years; event logs 90 days."  
   - How it helps: Determines partitioning granularity and retention automation, sizing for storage and index pruning, and cold/hot storage design.

5. **Schema & cardinality (table row counts, PKs, FK relationships)**  
   - Expected answer: "orders (100M rows), order_items (500M), products (1M). Many-to-one FKs from order_items→orders."  
   - How it helps: Informs shard/partition keys (partition orders by created_at, keep order_items co-located), and evaluates feasibility of co-locating related rows.

6. **Current partitioning/sharding and ops constraints**  
   - Expected answer: "No sharding; some partitioning by month on events; ops prefers minimal app changes."  
   - How it helps: If ops prefer minimal app changes, favor Postgres table partitioning, read replicas, and materialized views over full sharding or client-side routing.

7. **ETL/ingest patterns and windows (batch vs streaming)**  
   - Expected answer: "Nightly batch loads from OLTP via CDC + some streaming click events every few minutes."  
   - How it helps: Determines safe times for heavy maintenance, enables incremental partition backfills, and influences use of COPY/partition exchange vs upserts.

8. **Concurrency and user traffic patterns (BI tool connections, ad‑hoc users)**
   - Expected answer: "Few concurrent BI users (10s) but many concurrent dashboard widgets firing queries."  
   - How it helps: Necessitates connection pooling, prepared statements, and result caching or query result materialization to avoid saturating DB workers.

9. **Indexing strategy and pain points (index size, bloat, hot indexes)**  
   - Expected answer: "Large b-tree indexes on order_id and created_at; index bloat causing slow VACUUM."  
   - How it helps: Drives index consolidation, use of partial or BRIN indexes for range scans, and scheduled maintenance windows for VACUUM/REINDEX.

10. **Hardware and infra (CPU, memory, disk type, cloud/on‑prem, replicas)**  
    - Expected answer: "Cloud-managed Postgres 8 vCPU, 64GB RAM, NVMe; 2 read replicas."  
    - How it helps: Determines in-memory vs disk-bound strategy (increase work_mem, effective_cache_size), feasibility of adding replicas, and storage optimizations (compression, tablespaces).

11. **Backup/restore & DR requirements**  
    - Expected answer: "Daily backups; RTO 4h; point-in-time recovery 7 days."  
    - How it helps: Affects acceptable migration approaches (online vs offline), ability to test schema changes, and how aggressive you can be with destructive optimizations.

12. **Consistency & correctness requirements for analytics**  
    - Expected answer: "Eventual consistency acceptable for dashboards; financial reports need exact counts."  
    - How it helps: Enables asynchronous replication, summary tables for dashboards, and stricter paths (single-node aggregates) for financial reports.

13. **Regulatory & compliance constraints (PII, encryption, locality)**  
    - Expected answer: "EU customer data must stay in EU; PII must be encrypted at rest."  
    - How it helps: Constrains shard placement, backup locations, and may require tokenization/column encryption that influences indexability and query plans.

14. **Monitoring, observability & current pain signals**  
    - Expected answer: "We have pg_stat_statements, Grafana dashboards; alerts for queueing and slow queries but missing per-partition metrics."  
    - How it helps: Identifies gaps to instrument (per-partition IO, top-k keys), enables creation of alerting for skew, and informs what immediate visibility improvements are needed.

15. **Cost constraints and maintenance windows**  
    - Expected answer: "Budget limited; maintenance windows at 02:00–04:00; prefer low ops overhead."  
    - How it helps: Favors lower-cost optimizations (SQL tuning, partitioning, read replicas) over expensive re-architecting (full sharding across clusters) and schedules heavy migrations within windows.

16. **Expected traffic patterns during promotions / Black Friday**  
    - Expected answer: "10x traffic spikes for 24–48 hours annually; writes surge for orders and checkout events."  
    - How it helps: Drives autoscaling plans, pre-splitting or pre-warming partitions, queueing/buffering writes, and stress-testing for high‑skew scenarios.

17. **Data quality and schema drift concerns**  
    - Expected answer: "Occasional schema changes from upstream services; data quality issues in event payloads."  
    - How it helps: Necessitates flexible ETL (schema-on-read), robust staging tables, and migration-safe schema change strategies (backfill jobs, feature toggles).

18. **Long-running analytical queries & BI expectations (ad‑hoc joins, exports)**  
    - Expected answer: "Analysts run heavy exports and ad‑hoc joins that sometimes degrade cluster performance."  
    - How it helps: Suggests separating workloads (analytics cluster, read replicas, query routing), resource queues, or using a separate OLAP engine (e.g., materialized aggregates, columnar copy).

19. **Tolerance for schema denormalization or duplicate data**  
    - Expected answer: "Denormalization acceptable if it improves performance and reduces joins."  
    - How it helps: Justifies building summary tables, pre-joined tables, and localized indices to reduce cross-partition joins.

20. **Future roadmap (expected product or data model changes)**  
    - Expected answer: "Planning multi-region expansion and adding more detailed event tracking."  
    - How it helps: Encourages designs that support re-sharding, consistent hashing, geo-replication, and partitioning schemes that can evolve without disruptive rewrites.

---

For each real answer, I would:

- Map constraints to a prioritized action list (quick wins: indexes, query rewrites, materialized views; medium: partitioning and BRIN/partial indexes; long: sharding, cross‑region replication).  
- Produce a measurable test plan (benchmarks with representative data and Zipfian skews), migration steps, rollback plan, and monitoring/alerting changes.

If you want, paste environment details (pg version, table stats, example slow query plans) and I’ll produce a prioritized, step‑by‑step optimization runbook.
