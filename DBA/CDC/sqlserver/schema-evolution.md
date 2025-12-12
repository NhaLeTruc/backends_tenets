# Schema Evolution Guide: CDC Pipeline

Complete guide for handling schema changes in the SQL Server to PostgreSQL CDC pipeline.

## Table of Contents

1. [Overview](#overview)
2. [Supported Schema Changes](#supported-schema-changes)
3. [Configuration](#configuration)
4. [Handling Schema Changes](#handling-schema-changes)
5. [Schema Registry](#schema-registry)
6. [Dead Letter Queue](#dead-letter-queue)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The CDC pipeline is configured to handle schema evolution automatically where possible, while routing incompatible changes to a Dead Letter Queue (DLQ) for manual review.

### Schema Evolution Strategy

```
SQL Server Schema Change
         ↓
Debezium Detects Change
         ↓
    Schema Registry
    (Avro Schema)
         ↓
   JDBC Sink Connector
         ↓
   ┌─────┴─────┐
   │           │
   ↓           ↓
Compatible   Incompatible
   ↓           ↓
auto.evolve  Dead Letter
PostgreSQL    Queue
```

### Key Features

- **Automatic Column Addition**: New columns added automatically with `auto.evolve=true`
- **Schema Change Events**: Debezium emits schema change events to dedicated topic
- **Avro Schema Evolution**: Schema Registry tracks schema versions
- **Dead Letter Queue**: Failed records route to DLQ for investigation
- **Monitoring**: Prometheus alerts for schema changes and DLQ growth

---

## Supported Schema Changes

### Automatically Handled (Forward Compatible)

These changes are handled automatically by the pipeline:

#### 1. ADD COLUMN (Nullable)

**SQL Server**:
```sql
ALTER TABLE dbo.customers
ADD phone VARCHAR(20) NULL;
```

**Result**: Column automatically added to PostgreSQL table with `auto.evolve=true`.

**Requirements**:
- New column must be nullable OR have a default value
- Column type must be compatible between SQL Server and PostgreSQL

#### 2. ADD COLUMN (With Default)

**SQL Server**:
```sql
ALTER TABLE dbo.customers
ADD status VARCHAR(20) NOT NULL DEFAULT 'active';
```

**Result**: Column added with default value applied to existing rows.

### Manual Handling Required

These changes require manual intervention:

#### 1. DROP COLUMN

**SQL Server**:
```sql
ALTER TABLE dbo.customers
DROP COLUMN middle_name;
```

**Result**: Column remains in PostgreSQL (safety feature). New inserts will have NULL values.

**Action**: Manually drop column in PostgreSQL when ready:
```sql
ALTER TABLE customers DROP COLUMN middle_name;
```

#### 2. RENAME COLUMN

**SQL Server**:
```sql
EXEC sp_rename 'dbo.customers.email', 'email_address', 'COLUMN';
```

**Result**: Treated as DROP old column + ADD new column.

**Action**: Manually rename in PostgreSQL:
```sql
ALTER TABLE customers RENAME COLUMN email TO email_address;
```

#### 3. ALTER COLUMN TYPE (Incompatible)

**SQL Server**:
```sql
ALTER TABLE dbo.customers
ALTER COLUMN age VARCHAR(10);  -- was INT
```

**Result**: May route to DLQ if types are incompatible.

**Action**: Review DLQ, manually migrate data, update schema.

#### 4. ADD NOT NULL Constraint (No Default)

**SQL Server**:
```sql
ALTER TABLE dbo.customers
ADD city VARCHAR(100) NOT NULL;  -- No default!
```

**Result**: Existing records cannot satisfy constraint, route to DLQ.

**Action**: Add default value or manually populate:
```sql
-- Fix in SQL Server
ALTER TABLE dbo.customers
ADD city VARCHAR(100) NOT NULL DEFAULT 'Unknown';
```

---

## Configuration

### Debezium Source Connector

Schema change detection is enabled in `docker/configs/debezium/sqlserver-source.json`:

```json
{
  "include.schema.changes": "true",
  "provide.transaction.metadata": "true",
  "schema.history.internal.kafka.topic": "schema-changes.warehouse_source"
}
```

### JDBC Sink Connector

Auto-evolution is enabled in `docker/configs/kafka-connect/postgresql-sink.json`:

```json
{
  "auto.create": "false",
  "auto.evolve": "true",
  "errors.tolerance": "all",
  "errors.deadletterqueue.topic.name": "dlq-postgresql-sink"
}
```

### Schema Registry

Avro schemas are automatically registered and versioned:
- **URL**: http://localhost:8081
- **Compatibility**: BACKWARD (default)
- **Schemas**: One per table (key and value)

---

## Handling Schema Changes

### Step-by-Step Process

#### 1. Plan the Change

Before making schema changes:

```bash
# Check current schema in both databases
docker exec cdc-sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'YourStrong!Passw0rd' \
  -d warehouse_source -Q "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'customers'"

docker exec cdc-postgres psql -U postgres -d warehouse_target \
  -c "\d+ customers"
```

#### 2. Make the Change in SQL Server

```sql
-- Example: Add new column
ALTER TABLE dbo.customers
ADD loyalty_points INT NULL;
```

#### 3. Monitor Schema Change Detection

```bash
# Check schema change topic
docker exec cdc-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic schema-changes.warehouse_source \
  --from-beginning --max-messages 10

# Check Prometheus for schema change events
curl 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=kafka_log_log_size{topic="schema-changes.warehouse_source"}'
```

#### 4. Verify PostgreSQL Schema Updated

```bash
# Wait 30-60 seconds for auto.evolve to process
sleep 60

# Check PostgreSQL schema
docker exec cdc-postgres psql -U postgres -d warehouse_target \
  -c "\d+ customers"
```

#### 5. Test Data Replication

```sql
-- Insert test data with new column
INSERT INTO dbo.customers (name, email, loyalty_points)
VALUES ('Test User', 'test@example.com', 100);

-- Verify in PostgreSQL (wait 5-10 seconds)
SELECT name, email, loyalty_points FROM customers WHERE name = 'Test User';
```

### Monitoring Schema Changes

**Via Grafana**:
1. Open http://localhost:3000
2. Navigate to "CDC Pipeline Overview"
3. Check "Schema Changes" panel (if configured)

**Via Prometheus**:
```bash
# Schema change topic size
curl -s 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=kafka_log_log_size{topic="schema-changes.warehouse_source"}'

# Rate of schema changes
curl -s 'http://localhost:9090/api/v1/query' \
  --data-urlencode 'query=rate(kafka_log_log_size{topic="schema-changes.warehouse_source"}[1h])'
```

**Via monitor.sh**:
```bash
# Check for alerts
./scripts/bash/monitor.sh alerts | grep -i schema
```

---

## Schema Registry

### Viewing Schemas

**List all subjects**:
```bash
curl http://localhost:8081/subjects
```

**Get latest schema version**:
```bash
curl http://localhost:8081/subjects/sqlserver.warehouse_source.dbo.customers-value/versions/latest | jq .
```

**Get schema by version**:
```bash
curl http://localhost:8081/subjects/sqlserver.warehouse_source.dbo.customers-value/versions/1 | jq .
```

### Schema Compatibility

The pipeline uses **BACKWARD** compatibility by default:
- New schema can read old data
- Safe to add optional fields
- Cannot remove required fields

**Check compatibility**:
```bash
# Test if new schema is compatible
curl -X POST http://localhost:8081/compatibility/subjects/sqlserver.warehouse_source.dbo.customers-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "{\"type\":\"record\",\"name\":\"Customer\",\"fields\":[{\"name\":\"id\",\"type\":\"int\"},{\"name\":\"name\",\"type\":\"string\"}]}"}'
```

### Schema Evolution History

View all schema versions:
```bash
# List versions
curl http://localhost:8081/subjects/sqlserver.warehouse_source.dbo.customers-value/versions

# Get each version
for version in $(seq 1 5); do
  echo "Version $version:"
  curl http://localhost:8081/subjects/sqlserver.warehouse_source.dbo.customers-value/versions/$version | jq .schema
done
```

---

## Dead Letter Queue

### Viewing DLQ Messages

**Check DLQ size**:
```bash
docker exec cdc-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic dlq-postgresql-sink \
  --time -1
```

**Consume DLQ messages**:
```bash
docker exec cdc-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic dlq-postgresql-sink \
  --from-beginning \
  --max-messages 10 \
  --property print.key=true \
  --property print.headers=true
```

### Analyzing DLQ Records

Each DLQ message includes error context in headers:
- `__connect.errors.topic`: Original topic
- `__connect.errors.partition`: Original partition
- `__connect.errors.offset`: Original offset
- `__connect.errors.exception.class`: Exception class
- `__connect.errors.exception.message`: Error message

**Parse DLQ message**:
```bash
docker exec cdc-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic dlq-postgresql-sink \
  --from-beginning --max-messages 1 \
  --property print.headers=true | grep __connect.errors
```

### Recovering from DLQ

1. **Identify the issue**:
```bash
# Get error details
docker exec cdc-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic dlq-postgresql-sink \
  --from-beginning --max-messages 1 \
  --property print.headers=true
```

2. **Fix the schema issue**:
```sql
-- Example: Add missing column
ALTER TABLE customers ADD COLUMN new_field VARCHAR(100);
```

3. **Replay failed messages** (if needed):
```bash
# Stop sink connector
curl -X PUT http://localhost:8083/connectors/postgresql-jdbc-sink/pause

# Fix schema
# ...

# Resume connector (will reprocess from last committed offset)
curl -X PUT http://localhost:8083/connectors/postgresql-jdbc-sink/resume
```

---

## Best Practices

### 1. Test Schema Changes in Non-Production First

```bash
# Use docker-compose.test.yml for isolated testing
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d

# Test schema change
# Verify behavior
# Tear down test environment
```

### 2. Make Changes During Low-Traffic Periods

- Schedule schema changes during maintenance windows
- Monitor replication lag during change
- Have rollback plan ready

### 3. Add Columns as Nullable Initially

```sql
-- Good: Can be applied immediately
ALTER TABLE customers ADD phone VARCHAR(20) NULL;

-- Later, add constraint after backfilling data
UPDATE customers SET phone = 'Unknown' WHERE phone IS NULL;
ALTER TABLE customers ALTER COLUMN phone VARCHAR(20) NOT NULL;
```

### 4. Monitor DLQ Growth

```bash
# Set up alert for DLQ growth
# Alert fires if DLQ has >100 messages for 10 minutes
```

### 5. Document Schema Changes

Maintain a changelog:
```markdown
# Schema Changes

## 2025-12-02: Add loyalty_points column
- Table: customers
- Change: ADD COLUMN loyalty_points INT NULL
- Status: ✅ Auto-evolved successfully
- PostgreSQL updated: 2025-12-02 14:30 UTC
```

### 6. Use Schema Registry Compatibility Levels Wisely

```bash
# Set compatibility for specific subject
curl -X PUT http://localhost:8081/config/sqlserver.warehouse_source.dbo.customers-value \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"compatibility":"BACKWARD"}'
```

---

## Troubleshooting

### Schema Change Not Detected

**Check Debezium configuration**:
```bash
curl http://localhost:8083/connectors/sqlserver-cdc-source/config | jq '.["include.schema.changes"]'
# Should return: "true"
```

**Check schema change topic**:
```bash
docker exec cdc-kafka kafka-topics --describe \
  --bootstrap-server localhost:9092 \
  --topic schema-changes.warehouse_source
```

**Verify CDC is enabled on table**:
```sql
SELECT name, is_tracked_by_cdc
FROM sys.tables
WHERE name = 'customers';
```

### Column Not Added to PostgreSQL

**Check auto.evolve setting**:
```bash
curl http://localhost:8083/connectors/postgresql-jdbc-sink/config | jq '.["auto.evolve"]'
# Should return: "true"
```

**Check connector logs**:
```bash
docker logs cdc-kafka-connect --tail 100 | grep -i "schema\|evolve"
```

**Verify PostgreSQL permissions**:
```sql
-- Connector user must have ALTER TABLE permission
GRANT ALTER ON ALL TABLES IN SCHEMA public TO postgres;
```

### Type Mismatch Errors

**Check type mappings**:

| SQL Server Type | PostgreSQL Type | Compatible? |
|----------------|-----------------|-------------|
| INT            | INTEGER         | ✅ Yes      |
| BIGINT         | BIGINT          | ✅ Yes      |
| VARCHAR(n)     | VARCHAR(n)      | ✅ Yes      |
| NVARCHAR(n)    | VARCHAR(n)      | ✅ Yes      |
| DECIMAL(p,s)   | NUMERIC(p,s)    | ✅ Yes      |
| DATETIME2      | TIMESTAMP       | ✅ Yes      |
| BIT            | BOOLEAN         | ✅ Yes      |
| UNIQUEIDENTIFIER | UUID          | ⚠️ May need transform |

**Add SMT (Single Message Transform) for type conversion**:
```json
{
  "transforms": "cast",
  "transforms.cast.type": "org.apache.kafka.connect.transforms.Cast$Value",
  "transforms.cast.spec": "field_name:int32"
}
```

### DLQ Growing Rapidly

**Pause connector immediately**:
```bash
curl -X PUT http://localhost:8083/connectors/postgresql-jdbc-sink/pause
```

**Investigate errors**:
```bash
# Get recent errors
docker logs cdc-kafka-connect --tail 100 | grep -i error

# Check DLQ messages
docker exec cdc-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic dlq-postgresql-sink \
  --from-beginning --max-messages 5 \
  --property print.headers=true
```

**Fix and resume**:
```bash
# After fixing schema issue
curl -X PUT http://localhost:8083/connectors/postgresql-jdbc-sink/resume
```

---

## Additional Resources

- [Debezium Schema Evolution](https://debezium.io/documentation/reference/stable/connectors/sqlserver.html#sqlserver-schema-evolution)
- [Confluent Schema Registry](https://docs.confluent.io/platform/current/schema-registry/index.html)
- [JDBC Sink Connector Configuration](https://docs.confluent.io/kafka-connect-jdbc/current/sink-connector/sink_config_options.html)
- [Kafka Connect Dead Letter Queue](https://docs.confluent.io/platform/current/connect/concepts.html#dead-letter-queue)
