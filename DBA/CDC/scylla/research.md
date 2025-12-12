# Research: ScyllaDB to Postgres CDC Pipeline

**Date**: 2025-12-09
**Feature**: 001-scylla-pg-cdc
**Status**: Complete

## Executive Summary

This research document captures technology decisions, best practices, and architectural patterns for building a production-grade CDC pipeline from ScyllaDB to Postgres using open-source components. All decisions align with the project constitution's principles of exactly-once semantics, observability, and minimal custom code.

## Core Technology Stack

### Decision: Kafka Connect Framework

**Rationale**:
- Industry-standard distributed connector framework with proven CDC implementations
- Built-in exactly-once semantics support via Kafka transactions
- Native integration with Schema Registry for schema evolution
- Horizontal scalability through worker distribution
- Extensive connector ecosystem (Confluent Hub)
- REST API for management (though we'll wrap with CLI scripts per requirements)

**Alternatives Considered**:
- **Debezium**: Strong for database CDC but limited ScyllaDB support (primarily Cassandra connector)
- **Custom CDC reader**: Would violate "minimal custom code" requirement, high maintenance burden
- **Apache Flink CDC**: Powerful but adds complexity, steeper learning curve

**Selected Versions**:
- Kafka 3.6.1 (latest stable, required for improved exactly-once semantics)
- Kafka Connect 3.6.1 (bundled with Kafka)
- Confluent Platform 7.5.3 (for Schema Registry, compatible with Apache Kafka 3.6)

### Decision: Scylla CDC Source Connector (Confluent Hub)

**Rationale**:
- Official ScyllaDB CDC support via Scylla CDC Source Connector
- Reads from ScyllaDB CDC log tables automatically created per table
- Supports Avro schema generation from Scylla schema
- Handles table-level parallelism through Kafka Connect tasks
- Community-supported with active development

**Configuration Best Practices**:
```json
{
  "connector.class": "com.scylladb.cdc.kafka.connect.ScyllaSourceConnector",
  "scylla.name": "scylla-source",
  "scylla.table.names": "<keyspace>.<table>",
  "scylla.cluster.ip.addresses": "<vault-retrieved>",
  "scylla.user": "<vault-retrieved>",
  "scylla.password": "<vault-retrieved>",
  "tasks.max": "4",  // Per-table task parallelism
  "key.converter": "io.confluent.connect.avro.AvroConverter",
  "key.converter.schema.registry.url": "http://schema-registry:8081",
  "value.converter": "io.confluent.connect.avro.AvroConverter",
  "value.converter.schema.registry.url": "http://schema-registry:8081",
  "errors.tolerance": "none",  // Fail-fast for data integrity
  "errors.deadletterqueue.topic.name": "dlq-scylla-source",
  "errors.deadletterqueue.context.headers.enable": true
}
```

**Key Features**:
- Automatic CDC log consumption
- Per-partition ordering guarantees
- Offset management via Kafka Connect framework
- Schema extraction from ScyllaDB system tables

**Alternatives Considered**:
- **Cassandra Connector (Debezium)**: ScyllaDB compatible but doesn't leverage ScyllaDB-specific CDC optimizations
- **Custom Python reader**: Would require significant custom code, offset management complexity

### Decision: PostgreSQL JDBC Sink Connector (Confluent Hub)

**Rationale**:
- Industry-standard Kafka to JDBC sink implementation
- Supports UPSERT mode (INSERT + UPDATE on conflict) for idempotency
- Automatic table creation and schema evolution
- Batch writes for efficiency (configurable batch size)
- Transactions support for exactly-once delivery

**Configuration Best Practices**:
```json
{
  "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
  "topics": "<topic-pattern>",
  "connection.url": "<vault-retrieved>",
  "connection.user": "<vault-retrieved>",
  "connection.password": "<vault-retrieved>",
  "auto.create": "true",
  "auto.evolve": "true",
  "insert.mode": "upsert",
  "pk.mode": "record_key",
  "pk.fields": "<primary-key-fields>",
  "delete.enabled": "true",
  "batch.size": "3000",
  "errors.tolerance": "none",
  "errors.deadletterqueue.topic.name": "dlq-postgres-sink",
  "errors.deadletterqueue.context.headers.enable": true,
  "max.retries": "10",
  "retry.backoff.ms": "3000"
}
```

**Key Features**:
- UPSERT semantics prevent duplicate inserts
- Automatic DDL execution for schema changes
- Batch writes for throughput optimization
- Connection pooling built-in

**Alternatives Considered**:
- **Custom JDBC writer**: Violates minimal custom code principle
- **pg_dump/pg_restore approach**: Not real-time, lacks CDC event semantics

## Schema Management

### Decision: Kafka Schema Registry with Avro

**Rationale**:
- Centralized schema versioning and compatibility enforcement
- Avro provides compact binary serialization (smaller than JSON)
- Schema evolution support (add/remove fields with defaults)
- Backward/forward compatibility checks before schema registration
- Integrates natively with Kafka Connect converters

**Schema Registry Configuration**:
```properties
# Compatibility mode: BACKWARD (new schema can read old data)
compatibility.mode=BACKWARD

# Enable schema validation on write
schema.registry.url=http://schema-registry:8081
```

**Alternatives Considered**:
- **JSON with JSON Schema**: Less efficient serialization, weaker tooling support
- **Protobuf**: Excellent performance but less native Kafka Connect integration
- **No schema registry**: Risk of schema drift, no compatibility enforcement

## Observability Stack

### Decision: Prometheus + Grafana + Jaeger

**Rationale**:
- **Prometheus**: Industry standard for metrics, excellent Kafka/JMX support
- **Grafana**: Rich visualization, pre-built Kafka Connect dashboards available
- **Jaeger**: Distributed tracing for end-to-end event tracking

**Metrics Collection**:
- Kafka Connect exposes JMX metrics (connector lag, task status, error rates)
- Prometheus JMX Exporter agent scrapes Connect workers
- Custom Python reconciliation scripts emit metrics via Prometheus client library

**Key Metrics** (align with constitution Principle VII):
```yaml
# Lag metrics
kafka_connect_sink_connector_lag_seconds
kafka_connect_source_connector_last_poll_seconds_ago

# Throughput metrics
kafka_connect_connector_task_batch_size_avg
kafka_topics_messages_in_per_sec

# Error metrics
kafka_connect_connector_task_error_total
kafka_connect_dead_letter_queue_messages_total

# Health metrics
kafka_connect_connector_status  # 1=running, 0=failed
kafka_connect_task_status
```

**Grafana Dashboards**:
1. **CDC Pipeline Overview**: Lag, throughput, error rates across all connectors
2. **Connector Health**: Per-connector/task status, restart counts
3. **Schema Evolution**: Schema version changes, compatibility failures
4. **Reconciliation**: Discrepancy counts, repair success rates

**Jaeger Tracing Integration**:
- Correlation IDs injected at Scylla source connector
- Propagated through Kafka message headers
- Extracted at Postgres sink for end-to-end trace

**Alternatives Considered**:
- **ELK Stack**: Heavier weight, primarily log-focused vs metrics
- **DataDog/New Relic**: Commercial, violates open-source requirement
- **Custom metrics**: Reinventing the wheel, high maintenance

## Secrets Management

### Decision: HashiCorp Vault

**Rationale**:
- Industry-standard secrets management
- Dynamic database credentials with automatic rotation support
- Audit logging of secret access
- KV v2 engine for versioned secrets
- CLI and HTTP API for script integration

**Vault Setup**:
```bash
# Enable KV v2 engine
vault secrets enable -path=cdc kv-v2

# Store database credentials
vault kv put cdc/scylla username=scylla_cdc password=<generated>
vault kv put cdc/postgres username=pg_writer password=<generated>

# Create policy for CDC pipeline access
vault policy write cdc-pipeline - <<EOF
path "cdc/data/scylla" { capabilities = ["read"] }
path "cdc/data/postgres" { capabilities = ["read"] }
EOF

# AppRole authentication for scripts
vault auth enable approle
```

**Integration with Connectors**:
- Bash wrapper scripts fetch credentials from Vault before deploying connectors
- Credentials never hardcoded in connector JSON files
- Template files use `<vault-retrieved>` placeholders

**Example Credential Retrieval**:
```bash
#!/bin/bash
# scripts/deploy-connector.sh

# Fetch credentials from Vault
SCYLLA_USER=$(vault kv get -field=username cdc/scylla)
SCYLLA_PASS=$(vault kv get -field=password cdc/scylla)

# Substitute into connector config template
sed -e "s/<vault-scylla-user>/$SCYLLA_USER/" \
    -e "s/<vault-scylla-pass>/$SCYLLA_PASS/" \
    configs/connectors/scylla-source.json > /tmp/scylla-source.json

# Deploy via Kafka Connect REST API
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @/tmp/scylla-source.json

rm /tmp/scylla-source.json  # Clean up temp file with credentials
```

**Alternatives Considered**:
- **Environment variables**: No audit trail, harder rotation, less secure
- **AWS Secrets Manager**: Cloud-specific, not open-source
- **Kubernetes Secrets**: Requires K8s, base64 encoding not true encryption

## Reconciliation Strategy

### Decision: Scheduled + On-Demand Python Script

**Rationale**:
- Reconciliation not natively supported by Kafka Connect
- Custom Python script provides flexibility for business logic
- Stateless design enables scheduled cron execution + manual triggers
- Checkpointing via Postgres table for resumable reconciliation

**Reconciliation Algorithm**:
1. **Snapshot Phase**:
   - Query ScyllaDB for current table state (paginated, 10k rows per batch)
   - Query Postgres for corresponding rows
   - Compare hashes or column values
   - Store discrepancies in `reconciliation_log` table

2. **Repair Phase**:
   - For missing rows: INSERT into Postgres
   - For mismatched rows: UPDATE Postgres with ScyllaDB values
   - For extra rows: Log warning (potential delete not captured)
   - Record repairs in `reconciliation_repairs` table

3. **Checkpoint Phase**:
   - Store last reconciled primary key in `reconciliation_checkpoints` table
   - On restart, resume from last checkpoint

**Scheduling**:
```bash
# Cron entry for daily reconciliation at 2 AM
0 2 * * * /opt/cdc/scripts/schedule-reconciliation.sh >> /var/log/cdc/reconciliation.log 2>&1
```

**On-Demand Execution**:
```bash
# Manual reconciliation trigger
./scripts/reconcile.py --table keyspace.users --mode full
./scripts/reconcile.py --table keyspace.orders --mode incremental --since "2025-12-08"
```

**Alternatives Considered**:
- **Real-time reconciliation**: Too expensive, unnecessary with exactly-once semantics
- **Third-party tools (dbt, Great Expectations)**: Overkill for CDC, not designed for bidirectional comparison
- **Database triggers**: Complex cross-database coordination, performance impact

## Docker Compose Local Environment

### Decision: Multi-Service Composition with Profiles

**Rationale**:
- Docker Compose provides declarative multi-container orchestration
- Profiles enable selective service startup (e.g., skip monitoring for fast tests)
- Volumes persist data across restarts for iterative development
- Health checks ensure dependency ordering (e.g., Kafka waits for Zookeeper)

**Service Architecture**:
```yaml
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.3
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.5.3
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      # Enable exactly-once semantics
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1

  schema-registry:
    image: confluentinc/cp-schema-registry:7.5.3
    depends_on:
      - kafka
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:9092

  kafka-connect:
    build: ./docker/kafka-connect
    depends_on:
      - kafka
      - schema-registry
      - scylla
      - postgres
    ports:
      - "8083:8083"
    environment:
      CONNECT_BOOTSTRAP_SERVERS: kafka:9092
      CONNECT_KEY_CONVERTER: io.confluent.connect.avro.AvroConverter
      CONNECT_VALUE_CONVERTER: io.confluent.connect.avro.AvroConverter
      CONNECT_EXACTLY_ONCE_SOURCE_SUPPORT: enabled
      CONNECT_GROUP_ID: cdc-connect-cluster

  scylla:
    image: scylladb/scylla:5.4.2
    ports:
      - "9042:9042"
    volumes:
      - ./docker/scylla/init.cql:/docker-entrypoint-initdb.d/init.cql
    command: --smp 1 --memory 750M

  postgres:
    image: postgres:15.5
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: warehouse
    volumes:
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql

  vault:
    image: hashicorp/vault:1.15.4
    ports:
      - "8200:8200"
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: dev-token
      VAULT_DEV_LISTEN_ADDRESS: 0.0.0.0:8200
    cap_add:
      - IPC_LOCK

  prometheus:
    image: prom/prometheus:v2.48.1
    profiles: ["monitoring"]
    ports:
      - "9090:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana:10.2.3
    profiles: ["monitoring"]
    ports:
      - "3000:3000"
    volumes:
      - ./docker/grafana/datasources.yml:/etc/grafana/provisioning/datasources/datasources.yml
      - ./docker/grafana/dashboards:/etc/grafana/provisioning/dashboards

  jaeger:
    image: jaegertracing/all-in-one:1.51.0
    profiles: ["monitoring"]
    ports:
      - "16686:16686"  # UI
      - "14268:14268"  # Collector HTTP
```

**Usage Patterns**:
```bash
# Start core pipeline (no monitoring)
docker-compose up -d

# Start with full observability stack
docker-compose --profile monitoring up -d

# Run integration tests
docker-compose -f docker-compose.yml -f docker-compose.test.yml up --abort-on-container-exit
```

**Alternatives Considered**:
- **Kubernetes (Minikube/Kind)**: Overkill for local dev, slower startup
- **Individual docker run commands**: Hard to manage dependencies, no orchestration
- **Vagrant VMs**: Heavier resource footprint, slower than containers

## Best Practices

### Exactly-Once Semantics Configuration

**Kafka Producer Settings** (Scylla Source Connector):
```properties
enable.idempotence=true
transactional.id=scylla-source-<table>
acks=all
max.in.flight.requests.per.connection=1
```

**Kafka Consumer Settings** (Postgres Sink Connector):
```properties
isolation.level=read_committed
enable.auto.commit=false
```

**Kafka Connect Framework**:
```properties
exactly.once.source.support=enabled
consumer.isolation.level=read_committed
```

### Schema Evolution Guidelines

**Compatible Changes** (automatic):
- Add column with default value
- Remove column (sink ignores missing fields)
- Widen column type (INT → BIGINT)

**Incompatible Changes** (require manual intervention):
- Change column type incompatibly (STRING → INT)
- Remove column without default (source sends, sink expects)
- Rename column (treated as remove + add)

**Migration Process**:
1. Test schema change in dev environment
2. Verify Schema Registry compatibility check passes
3. Apply schema change to ScyllaDB
4. Monitor connector for schema evolution errors
5. If errors, rollback schema change and adjust strategy

### Error Handling Strategy

**Transient Errors** (retry):
- Network timeouts
- Database connection failures
- Temporary resource exhaustion

**Permanent Errors** (dead letter queue):
- Schema incompatibility
- Constraint violations (e.g., foreign key)
- Malformed data

**DLQ Monitoring**:
```bash
# Check DLQ message count
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic dlq-scylla-source \
  --from-beginning --max-messages 10

# Alert if DLQ non-empty
prometheus_alert:
  alert: DeadLetterQueueNotEmpty
  expr: kafka_topics_messages_in_total{topic=~"dlq-.*"} > 0
  for: 5m
```

### Performance Tuning

**Kafka Connect Worker**:
- CPU: 4+ cores per worker
- Memory: 4GB+ heap (set `KAFKA_HEAP_OPTS=-Xmx4g -Xms4g`)
- Tasks: 4-8 per connector (tune based on source parallelism)

**Kafka Topics**:
- Partitions: Match ScyllaDB table partition count or 2x CPU cores
- Replication factor: 3 for production (1 for dev)
- Retention: 24+ hours (enough for recovery window)

**Postgres Sink Batching**:
- `batch.size=3000`: Balance latency vs throughput
- `linger.ms=100`: Allow batching within 100ms window
- Monitor lag to tune batch size upward

### Testing Pyramid

**Unit Tests** (fast, TDD):
- Reconciliation comparer logic
- Schema validator functions
- Vault client credential retrieval
- Correlation ID propagation

**Integration Tests** (moderate, post-implementation):
- End-to-end event flow (Scylla → Kafka → Postgres)
- Schema evolution scenarios
- Failure recovery (restart mid-processing)
- Dead letter queue routing

**Contract Tests** (moderate, post-implementation):
- Scylla connector produces valid Avro
- Postgres sink consumes expected format
- Schema Registry compatibility enforcement

**Chaos Tests** (slow, weekly):
- Network partition simulation (Toxiproxy)
- Process crashes (kill -9 Kafka Connect)
- Database unavailability (stop Postgres mid-processing)

## References

- [Kafka Connect Documentation](https://docs.confluent.io/platform/current/connect/index.html)
- [Scylla CDC Source Connector](https://github.com/scylladb/scylla-cdc-source-connector)
- [PostgreSQL JDBC Sink Connector](https://docs.confluent.io/kafka-connectors/jdbc/current/sink-connector/index.html)
- [HashiCorp Vault Best Practices](https://developer.hashicorp.com/vault/tutorials/operations/production-hardening)
- [Prometheus JMX Exporter](https://github.com/prometheus/jmx_exporter)
- [Kafka Exactly-Once Semantics](https://www.confluent.io/blog/exactly-once-semantics-are-possible-heres-how-apache-kafka-does-it/)
