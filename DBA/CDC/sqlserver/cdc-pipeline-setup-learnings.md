# CDC Pipeline Setup: Learnings and Troubleshooting Guide

**Date**: 2025-12-03
**Pipeline**: SQL Server → Debezium → Kafka → JDBC Sink → PostgreSQL

## Overview

This document captures the key learnings, issues encountered, and solutions implemented while setting up a production-ready Change Data Capture (CDC) pipeline from SQL Server to PostgreSQL using Debezium, Kafka, and Kafka Connect.

## Architecture

```
SQL Server (CDC enabled)
    ↓
Debezium SQL Server Source Connector
    ↓
Apache Kafka (with Schema Registry)
    ↓
Confluent JDBC Sink Connector
    ↓
PostgreSQL Target Database
```

## Key Issues and Solutions

### 1. SQL Server ODBC Driver Version

**Issue**: SQL Server 2019 uses ODBC Driver 18, not the older version.

**Error**:
```
/opt/mssql-tools/bin/sqlcmd: no such file or directory
```

**Solution**:
- Update all sqlcmd paths from `/opt/mssql-tools/bin/sqlcmd` to `/opt/mssql-tools18/bin/sqlcmd`
- Add `-C` flag to trust self-signed certificates: `sqlcmd -S localhost -U sa -P password -C`

**Files Modified**:
- [scripts/bash/init-sqlserver.sh](../scripts/bash/init-sqlserver.sh)
- [docker/docker-compose.yml](../docker/docker-compose.yml) (healthcheck)

### 2. SQL Server Password Quoting

**Issue**: Shell interpretation of special characters in passwords.

**Error**:
```
Login failed for user 'sa'. Reason: Password did not match
```

**Solution**:
- Remove quotes around password with special characters
- Correct: `-P YourStrong!Passw0rd`
- Wrong: `-P 'YourStrong!Passw0rd'` (shell interprets `!` inside quotes)

### 3. Kafka Connect Plugin Installation

**Issue**: Debezium SQL Server connector not available in Confluent Hub.

**Error**:
```
Component not found: debezium/debezium-connector-sqlserver
```

**Solution**:
Download and install manually from Maven Central:
```bash
cd /tmp
curl -sL https://repo1.maven.org/maven2/io/debezium/debezium-connector-sqlserver/2.4.2.Final/debezium-connector-sqlserver-2.4.2.Final-plugin.tar.gz | tar xz
mv debezium-connector-sqlserver /usr/share/confluent-hub-components/
```

**Files Modified**:
- [docker/docker-compose.yml](../docker/docker-compose.yml) (kafka-connect command)

### 4. Vault Configuration Issues

**Issue**: Vault config provider not available, causing Kafka Connect startup failures.

**Error**:
```
ClassNotFoundException: com.github.jcustenborder.kafka.config.vault.VaultConfigProvider
```

**Solution**:
Disabled Vault configuration provider and used direct credentials for development:
```yaml
# CONNECT_CONFIG_PROVIDERS: vault  # Commented out
```

**Alternative**: For production, install the Vault config provider plugin or use environment variables.

### 5. Vault Service Port Conflict

**Issue**: Vault dev mode listener conflicted with config file listener.

**Error**:
```
address already in use at secret/
```

**Solution**:
- Removed config volume mount
- Used dev mode exclusively with command: `server -dev -dev-root-token-id=dev-root-token`
- Added `VAULT_TOKEN` environment variable for easier CLI access

### 6. Vault Policy Creation

**Issue**: Policy file not found after removing config volume.

**Error**:
```
open /vault/config/policies/kafka-connect-policy.hcl: no such file
```

**Solution**:
Create policy inline using heredoc instead of file:
```bash
docker exec -e VAULT_TOKEN="$VAULT_TOKEN" cdc-vault sh -c 'cat <<EOF | vault policy write kafka-connect -
# Policy content here
EOF
'
```

Use `jq` for JSON parsing:
```bash
CONNECT_TOKEN=$(... | jq -r '.auth.client_token')
```

**Files Modified**:
- [scripts/bash/vault-init.sh](../scripts/bash/vault-init.sh)

### 7. SQL Server Snapshot Isolation

**Issue**: Debezium requires snapshot isolation for consistent reads.

**Error**:
```
Snapshot isolation transaction failed accessing database 'warehouse_source' because snapshot isolation is not allowed
```

**Solution**:
Enable snapshot isolation on the database:
```sql
ALTER DATABASE warehouse_source SET ALLOW_SNAPSHOT_ISOLATION ON;
ALTER DATABASE warehouse_source SET READ_COMMITTED_SNAPSHOT ON;
```

**Note**: These commands can take time if there are active connections. May require SQL Server restart.

**Alternative**: Use `snapshot.isolation.mode: "read_uncommitted"` in Debezium config (less safe but works).

### 8. Schema History Topic Configuration

**Issue**: Schema history topic auto-created with compaction, but Debezium sends messages without keys.

**Error**:
```
Compacted topic cannot accept message without key in topic partition schema-changes.warehouse_source-0
```

**Solution**:
Create schema history topic with delete cleanup policy:
```bash
docker exec cdc-kafka kafka-topics --bootstrap-server localhost:9092 \
  --create --topic schema-changes.warehouse_source \
  --partitions 1 --replication-factor 1 \
  --config cleanup.policy=delete \
  --config retention.ms=604800000
```

### 9. Debezium Message Structure

**Issue**: Debezium CDC messages have a complex envelope structure that the JDBC sink can't process directly.

**Error**:
```
sqlserver.warehouse_source.dbo.customers.Value (STRUCT) type doesn't have a mapping to the SQL database column type
```

**Solution**:
Add Debezium SMT (Single Message Transform) to unwrap the envelope:
```json
{
  "transforms": "unwrap",
  "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
  "transforms.unwrap.drop.tombstones": "false",
  "transforms.unwrap.delete.handling.mode": "rewrite"
}
```

**Files Modified**:
- [docker/configs/kafka-connect/postgresql-sink.json](../docker/configs/kafka-connect/postgresql-sink.json)

### 10. Topic Naming and Table Creation

**Issue**: PostgreSQL interprets dots in table names as schema separators.

**Error**:
```
ERROR: schema "sqlserver" does not exist
```

**Problem**: Topic `sqlserver.warehouse_source.dbo.customers` → PostgreSQL tries to create table `customers` in schema `sqlserver.warehouse_source.dbo`.

**Solution**:
Add RegexRouter transform to simplify table names:
```json
{
  "transforms": "unwrap,route",
  "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
  "transforms.route.regex": "sqlserver\\.warehouse_source\\.dbo\\.(.*)",
  "transforms.route.replacement": "$1"
}
```

**Result**: Topic `sqlserver.warehouse_source.dbo.customers` → Table `customers`

### 11. Timestamp Data Type Mismatch

**Issue**: Debezium sends SQL Server DATETIME2 as microseconds since epoch (bigint), but JDBC sink auto-creates TIMESTAMP columns.

**Error**:
```
ERROR: column "created_at" is of type timestamp without time zone but expression is of type bigint
```

**Solution**:
Manually create tables with BIGINT for timestamp columns:
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(200),
    created_at BIGINT,  -- Microseconds since epoch
    updated_at BIGINT,
    __deleted VARCHAR(10)
);
```

Set `auto.create: "false"` in sink connector config.

**Alternative Solutions**:
1. Use timestamp conversion SMT (more complex)
2. Configure Debezium with `time.precision.mode: "connect"` (requires schema changes)

### 12. Connector Configuration - PK Mode

**Issue**: Initial configuration used `pk.mode: "record_key"` which doesn't work with the unwrapped message structure.

**Error**:
```
PK mode for table is RECORD_VALUE with configured PK fields [id], but record value schema does not contain field: id
```

**Solution**:
After unwrapping with ExtractNewRecordState, use:
```json
{
  "pk.mode": "record_value",
  "pk.fields": "id"
}
```

The unwrap transform flattens the message so the `id` field is in the value payload.

### 13. Consumer Group Offset Management

**Issue**: After fixing errors, the sink connector had already committed offsets, so it wouldn't reprocess failed messages.

**Solution**:
Reset consumer group offsets:
```bash
# Stop connector
curl -X DELETE http://localhost:8083/connectors/postgresql-jdbc-sink

# Reset offsets
docker exec cdc-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group connect-postgresql-jdbc-sink \
  --reset-offsets --to-earliest --all-topics --execute

# Redeploy connector
./scripts/bash/deploy-connector.sh docker/configs/kafka-connect/postgresql-sink.json
```

## Final Working Configuration

### Debezium SQL Server Source Connector

Key settings in [sqlserver-source.json](../docker/configs/debezium/sqlserver-source.json):

```json
{
  "snapshot.mode": "schema_only",
  "snapshot.locking.mode": "none",
  "schema.history.internal.kafka.topic": "schema-changes.warehouse_source",
  "table.include.list": "dbo.customers,dbo.orders,dbo.line_items"
}
```

**Note**: `schema_only` snapshot mode skips initial data snapshot, only captures schema and subsequent changes.

### PostgreSQL JDBC Sink Connector

Key settings in [postgresql-sink.json](../docker/configs/kafka-connect/postgresql-sink.json):

```json
{
  "insert.mode": "upsert",
  "pk.mode": "record_value",
  "pk.fields": "id",
  "auto.create": "false",
  "auto.evolve": "false",

  "transforms": "unwrap,route",
  "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
  "transforms.unwrap.drop.tombstones": "false",
  "transforms.unwrap.delete.handling.mode": "rewrite",
  "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
  "transforms.route.regex": "sqlserver\\.warehouse_source\\.dbo\\.(.*)",
  "transforms.route.replacement": "$1",

  "errors.tolerance": "all",
  "errors.deadletterqueue.topic.name": "dlq-postgresql-sink"
}
```

## Testing the Pipeline

### 1. Insert Test Data in SQL Server

```bash
docker exec cdc-sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P YourStrong!Passw0rd -C \
  -d warehouse_source \
  -Q "INSERT INTO dbo.customers (name, email) VALUES ('Test User', 'test@example.com')"
```

### 2. Verify CDC Capture in SQL Server

```bash
docker exec cdc-sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P YourStrong!Passw0rd -C \
  -d warehouse_source \
  -Q "SELECT COUNT(*) as change_count FROM cdc.dbo_customers_CT"
```

### 3. Check Kafka Topic

```bash
# Check message count
docker exec cdc-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic sqlserver.warehouse_source.dbo.customers

# Consume messages (for debugging)
docker exec cdc-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic sqlserver.warehouse_source.dbo.customers \
  --from-beginning --max-messages 1
```

### 4. Verify Data in PostgreSQL

```bash
docker exec cdc-postgres psql -U postgres -d warehouse_target \
  -c "SELECT * FROM customers WHERE name = 'Test User'"
```

### 5. Monitor Connector Status

```bash
# Check Debezium source
curl -s http://localhost:8083/connectors/sqlserver-cdc-source/status | jq

# Check PostgreSQL sink
curl -s http://localhost:8083/connectors/postgresql-jdbc-sink/status | jq

# Check dead letter queue for errors
docker exec cdc-kafka kafka-run-class kafka.tools.GetOffsetShell \
  --broker-list localhost:9092 \
  --topic dlq-postgresql-sink
```

## Best Practices

### 1. Error Handling

- Use `errors.tolerance: "all"` with dead letter queue for production resilience
- Monitor DLQ regularly for failed messages
- Set appropriate retry timeouts:
  ```json
  {
    "errors.retry.timeout": "300000",
    "errors.retry.delay.max.ms": "60000"
  }
  ```

### 2. Monitoring

Key metrics to monitor:
- Kafka Connect connector status (RUNNING/FAILED)
- Kafka topic lag (consumer group offset vs log-end-offset)
- Dead letter queue message count
- SQL Server CDC capture job status

### 3. Schema Evolution

- Set `auto.evolve: "true"` for development
- For production, plan schema changes carefully:
  1. Add column in source database
  2. Update Debezium connector (restart if needed)
  3. Update sink connector or manually alter target table
  4. Test with sample data

### 4. Snapshot Mode Selection

Options for `snapshot.mode`:
- `initial`: Full snapshot + ongoing changes (default, recommended for new deployments)
- `schema_only`: No data snapshot, only schema + ongoing changes (used in this setup)
- `when_needed`: Snapshot only if no offset exists
- `never`: Only capture changes (requires prior snapshot)

**Recommendation**: Use `initial` for new deployments unless you have a large dataset and can tolerate skipping historical data.

### 5. Data Type Mappings

Common SQL Server → PostgreSQL type mappings with Debezium:

| SQL Server Type | Debezium Type | PostgreSQL Type (Target) |
|----------------|---------------|-------------------------|
| INT            | INT32         | INTEGER                 |
| BIGINT         | INT64         | BIGINT                  |
| NVARCHAR(n)    | STRING        | VARCHAR(n)              |
| DATETIME2      | INT64 (μs)    | BIGINT or TIMESTAMP*    |
| DECIMAL(p,s)   | DECIMAL       | NUMERIC(p,s)            |
| BIT            | BOOLEAN       | BOOLEAN                 |

*Requires manual table creation with BIGINT or timestamp conversion SMT

## Troubleshooting Commands

### Check Kafka Connect Logs

```bash
# Recent logs
docker logs cdc-kafka-connect --tail 100

# Follow logs
docker logs -f cdc-kafka-connect

# Search for errors
docker logs cdc-kafka-connect 2>&1 | grep -i "error\|exception"
```

### List and Describe Topics

```bash
# List all topics
docker exec cdc-kafka kafka-topics --bootstrap-server localhost:9092 --list

# Describe specific topic
docker exec cdc-kafka kafka-topics --bootstrap-server localhost:9092 \
  --describe --topic sqlserver.warehouse_source.dbo.customers
```

### Consumer Group Management

```bash
# List consumer groups
docker exec cdc-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 --list

# Describe consumer group
docker exec cdc-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group connect-postgresql-jdbc-sink --describe
```

### Connector Management

```bash
# List connectors
curl -s http://localhost:8083/connectors

# Get connector config
curl -s http://localhost:8083/connectors/sqlserver-cdc-source | jq

# Restart connector
curl -X POST http://localhost:8083/connectors/sqlserver-cdc-source/restart

# Delete connector
curl -X DELETE http://localhost:8083/connectors/sqlserver-cdc-source
```

### SQL Server CDC Status

```bash
# Check if CDC is enabled on database
docker exec cdc-sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P YourStrong!Passw0rd -C \
  -Q "SELECT name, is_cdc_enabled FROM sys.databases WHERE name = 'warehouse_source'"

# Check CDC-enabled tables
docker exec cdc-sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P YourStrong!Passw0rd -C \
  -d warehouse_source \
  -Q "SELECT name, is_tracked_by_cdc FROM sys.tables WHERE schema_id = SCHEMA_ID('dbo')"

# Check CDC capture job
docker exec cdc-sqlserver /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P YourStrong!Passw0rd -C \
  -d warehouse_source \
  -Q "EXEC sys.sp_cdc_help_jobs"
```

## Common Pitfalls

1. **Forgetting `-C` flag**: SQL Server ODBC Driver 18 requires `-C` to trust certificates in development
2. **Quote password correctly**: Avoid single quotes around passwords with special characters
3. **Schema history topic**: Must use `cleanup.policy=delete`, not compaction
4. **Topic naming**: Dots in topic names cause PostgreSQL schema issues - use RegexRouter
5. **Timestamp types**: Debezium sends microseconds as bigint, not TIMESTAMP
6. **Snapshot isolation**: Required for consistent snapshots (or use `read_uncommitted`)
7. **Connector restarts**: Don't forget to reset consumer offsets when debugging errors
8. **ALTER DATABASE locks**: Can block all connections; may require SQL Server restart

## Performance Tuning

### Debezium Connector

```json
{
  "max.batch.size": "2048",           // Records per batch
  "max.queue.size": "8192",            // Internal queue size
  "poll.interval.ms": "500",           // CDC poll interval
  "snapshot.fetch.size": "2000"        // Rows per snapshot fetch
}
```

### JDBC Sink Connector

```json
{
  "batch.size": "3000",                // Records per insert batch
  "connection.pool.size": "10",        // DB connection pool
  "tasks.max": "3"                     // Parallel tasks
}
```

### Kafka Topic Configuration

```bash
# Create topic with specific partitions for parallelism
docker exec cdc-kafka kafka-topics --bootstrap-server localhost:9092 \
  --create --topic sqlserver.warehouse_source.dbo.customers \
  --partitions 3 --replication-factor 1
```

## References

- [Debezium SQL Server Connector Documentation](https://debezium.io/documentation/reference/stable/connectors/sqlserver.html)
- [Confluent JDBC Sink Connector](https://docs.confluent.io/kafka-connectors/jdbc/current/sink-connector/index.html)
- [Kafka Connect SMT Documentation](https://docs.confluent.io/platform/current/connect/transforms/overview.html)
- [SQL Server CDC Documentation](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server)

## Conclusion

This CDC pipeline successfully replicates data from SQL Server to PostgreSQL with the following characteristics:

- **Latency**: Near real-time (sub-second for small transactions)
- **Reliability**: Dead letter queue for error handling
- **Scalability**: Partitioned topics and parallel sink tasks
- **Schema Evolution**: Supported with manual coordination

The key to success was understanding the Debezium message envelope structure and properly configuring SMTs to transform messages for the JDBC sink connector.

### 14. PostgreSQL Initialization Script Heredoc Issue

**Issue**: The init-postgres.sh script used heredoc syntax with `docker exec`, which doesn't work as expected.

**Problem**:
```bash
docker exec cdc-postgres psql -U postgres -d warehouse_target <<EOF
CREATE TABLE customers (...);

### 14. PostgreSQL Initialization Script Heredoc Issue

**Issue**: The init-postgres.sh script used heredoc syntax with `docker exec`, which doesn't work as expected.

**Problem**:
```bash
docker exec cdc-postgres psql -U postgres -d warehouse_target <<EOF
CREATE TABLE customers (...);
EOF
```

The heredoc is interpreted by the **local shell**, not inside the container, causing it to fail silently or not execute properly.

**Solution**:
Use `-c` flag with inline SQL instead:
```bash
docker exec cdc-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(200),
    created_at BIGINT,
    updated_at BIGINT,
    __deleted VARCHAR(10)
);

CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
"
```

**Key Changes to init-postgres.sh**:
1. Replaced heredoc with `-c` flag and inline SQL
2. Changed TIMESTAMP columns to BIGINT (for Debezium microseconds)
3. Added `__deleted` column for soft delete tracking
4. Added verification step to confirm tables were created
5. Made NOT NULL constraints optional (Debezium may send nulls)
6. Removed foreign key constraints (can cause issues with CDC ordering)

**Files Modified**:
- [scripts/bash/init-postgres.sh](../scripts/bash/init-postgres.sh)

**Why Heredoc Fails with Docker Exec**:
- Heredoc (`<<EOF`) is a shell feature that redirects multi-line input
- When used with `docker exec`, the local shell processes the heredoc
- `docker exec` receives the content but may not process it correctly depending on how stdin is handled
- Using `-c` with a quoted string is more reliable for passing SQL to psql
