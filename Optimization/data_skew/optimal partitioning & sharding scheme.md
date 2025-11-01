# Step-by-step guide — Constructing an optimal partitioning & sharding scheme for RDBMS

## 1) Describe objectives and constraints

- Define SLA (latency, p99), capacity (QPS, write rate), and consistency requirements.
- List workload types: read-heavy, write-heavy, transactional (multi-row/multi-shard), analytic.
- Inventory constraints: existing client drivers, foreign keys, backups, ops team capacity.

## 2) Measure current workload and data shape

- Capture per-key QPS, query patterns, hotspot keys, table growth rates and row sizes.
- Measure cardinality and distribution of candidate partition keys (user_id, created_at, tenant_id).
- Identify cross-row transactions and referential constraints.

## 3) Choose partitioning level and approach

- Table partitioning (same DB instance) when you need pruning and retention (time-series, large tables).
  - Range partitioning: good for time-based data and fast range scans.
  - List partitioning: good for well-known categorical values (regions, tenants).
  - Hash partitioning: good to evenly spread inserts across physical partitions.
- Sharding (multi-node) when single node capacity is insufficient.
  - Shard by tenant/user/region or hashed surrogate to balance load.
  - Use consistent hashing or lookup-based mapping for flexible rebalancing.

## 4) Select partition/shard key using practical heuristics

- Choose a key with:
  - High cardinality (avoid tiny number of buckets).
  - Correlation to access patterns (locality helps range queries).
  - Low skew or ability to transform (salt/hash) if skewed.
- Avoid global monotonically-increasing keys (auto-increment) as sole shard key.

## 5) Design key transformations and mapping

- If hot keys exist, apply salting or prefix hashing to disperse writes (note added read fan-in).
- For range locality where range queries matter, use composite keys: (tenant_id, created_at).
- Maintain a shard map service (simple mapping table) or deterministic hash function in clients.

## 6) Plan schema and application changes

- Remove or adapt cross-shard foreign keys and joins:
  - Denormalize where necessary, or implement application-level joins/fan-out.
- Replace global sequences with per-shard sequences or GUIDs.
- Ensure idempotency for write retries (idempotency tokens).

## 7) Design routing and transaction model

- Routing:
  - Client-side routing for deterministic maps (fast, fewer hops).
  - Proxy/router service for flexible remapping and connection pooling.
- Transactions:
  - Prefer single-shard transactions. For cross-shard workflows use sagas/compensating transactions.
  - If distributed transactions required, design for low frequency and accept performance cost.

## 8) Replication and read scaling

- Add read replicas per shard for read-heavy workloads.
- Consider cache layers (Redis) keyed by logical key and invalidate consistently.
- Use follower reads where stale data is acceptable.

## 9) Plan rebalancing, split and migration procedures

- For hash shards: use consistent hashing with virtual nodes for online rebalancing.
- For range shards: plan split points and online chunk migration tools.
- Implement throttled data migration (backfill jobs with rate limits) and automated routing updates.

## 10) Operational considerations

- Backups, restore, and schema migrations per shard — ensure automation and orchestration.
- Monitoring: per-shard metrics (CPU, disk, QPS, latency) and top-k key detection.
- Alerts for hotspot growth and imbalanced shard utilization.

## 11) Test and validate

- Run load tests using real access patterns (90/9/1, Zipfian) to validate distribution.
- Test failure modes: node loss, network partition, and failover.
- Validate operational tasks: shard split, migration, schema change rollouts.

## 12) Rollout strategy

- Start with non-production canary shard(s).
- Migrate a low-risk tenant or traffic slice first; monitor metrics and rollback plan.
- Automate progressive rollout (increase shards/tenants gradually).

## 13) Iterate and automate

- Automate shard mapping updates, health checks, and rebalancing.
- Continuously collect per-key heavy hitter stats and trigger partition splits or remaps when thresholds exceeded.

## 14) Example SQL snippets (Postgres/MySQL style)

- Range partition (Postgres):
  - CREATE TABLE events (...) PARTITION BY RANGE (created_at);
  - CREATE TABLE events_y2025 PARTITION OF events FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
- Hash partition (MySQL 8+):
  - CREATE TABLE t (id BIGINT, ...) PARTITION BY HASH(id) PARTITIONS 16;

## 15) Decision checklist (quick)

- Does the key support required queries (range vs random access)?
- Can you tolerate increased read complexity (salting/denorm)?
- Are cross-shard transactions minimal or can be redesigned?
- Is the ops team ready for migrations and per-shard maintenance?

## Notes

- There is no one-size-fits-all: prefer simple deterministic sharding first; add complexity (proxy, consistent hashing, auto-split) only when justified by scale.
- Keep monitoring and automation as first-class features to detect and react to skew early.
