# CDC Pipeline Throughput Analysis Guide

This guide provides commands and procedures for analyzing data throughput across each component of the ScyllaDB CDC pipeline.

## Table of Contents

1. [Pipeline Architecture Overview](#pipeline-architecture-overview)
2. [Component-by-Component Analysis](#component-by-component-analysis)
3. [End-to-End Throughput Verification](#end-to-end-throughput-verification)
4. [Troubleshooting Bottlenecks](#troubleshooting-bottlenecks)
5. [Performance Baselines](#performance-baselines)

---

## Pipeline Architecture Overview

The CDC pipeline consists of the following components:

```
ScyllaDB (Source)
    ↓ CDC logs
Scylla CDC Source Connector (Debezium)
    ↓ Kafka topics
Kafka Broker
    ↓ Consumer groups
PostgreSQL JDBC Sink Connector
    ↓ JDBC writes
PostgreSQL (Destination)
```

---

## Component-by-Component Analysis

### 1. ScyllaDB CDC Log Analysis

#### Check CDC-enabled tables
```bash
docker exec scylla-node1 cqlsh -e "SELECT table_name FROM system_schema.tables WHERE keyspace_name = 'app_data' AND extensions LIKE '%cdc%';"
```

#### Count CDC log entries for a specific table
```bash
docker exec scylla-node1 cqlsh -e "SELECT COUNT(*) FROM app_data.users_scylla_cdc_log;"
```

#### Check CDC log size and entries for all tables
```bash
for table in users orders order_items products inventory_transactions; do
  echo "=== $table CDC log ==="
  docker exec scylla-node1 cqlsh -e "SELECT COUNT(*) FROM app_data.${table}_scylla_cdc_log;"
done
```

#### View recent CDC log entries (sample)
```bash
docker exec scylla-node1 cqlsh -e "SELECT cdc\$time, cdc\$operation FROM app_data.users_scylla_cdc_log LIMIT 10;"
```

#### Check CDC generations
```bash
docker exec scylla-node1 cqlsh -e "SELECT * FROM app_data.cdc_metadata;"
```

---

### 2. Scylla CDC Source Connector Analysis

#### Check connector status
```bash
curl -s http://localhost:8083/connectors/scylla-cdc-source/status | jq '.'
```

#### Get connector metrics
```bash
curl -s http://localhost:8083/connectors/scylla-cdc-source/status | jq '{
  connector_state: .connector.state,
  tasks: [.tasks[] | {id: .id, state: .state, worker_id: .worker_id}]
}'
```

#### Check connector configuration
```bash
curl -s http://localhost:8083/connectors/scylla-cdc-source/config | jq '.'
```

#### View connector tasks in detail
```bash
curl -s http://localhost:8083/connectors/scylla-cdc-source/tasks | jq '.'
```

---

### 3. Kafka Broker Analysis

#### List all CDC-related topics
```bash
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list | grep -E '(scylla-cluster|heartbeat)'
```

#### Check topic message counts
```bash
for topic in $(docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list | grep 'scylla-cluster.app_data'); do
  echo "=== $topic ==="
  docker exec kafka kafka-run-class kafka.tools.GetOffsetShell \
    --broker-list localhost:9092 \
    --topic "$topic" \
    --time -1 | awk -F: '{sum += $3} END {print "Total messages: " sum}'
done
```

#### Describe a specific topic
```bash
docker exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --describe --topic scylla-cluster.app_data.users
```

#### Check consumer group lag for sink connector
```bash
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group connect-postgres-jdbc-sink \
  --describe
```

**Understanding the output:**
- `CURRENT-OFFSET`: Messages consumed by the sink connector
- `LOG-END-OFFSET`: Total messages in the topic
- `LAG`: Messages waiting to be consumed (should be low/zero for healthy pipeline)

#### Detailed lag analysis with all metrics
```bash
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group connect-postgres-jdbc-sink \
  --describe --verbose
```

#### Monitor consumer lag in real-time
```bash
watch -n 2 'docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group connect-postgres-jdbc-sink --describe'
```

---

### 4. PostgreSQL JDBC Sink Connector Analysis

#### Check connector status
```bash
curl -s http://localhost:8083/connectors/postgres-jdbc-sink/status | jq '.'
```

#### Get detailed task status
```bash
curl -s http://localhost:8083/connectors/postgres-jdbc-sink/status | jq '{
  connector: .connector.state,
  tasks: [.tasks[] | {
    id: .id,
    state: .state,
    worker: .worker_id,
    trace: .trace
  }]
}'
```

#### Check for connector errors
```bash
curl -s http://localhost:8083/connectors/postgres-jdbc-sink/status | jq '.tasks[] | select(.state == "FAILED")'
```

#### View connector configuration
```bash
curl -s http://localhost:8083/connectors/postgres-jdbc-sink/config | jq '{
  batch_size: .["batch.size"],
  max_retries: .["max.retries"],
  tasks: .["tasks.max"],
  insert_mode: .["insert.mode"]
}'
```

---

### 5. PostgreSQL Destination Analysis

#### Count replicated records in all tables
```bash
psql -h localhost -p 5432 -U postgres -d warehouse -c "
SELECT
  schemaname,
  tablename,
  n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'cdc_data'
ORDER BY tablename;
"
```

#### Check table sizes
```bash
psql -h localhost -p 5432 -U postgres -d warehouse -c "
SELECT
  schemaname || '.' || tablename as table,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'cdc_data'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

#### Check recent activity on CDC tables
```bash
psql -h localhost -p 5432 -U postgres -d warehouse -c "
SELECT
  schemaname || '.' || tablename as table,
  n_tup_ins as inserts,
  n_tup_upd as updates,
  n_tup_del as deletes,
  last_autovacuum,
  last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname = 'cdc_data'
ORDER BY tablename;
"
```

#### Monitor active connections and queries
```bash
psql -h localhost -p 5432 -U postgres -d warehouse -c "
SELECT
  pid,
  usename,
  application_name,
  client_addr,
  state,
  query_start,
  LEFT(query, 100) as query
FROM pg_stat_activity
WHERE datname = 'warehouse'
  AND application_name LIKE '%kafka%'
ORDER BY query_start DESC;
"
```

---

## End-to-End Throughput Verification

### Complete Pipeline Health Check Script

```bash
#!/bin/bash
# Save as: check_pipeline_health.sh

echo "=================================="
echo "CDC PIPELINE HEALTH CHECK"
echo "=================================="
echo ""

echo "[1/5] ScyllaDB CDC Logs"
echo "------------------------"
docker exec scylla-node1 cqlsh -e "SELECT COUNT(*) FROM app_data.users_scylla_cdc_log;" 2>/dev/null | grep -A1 count

echo ""
echo "[2/5] Scylla CDC Source Connector"
echo "----------------------------------"
curl -s http://localhost:8083/connectors/scylla-cdc-source/status | jq -r '.connector.state'

echo ""
echo "[3/5] Kafka Topics"
echo "------------------"
docker exec kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic scylla-cluster.app_data.users \
  --time -1 2>/dev/null | awk -F: '{sum += $3} END {print "Total messages: " sum}'

echo ""
echo "[4/5] Consumer Lag"
echo "------------------"
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group connect-postgres-jdbc-sink \
  --describe 2>/dev/null | grep -E '(TOPIC|scylla-cluster.app_data.users)' | head -5

echo ""
echo "[5/5] PostgreSQL Sink Connector"
echo "--------------------------------"
curl -s http://localhost:8083/connectors/postgres-jdbc-sink/status | jq -r '.connector.state'

echo ""
echo "[6/6] PostgreSQL Record Counts"
echo "-------------------------------"
psql -h localhost -p 5432 -U postgres -d warehouse -t -c "
SELECT tablename || ': ' || n_live_tup
FROM pg_stat_user_tables
WHERE schemaname = 'cdc_data' AND tablename = 'users';
"
```

Make it executable and run:
```bash
chmod +x check_pipeline_health.sh
./check_pipeline_health.sh
```

---

### Replication Latency Test

This test measures end-to-end latency from ScyllaDB insert to PostgreSQL visibility.

```bash
#!/bin/bash
# Save as: test_replication_latency.sh

USER_ID=$(uuidgen)
START_TIME=$(date +%s)

echo "Inserting test record with user_id: $USER_ID"
docker exec scylla-node1 cqlsh -e "
INSERT INTO app_data.users (user_id, username, email, first_name, last_name, created_at, updated_at, status)
VALUES ($USER_ID, 'latency_test', 'test@example.com', 'Test', 'User', toTimestamp(now()), toTimestamp(now()), 'active');
"

echo "Waiting for replication to PostgreSQL..."
TIMEOUT=120
ELAPSED=0

while [ $ELAPSED -lt $TIMEOUT ]; do
  COUNT=$(psql -h localhost -p 5432 -U postgres -d warehouse -t -c "
    SELECT COUNT(*) FROM cdc_data.users WHERE user_id = '$USER_ID';
  " 2>/dev/null | tr -d ' ')

  if [ "$COUNT" = "1" ]; then
    END_TIME=$(date +%s)
    LATENCY=$((END_TIME - START_TIME))
    echo "✓ Replication successful!"
    echo "✓ End-to-end latency: ${LATENCY} seconds"
    exit 0
  fi

  sleep 2
  ELAPSED=$((ELAPSED + 2))
  echo -n "."
done

echo ""
echo "✗ Replication timed out after ${TIMEOUT} seconds"
exit 1
```

---

## Troubleshooting Bottlenecks

### Identify Slow Components

#### 1. Check if CDC logs are being generated
```bash
# Insert a test record
docker exec scylla-node1 cqlsh -e "
INSERT INTO app_data.users (user_id, username, email, first_name, last_name, created_at, updated_at, status)
VALUES (uuid(), 'bottleneck_test', 'test@example.com', 'Test', 'User', toTimestamp(now()), toTimestamp(now()), 'active');
"

# Verify CDC log entry appears (should be immediate)
sleep 1
docker exec scylla-node1 cqlsh -e "
SELECT COUNT(*) FROM app_data.users_scylla_cdc_log WHERE cdc\$time > dateOf(now()) - 10000;
"
```

**Expected:** CDC log entry appears within 1 second

---

#### 2. Check if source connector is reading CDC logs
```bash
# Before: Note current Kafka topic offset
docker exec kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic scylla-cluster.app_data.users \
  --time -1 2>/dev/null | awk -F: '{sum += $3} END {print "Before: " sum}'

# Insert test record in ScyllaDB
docker exec scylla-node1 cqlsh -e "
INSERT INTO app_data.users (user_id, username, email, first_name, last_name, created_at, updated_at, status)
VALUES (uuid(), 'source_test', 'test@example.com', 'Test', 'User', toTimestamp(now()), toTimestamp(now()), 'active');
"

# After: Check if offset increased (wait 5-10 seconds)
sleep 10
docker exec kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic scylla-cluster.app_data.users \
  --time -1 2>/dev/null | awk -F: '{sum += $3} END {print "After:  " sum}'
```

**Expected:** Offset increases within 5-10 seconds (typically 3-6 messages due to CDC amplification)

---

#### 3. Check if sink connector is consuming from Kafka
```bash
# Check lag before and after
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group connect-postgres-jdbc-sink \
  --describe 2>/dev/null | grep scylla-cluster.app_data.users
```

**Expected:** LAG should decrease to 0 within 30 seconds

---

#### 4. Check if data arrives in PostgreSQL
```bash
# Query for recent records (inserted in last minute)
psql -h localhost -p 5432 -U postgres -d warehouse -c "
SELECT username_value, email_value, status_value
FROM cdc_data.users
WHERE username_value LIKE '%test%'
ORDER BY user_id DESC
LIMIT 5;
"
```

**Expected:** Data appears within 45-90 seconds of ScyllaDB insert

---

### Common Bottleneck Patterns

#### Pattern 1: High Kafka Lag
```bash
# Symptom: LAG column shows large numbers
docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group connect-postgres-jdbc-sink \
  --describe | grep -E 'LAG|TOPIC'
```

**Diagnosis:**
- Sink connector is slow or failed
- PostgreSQL is slow to accept writes
- Network issues between Kafka and PostgreSQL

**Resolution:**
```bash
# Check sink connector status
curl -s http://localhost:8083/connectors/postgres-jdbc-sink/status | jq '.tasks[] | select(.state != "RUNNING")'

# Restart sink connector if needed
curl -X POST http://localhost:8083/connectors/postgres-jdbc-sink/restart

# Increase batch size if throughput is low
curl -X PUT http://localhost:8083/connectors/postgres-jdbc-sink/config \
  -H "Content-Type: application/json" \
  -d '{"batch.size": "5000"}'
```

---

#### Pattern 2: Source Connector Not Producing
```bash
# Symptom: No messages in Kafka topics despite CDC logs
docker exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --describe --topic scylla-cluster.app_data.users | grep PartitionCount
```

**Diagnosis:**
- Source connector is failed or paused
- CDC not enabled on tables
- Network issues between ScyllaDB and Kafka

**Resolution:**
```bash
# Check source connector
curl -s http://localhost:8083/connectors/scylla-cdc-source/status | jq '.'

# Restart source connector
curl -X POST http://localhost:8083/connectors/scylla-cdc-source/restart
```

---

#### Pattern 3: PostgreSQL Lock Contention
```bash
# Symptom: Slow replication, sink connector shows errors
psql -h localhost -p 5432 -U postgres -d warehouse -c "
SELECT
  locktype,
  relation::regclass,
  mode,
  granted,
  pid,
  query
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT granted
  AND relation::regclass::text LIKE 'cdc_data%';
"
```

**Resolution:**
- Investigate long-running queries
- Check for missing indexes on primary keys
- Verify UPSERT mode is working correctly

---

## Performance Baselines

### Expected Throughput Rates

| Stage | Metric | Healthy Range | Warning Threshold |
|-------|--------|---------------|-------------------|
| **ScyllaDB CDC Log** | Write latency | < 1 second | > 5 seconds |
| **Source Connector** | Kafka publish rate | 3-10 msg/write | > 20 msg/write |
| **Kafka Consumer Lag** | Messages behind | 0-50 | > 500 |
| **Sink Connector** | Batch processing | 1000-3000 msg/batch | < 100 msg/batch |
| **End-to-End Latency** | Insert to visible | 3-45 seconds | > 90 seconds |
| **Replication Success** | % of records | 100% | < 99% |

### Message Amplification

CDC events generate multiple Kafka messages per database operation:

- **INSERT:** 2-3 messages (pre-image, post-image, metadata)
- **UPDATE:** 3-4 messages (pre-image, post-image, delta, metadata)
- **DELETE:** 2-3 messages (pre-image, tombstone)

**Normal amplification factor:** 6-8x messages per operation

Example:
```
1 INSERT in ScyllaDB → 6-8 messages in Kafka → 1 row in PostgreSQL
```

---

### Monitoring Commands Summary

```bash
# Quick health check one-liner
echo "ScyllaDB CDC: $(docker exec scylla-node1 cqlsh -e 'SELECT COUNT(*) FROM app_data.users_scylla_cdc_log;' 2>/dev/null | grep -A1 count | tail -1 | tr -d ' ') | \
Kafka Messages: $(docker exec kafka kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic scylla-cluster.app_data.users --time -1 2>/dev/null | awk -F: '{sum += $3} END {print sum}') | \
Kafka Lag: $(docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group connect-postgres-jdbc-sink --describe 2>/dev/null | grep scylla-cluster.app_data.users | awk '{print $5}' | head -1) | \
PostgreSQL Rows: $(psql -h localhost -p 5432 -U postgres -d warehouse -t -c 'SELECT n_live_tup FROM pg_stat_user_tables WHERE schemaname='\''cdc_data'\'' AND tablename='\''users'\'';' 2>/dev/null | tr -d ' ')"
```

---

## Advanced Diagnostics

### Check Kafka Connect Metrics

```bash
# Get JMX metrics (if enabled)
docker exec kafka-connect curl -s localhost:9999/metrics | grep -E '(kafka.consumer|kafka.producer)'
```

### Check Schema Registry Performance

```bash
# List all schemas
curl -s http://localhost:8081/subjects | jq '.'

# Get schema for specific topic
curl -s http://localhost:8081/subjects/scylla-cluster.app_data.users-value/versions/latest | jq '.'
```

### Deep Dive: Kafka Topic Analysis

```bash
# Analyze message distribution across partitions
docker exec kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic scylla-cluster.app_data.users \
  --time -1 2>/dev/null
```

### PostgreSQL Performance Tuning Check

```bash
psql -h localhost -p 5432 -U postgres -d warehouse -c "
SELECT
  name,
  setting,
  unit,
  short_desc
FROM pg_settings
WHERE name IN (
  'shared_buffers',
  'work_mem',
  'maintenance_work_mem',
  'max_connections',
  'effective_cache_size'
);
"
```

---

## Automated Monitoring Setup

### Create a Monitoring Dashboard Script

```bash
#!/bin/bash
# Save as: monitor_dashboard.sh

while true; do
  clear
  echo "╔════════════════════════════════════════════════════════════╗"
  echo "║          CDC PIPELINE MONITORING DASHBOARD                 ║"
  echo "╚════════════════════════════════════════════════════════════╝"
  echo ""

  # ScyllaDB
  CDC_COUNT=$(docker exec scylla-node1 cqlsh -e "SELECT COUNT(*) FROM app_data.users_scylla_cdc_log;" 2>/dev/null | grep -A1 count | tail -1 | tr -d ' ')
  echo "📊 ScyllaDB CDC Log Entries: $CDC_COUNT"

  # Kafka
  KAFKA_MSGS=$(docker exec kafka kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic scylla-cluster.app_data.users --time -1 2>/dev/null | awk -F: '{sum += $3} END {print sum}')
  echo "📨 Kafka Messages (users topic): $KAFKA_MSGS"

  # Consumer Lag
  LAG=$(docker exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group connect-postgres-jdbc-sink --describe 2>/dev/null | grep scylla-cluster.app_data.users | head -1 | awk '{print $5}')
  echo "⏱️  Consumer Lag: $LAG"

  # PostgreSQL
  PG_COUNT=$(psql -h localhost -p 5432 -U postgres -d warehouse -t -c "SELECT n_live_tup FROM pg_stat_user_tables WHERE schemaname='cdc_data' AND tablename='users';" 2>/dev/null | tr -d ' ')
  echo "💾 PostgreSQL Rows: $PG_COUNT"

  # Connectors
  SOURCE_STATE=$(curl -s http://localhost:8083/connectors/scylla-cdc-source/status 2>/dev/null | jq -r '.connector.state')
  SINK_STATE=$(curl -s http://localhost:8083/connectors/postgres-jdbc-sink/status 2>/dev/null | jq -r '.connector.state')
  echo ""
  echo "🔌 Source Connector: $SOURCE_STATE"
  echo "🔌 Sink Connector: $SINK_STATE"

  echo ""
  echo "Last updated: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "Press Ctrl+C to exit"

  sleep 5
done
```

Make it executable:
```bash
chmod +x monitor_dashboard.sh
./monitor_dashboard.sh
```

---

## Conclusion

Use this guide to:
1. Verify each component is processing data
2. Measure throughput at each stage
3. Identify bottlenecks in the pipeline
4. Establish performance baselines
5. Troubleshoot replication issues

For test-specific throughput issues, see [Contract Test Troubleshooting Guide](contract_test_troubleshooting.md).
