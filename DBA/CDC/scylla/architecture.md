# ScyllaDB to PostgreSQL CDC Pipeline - Architecture

## Overview

This document describes the architecture of the Change Data Capture (CDC) pipeline that replicates data from ScyllaDB to PostgreSQL in near real-time using Kafka Connect.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CDC Pipeline Architecture                       │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│              │         │              │         │              │
│  ScyllaDB    │────────▶│    Kafka     │────────▶│ PostgreSQL   │
│  (Source)    │  CDC    │   Connect    │  Sink   │  (Target)    │
│              │         │              │         │              │
└──────────────┘         └──────────────┘         └──────────────┘
       │                        │                         │
       │                        │                         │
       │                        ▼                         │
       │                 ┌──────────────┐                │
       │                 │    Kafka     │                │
       │                 │   Broker     │                │
       │                 └──────────────┘                │
       │                        │                         │
       │                        ▼                         │
       │                 ┌──────────────┐                │
       │                 │   Schema     │                │
       │                 │  Registry    │                │
       │                 └──────────────┘                │
       │                                                  │
       └──────────────────┬───────────────────────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │Reconciliation│
                   │   Service    │
                   └──────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│                       Observability Stack                                 │
├──────────────────────────────────────────────────────────────────────────┤
│  Prometheus ──▶ Grafana Dashboards                                       │
│  Jaeger     ──▶ Distributed Tracing                                      │
│  Logs       ──▶ Structured JSON with Correlation IDs                     │
└──────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. ScyllaDB (Source Database)

**Purpose**: Source database with CDC-enabled tables

**Key Features**:
- CDC logs capture all INSERT, UPDATE, DELETE operations
- Change streams provide ordered, consistent change events
- Horizontal scalability with distributed architecture

**CDC Tables**:
- `app_data.users`
- `app_data.products`
- `app_data.orders`
- `app_data.order_items`
- `app_data.inventory_transactions`

**Connection**:
- Protocol: CQL (Cassandra Query Language)
- Port: 9042
- Driver: DataStax Cassandra driver

### 2. Kafka Ecosystem

#### 2.1 Kafka Broker

**Purpose**: Message broker for CDC event streaming

**Configuration**:
- Topic prefix: `cdc.scylla.*`
- Partitions: 8 per topic (configurable)
- Replication factor: 1 (single-node dev), 3 (production)
- Retention: 24 hours (86400000 ms)
- Compression: Snappy

**Topics**:
- `cdc.scylla.users` - User table changes
- `cdc.scylla.products` - Product table changes
- `cdc.scylla.orders` - Order table changes
- `cdc.scylla.order_items` - Order item table changes
- `cdc.scylla.inventory_transactions` - Inventory transaction changes
- `dlq-scylla-source` - Dead Letter Queue for failed source events
- `dlq-postgres-sink` - Dead Letter Queue for failed sink events
- `heartbeat.scylla` - Heartbeat messages every 30s
- `scylla-schema-history` - Schema evolution tracking

#### 2.2 Schema Registry

**Purpose**: Centralized schema management for Avro messages

**Features**:
- Schema versioning with backward/forward compatibility
- Schema evolution tracking
- Avro schema storage and validation

**Compatibility Modes**:
- `BACKWARD` (default): New schema can read old data
- `FORWARD`: Old schema can read new data
- `FULL`: Both backward and forward compatible
- `NONE`: No compatibility checks

**Port**: 8081

#### 2.3 Kafka Connect

**Purpose**: Distributed streaming platform for connector execution

**Architecture**:
- **Workers**: 4 tasks per connector (configurable)
- **Distribution**: Tasks distributed across available workers
- **Fault Tolerance**: Automatic task rebalancing on worker failure
- **Offset Management**: Kafka-based offset storage for exactly-once semantics

**Connectors**:
1. **ScyllaDB Source Connector** (`scylla-source`)
2. **PostgreSQL Sink Connector** (`postgres-sink`)

### 3. ScyllaDB Source Connector

**Connector Class**: `com.scylladb.cdc.debezium.connector.ScyllaConnector`

**Key Configuration**:
- **Snapshot mode**: `initial` - full table snapshot on first run
- **Consistency mode**: `all_tables` - consistent snapshot across all tables
- **Poll interval**: 1000ms
- **Batch size**: 2048 records
- **Queue size**: 8192 records

**Data Flow**:
1. Connect to ScyllaDB CDC streams
2. Read change events from CDC log tables
3. Convert to Kafka Connect records
4. Apply transformations (metadata, correlation ID)
5. Serialize to Avro format using Schema Registry
6. Publish to Kafka topics

**Transformations**:
- `addMetadata`: Add `cdc_timestamp` and `cdc_source` fields
- `addCorrelationId`: Insert correlation ID header for tracing
- `route`: Route messages to appropriate topics using regex

**Error Handling**:
- Tolerance: `all` - continue processing on errors
- Dead Letter Queue: `dlq-scylla-source`
- Log all errors with full messages
- Include error context in DLQ headers

### 4. PostgreSQL Sink Connector

**Connector Class**: `io.confluent.connect.jdbc.JdbcSinkConnector`

**Key Configuration**:
- **Connection pool size**: 10
- **Batch size**: 1000 records
- **Max retries**: 10
- **Retry backoff**: 3000ms

**Insert Modes**:
- `upsert`: INSERT or UPDATE based on primary key
- `insert`: INSERT only (fail on conflict)
- `update`: UPDATE only (fail if not exists)

**Data Flow**:
1. Consume messages from Kafka topics
2. Deserialize from Avro using Schema Registry
3. Apply transformations and filtering
4. Batch records for efficiency
5. Execute SQL statements (INSERT, UPDATE, DELETE)
6. Commit offsets on success

**Schema Mapping**:
- Automatic schema inference from Avro
- Field name mapping (snake_case to camelCase)
- Type conversions (UUID, TIMESTAMP, DECIMAL)

**Error Handling**:
- Tolerance: `all`
- Dead Letter Queue: `dlq-postgres-sink`
- Transaction rollback on batch failure
- Automatic retry with exponential backoff

### 5. PostgreSQL (Target Database)

**Purpose**: Data warehouse for replicated data

**Schema Structure**:
- **Schema**: `cdc_data` - replicated tables
- **Tables**: Mirror ScyllaDB table structure
- **Indexes**: Primary keys, foreign keys, performance indexes

**Connection**:
- Protocol: PostgreSQL wire protocol
- Port: 5432
- Driver: psycopg2 (Python), JDBC (Kafka Connect)

**Data Consistency**:
- Primary key enforcement
- Foreign key constraints (where applicable)
- NOT NULL constraints
- Unique constraints

### 6. Reconciliation Service

**Purpose**: Periodic data consistency validation and repair

**Components**:
- `src/reconciliation/comparer.py` - Row-level comparison
- `src/reconciliation/differ.py` - Discrepancy detection
- `src/reconciliation/repairer.py` - SQL repair action generation
- `scripts/reconcile.py` - CLI reconciliation tool

**Modes**:
- **Full reconciliation**: Compare all rows across all tables
- **Incremental reconciliation**: Compare only recent changes
- **Dry-run**: Generate repair actions without executing

**Workflow**:
1. **Extract**: Fetch rows from ScyllaDB and PostgreSQL
2. **Compare**: Identify missing, extra, and mismatched rows
3. **Repair**: Generate and execute SQL repair actions
4. **Report**: Log discrepancies and metrics

**Scheduling**:
- Cron-based scheduling via `scripts/schedule-reconciliation.sh`
- Recommended frequency: Daily for full, Hourly for incremental
- Checkpoint-based resumption for large datasets

### 7. Observability Stack

#### 7.1 Prometheus

**Purpose**: Metrics collection and alerting

**Custom Metrics**:
- `cdc_replication_lag_seconds` - Lag between source and target
- `cdc_records_replicated_total` - Total records replicated
- `cdc_replication_errors_total` - Replication error count
- `cdc_reconciliation_runs_total` - Reconciliation runs
- `cdc_discrepancies_found_total` - Data discrepancies
- `cdc_data_accuracy_percentage` - Data accuracy (0-100%)
- `cdc_schema_changes_total` - Schema change count
- `cdc_schema_compatibility_failures_total` - Schema compatibility failures
- `cdc_dlq_messages_total` - DLQ message count
- `cdc_connector_healthy` - Connector health status (0/1)

**Alert Rules**:
- High replication lag (>300s warning, >900s critical)
- High error rate (>0.1 errors/sec)
- Data discrepancy (accuracy <95% warning, <90% critical)
- DLQ backlog (>100 messages warning, >1000 critical)
- Connector down (>2 minutes)

#### 7.2 Grafana

**Purpose**: Metrics visualization and dashboards

**Dashboards**:
1. **Connector Health** - Real-time connector status, throughput, lag, errors
2. **Schema Evolution** - Schema versions, changes, compatibility failures
3. **Reconciliation** - Data accuracy, discrepancies, repair actions

**Features**:
- Auto-refresh (10-30s intervals)
- Threshold-based color coding
- Drill-down capabilities
- Time range selection (1h, 6h, 24h, 7d)

#### 7.3 Jaeger

**Purpose**: Distributed tracing for end-to-end visibility

**Trace Flow**:
1. ScyllaDB CDC event generated with trace ID
2. Kafka message published with trace context headers
3. Kafka Connect processing traced
4. PostgreSQL write operation traced
5. Full trace visible in Jaeger UI

**Trace Context Propagation**:
- W3C Trace Context format
- Correlation ID in Kafka message headers
- Structured logging with correlation ID

#### 7.4 Logging

**Format**: Structured JSON logging

**Fields**:
- `timestamp` - ISO 8601 format (UTC)
- `level` - Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `message` - Log message
- `correlation_id` - Trace correlation ID
- `table` - Affected table name
- `component` - Component name (reconciliation, connector, etc.)
- Additional context fields (duration, discrepancies, etc.)

**Log Aggregation**:
- Centralized log collection (Fluentd, Logstash, etc.)
- Log rotation (30 days retention)
- Searchable by correlation ID

## Data Flow

### 1. Normal Replication Flow

```
1. Application writes to ScyllaDB (INSERT/UPDATE/DELETE)
   └─▶ ScyllaDB writes to base table
       └─▶ ScyllaDB writes to CDC log table

2. Source Connector polls CDC log
   └─▶ Read change event (operation type, before/after values)
       └─▶ Add metadata (timestamp, source, correlation ID)
           └─▶ Serialize to Avro format
               └─▶ Publish to Kafka topic

3. Kafka Broker stores message
   └─▶ Message persisted to disk
       └─▶ Schema registered with Schema Registry
           └─▶ Message available for consumption

4. Sink Connector consumes message
   └─▶ Deserialize from Avro
       └─▶ Transform to SQL statement
           └─▶ Batch with other records
               └─▶ Execute SQL transaction

5. PostgreSQL applies changes
   └─▶ Row inserted/updated/deleted
       └─▶ Transaction committed
           └─▶ Offset committed to Kafka

6. Observability
   └─▶ Metrics exported to Prometheus
       └─▶ Trace sent to Jaeger
           └─▶ Logs written with correlation ID
```

### 2. Error Handling Flow

```
1. Connector encounters error
   └─▶ Log error with full context
       └─▶ Increment error metrics
           └─▶ Route message to Dead Letter Queue

2. Dead Letter Queue
   └─▶ Message persisted with error details
       └─▶ Headers include: error type, stack trace, timestamp
           └─▶ Alert triggered if threshold exceeded

3. DLQ Monitoring
   └─▶ Check DLQ message count (scripts/check-dlq.sh)
       └─▶ Analyze error patterns
           └─▶ Manual investigation

4. DLQ Replay
   └─▶ Fix root cause (schema, data, configuration)
       └─▶ Replay messages (scripts/replay-dlq.sh)
           └─▶ Verify successful reprocessing
```

### 3. Reconciliation Flow

```
1. Scheduled reconciliation run
   └─▶ Load checkpoint (if resuming)
       └─▶ Query ScyllaDB for batch of rows

2. Compare with PostgreSQL
   └─▶ Fetch matching rows from PostgreSQL
       └─▶ Identify discrepancies (missing, extra, mismatched)

3. Generate repair actions
   └─▶ Missing in target → INSERT
       └─▶ Extra in target → DELETE
           └─▶ Mismatched values → UPDATE

4. Execute repairs (if not dry-run)
   └─▶ Execute SQL statements
       └─▶ Log repair actions
           └─▶ Update metrics

5. Save checkpoint
   └─▶ Persist last processed key
       └─▶ Allow resumption if interrupted

6. Report generation
   └─▶ Summary: discrepancies found, repairs executed
       └─▶ Metrics: data accuracy percentage
           └─▶ Alerts: trigger if accuracy below threshold
```

## Deployment Architecture

### Development Environment

```
Single Docker Host
├── ScyllaDB container (1 node)
├── PostgreSQL container
├── Kafka container (1 broker)
├── Zookeeper container
├── Schema Registry container
├── Kafka Connect container
├── Prometheus container
├── Grafana container
└── Jaeger container
```

**Resource Requirements**:
- CPU: 8 cores minimum
- RAM: 16 GB minimum
- Disk: 100 GB (SSD recommended)

### Production Environment

```
Multi-Node Cluster
├── ScyllaDB Cluster (3+ nodes)
│   ├── Node 1 (coordinator)
│   ├── Node 2 (replica)
│   └── Node 3 (replica)
├── Kafka Cluster (3+ brokers)
│   ├── Broker 1
│   ├── Broker 2
│   └── Broker 3
├── Zookeeper Ensemble (3+ nodes)
├── Kafka Connect Cluster (3+ workers)
├── PostgreSQL (Primary + Replica)
│   ├── Primary (read-write)
│   └── Replica (read-only)
├── Schema Registry (HA setup)
├── Observability Stack
│   ├── Prometheus (HA with federation)
│   ├── Grafana (load balanced)
│   └── Jaeger (distributed backend)
└── Reconciliation Service (scheduled jobs)
```

**Resource Requirements**:
- **ScyllaDB**: 16 cores, 64 GB RAM, 1 TB NVMe per node
- **Kafka**: 8 cores, 32 GB RAM, 500 GB SSD per broker
- **Kafka Connect**: 4 cores, 16 GB RAM per worker
- **PostgreSQL**: 16 cores, 64 GB RAM, 1 TB SSD
- **Observability**: 8 cores, 32 GB RAM, 500 GB disk

## Security Architecture

### 1. Network Security

- **Firewall Rules**: Restrict access to necessary ports only
- **Network Segmentation**: Separate networks for data, management, monitoring
- **VPC/Subnets**: Isolated network environments

### 2. Authentication & Authorization

- **ScyllaDB**: Username/password authentication, role-based access control
- **PostgreSQL**: Password authentication, SSL certificate auth, row-level security
- **Kafka**: SASL/SCRAM authentication, ACLs for topic access
- **Schema Registry**: Basic authentication, SSL/TLS encryption
- **Grafana**: OAuth integration, LDAP/AD authentication

### 3. Encryption

- **In Transit**: TLS 1.2+ for all connections (ScyllaDB, PostgreSQL, Kafka, Schema Registry)
- **At Rest**: Encrypted disks for data storage (LUKS, dm-crypt)
- **Secrets Management**: External secrets store (HashiCorp Vault, AWS Secrets Manager)

### 4. Secrets Management

**Configuration**:
```json
{
  "scylla.user": "${file:/vault/secrets/scylla-credentials:username}",
  "scylla.password": "${file:/vault/secrets/scylla-credentials:password}",
  "connection.user": "${file:/vault/secrets/postgres-credentials:username}",
  "connection.password": "${file:/vault/secrets/postgres-credentials:password}"
}
```

**Best Practices**:
- Never commit credentials to version control
- Rotate credentials regularly (90 days)
- Use least-privilege principle
- Audit all credential access

## Performance Characteristics

### Throughput

- **Source Connector**: 10,000 events/sec (single worker)
- **Kafka Broker**: 100,000 messages/sec (3-broker cluster)
- **Sink Connector**: 5,000 events/sec (single worker)

**Factors Affecting Throughput**:
- Batch size configuration
- Number of parallel tasks
- Network latency
- PostgreSQL write performance

### Latency

- **End-to-end latency**: 100-500ms (p95)
- **ScyllaDB → Kafka**: 10-50ms
- **Kafka → PostgreSQL**: 50-200ms
- **Reconciliation lag**: 24 hours (daily schedule)

**Factors Affecting Latency**:
- Poll interval (source connector)
- Kafka consumer lag
- PostgreSQL transaction commit time
- Network round-trip time

### Scalability

**Horizontal Scaling**:
- **ScyllaDB**: Add nodes to cluster (linear scalability)
- **Kafka**: Add brokers and increase partitions
- **Kafka Connect**: Add workers (scales to number of tasks)
- **PostgreSQL**: Read replicas for query load

**Vertical Scaling**:
- Increase CPU/RAM for compute-bound workloads
- Faster disks (NVMe) for I/O-bound workloads

## Failure Modes and Recovery

### 1. Source Connector Failure

**Symptoms**: No new events in Kafka topics

**Recovery**:
1. Check connector status: `scripts/health-check.sh`
2. Review connector logs for errors
3. Restart connector: `scripts/deploy-connector.sh restart scylla-source`
4. Verify offset preservation (no data loss)

### 2. Sink Connector Failure

**Symptoms**: Increasing consumer lag, no PostgreSQL updates

**Recovery**:
1. Check DLQ for failed messages
2. Review sink connector logs
3. Fix root cause (schema, constraint violations)
4. Restart sink connector
5. Replay DLQ messages if needed

### 3. Network Partition

**Symptoms**: Connection timeouts, lag increase

**Recovery**:
- Automatic reconnection with exponential backoff
- No manual intervention required (tested via `scripts/test-network-partition.sh`)

### 4. Data Discrepancy

**Symptoms**: Reconciliation alerts, accuracy <100%

**Recovery**:
1. Run reconciliation: `scripts/reconcile.py full --table <table>`
2. Review discrepancy report
3. Execute repair actions: `scripts/reconcile.py full --table <table> --execute-repairs`
4. Investigate root cause (connector failure, data corruption)

## Monitoring and Alerting Strategy

### Key Metrics to Monitor

1. **Replication Lag**: Target <60s, Alert >300s
2. **Error Rate**: Target 0%, Alert >0.1%
3. **Data Accuracy**: Target 100%, Alert <95%
4. **DLQ Messages**: Target 0, Alert >100
5. **Connector Health**: Target 100%, Alert on failure

### Alert Severity Levels

- **Critical**: Immediate action required (connector down, data accuracy <90%)
- **Warning**: Investigation needed (high lag, error rate, accuracy <95%)
- **Info**: Informational only (schema changes, reconciliation runs)

### On-Call Response

1. **Critical Alerts**: Respond within 15 minutes
2. **Warning Alerts**: Respond within 1 hour
3. **Use Runbook**: Follow procedures in `docs/runbook.md`
4. **Escalation**: If unresolved in 2 hours, escalate to senior engineer

## Capacity Planning

### Growth Projections

**Current Load**:
- 1M records total
- 10,000 changes/day
- 100 GB data size

**6-Month Projection**:
- 10M records (+10x)
- 100,000 changes/day (+10x)
- 1 TB data size (+10x)

**Scaling Recommendations**:
- Add 2 ScyllaDB nodes (3 → 5 nodes)
- Add 1 Kafka broker (3 → 4 brokers)
- Increase partition count (8 → 16 per topic)
- Add 1 Kafka Connect worker (3 → 4 workers)
- Scale PostgreSQL vertically (16 → 32 cores, 64 → 128 GB RAM)

## Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Source DB | ScyllaDB | 5.2+ | NoSQL database with CDC |
| Target DB | PostgreSQL | 14+ | Relational data warehouse |
| Message Broker | Apache Kafka | 3.4+ | Event streaming |
| Schema Registry | Confluent Schema Registry | 7.4+ | Avro schema management |
| Source Connector | ScyllaDB CDC Connector | 1.x | CDC stream reader |
| Sink Connector | JDBC Sink Connector | 10.x | PostgreSQL writer |
| Metrics | Prometheus | 2.45+ | Metrics collection |
| Dashboards | Grafana | 10.0+ | Metrics visualization |
| Tracing | Jaeger | 1.47+ | Distributed tracing |
| Orchestration | Docker Compose | 2.x | Container orchestration |
| Reconciliation | Python | 3.11+ | Data consistency validation |
| Testing | pytest | 7.4+ | Unit/integration testing |

## Design Decisions

### 1. Why Kafka Connect over Custom Application?

**Pros**:
- Battle-tested, production-ready framework
- Built-in offset management (exactly-once semantics)
- Automatic fault tolerance and task rebalancing
- Rich connector ecosystem
- Schema Registry integration

**Cons**:
- Additional complexity (Kafka, Zookeeper, Schema Registry)
- Learning curve for configuration
- Resource overhead

**Decision**: Use Kafka Connect for reliability and ecosystem benefits

### 2. Why Avro over JSON?

**Pros**:
- Compact binary format (smaller messages)
- Schema evolution support
- Strong typing with validation
- Better performance for serialization/deserialization

**Cons**:
- Requires Schema Registry
- Less human-readable than JSON
- Additional complexity

**Decision**: Use Avro for production, JSON acceptable for development

### 3. Why Periodic Reconciliation?

**Pros**:
- Catches edge cases (connector failures, data corruption)
- Validates end-to-end data consistency
- Provides data quality metrics

**Cons**:
- Additional resource usage
- Potential for false positives

**Decision**: Run daily reconciliation for data quality assurance

### 4. Why Dead Letter Queue?

**Pros**:
- Prevents pipeline blocking on bad messages
- Preserves failed messages for analysis
- Allows manual replay after fixing issues

**Cons**:
- Additional storage required
- Needs monitoring and management

**Decision**: Use DLQ with alerting for proactive error handling

## References

- [ScyllaDB CDC Documentation](https://docs.scylladb.com/stable/using-scylla/cdc/cdc-intro.html)
- [Kafka Connect Documentation](https://kafka.apache.org/documentation/#connect)
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html)
- [Debezium Architecture](https://debezium.io/documentation/reference/stable/architecture.html)
- [PostgreSQL JDBC Sink Connector](https://docs.confluent.io/kafka-connect-jdbc/current/index.html)

---

**Document Version**: 1.0
**Last Updated**: 2025-12-09
**Authors**: CDC Pipeline Team
**Review Cycle**: Quarterly
