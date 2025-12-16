# Microsoft SQL Server CDC Source Connector (Confluent)

## Overview
The Microsoft SQL Server CDC Source (Debezium) connector for Confluent Cloud captures row-level changes from SQL Server databases and streams them to Apache Kafka. It takes an initial snapshot of existing data, then continuously monitors and records all subsequent changes.

**Important Note:** This connector is **deprecated** and reaches end-of-life on January 9, 2026. Confluent recommends migrating to [version 2](https://docs.confluent.io/cloud/current/connectors/cc-microsoft-sql-server-source-cdc-v2-debezium/index.html).

## Key Features
- **Automatic Topic Creation**: Topics are named as `<database.server.name>.<schemaName>.<tableName>`
- **Table Filtering**: Include/exclude specific tables from monitoring
- **Snapshot Modes**: `initial` (snapshot + stream), `schema_only` (structure only), `initial_only` (snapshot without stream)
- **Output Formats**: Avro, JSON Schema, Protobuf, or JSON (schemaless)
- **Tombstone Events**: Generate delete markers for proper Kafka log compaction
- **Incremental Snapshots**: Supported via signaling for large tables
- **Single Task Limit**: `tasks.max` must be set to 1

## Prerequisites
- SQL Server configured for Change Data Capture (CDC)
- Public network access to SQL Server
- Kafka cluster with credentials (API key or service account)
- Schema Registry enabled (for schema-based formats)

## Typical Configuration File

```json
{
  "connector.class": "SqlServerCdcSource",
  "name": "sqlserver-cdc-connector",
  "kafka.auth.mode": "KAFKA_API_KEY",
  "kafka.api.key": "YOUR_API_KEY",
  "kafka.api.secret": "YOUR_API_SECRET",
  
  "database.hostname": "sqlserver.example.com",
  "database.port": "1433",
  "database.user": "cdc_user",
  "database.password": "secure_password",
  "database.dbname": "production_db",
  "database.server.name": "sqlserver-prod",
  "database.instance": "MSSQLSERVER",
  
  "table.include.list": "dbo.customers,dbo.orders,dbo.products",
  "column.exclude.list": "dbo\\..*\\.internal_.*",
  
  "snapshot.mode": "initial",
  "snapshot.isolation.mode": "repeatable_read",
  
  "output.data.format": "JSON",
  "output.key.format": "STRING",
  "after.state.only": true,
  
  "tombstones.on.delete": true,
  "provide.transaction.metadata": false,
  "decimal.handling.mode": "string",
  "binary.handling.mode": "base64",
  "time.precision.mode": "adaptive",
  
  "poll.interval.ms": "1000",
  "max.batch.size": "2048",
  "heartbeat.interval.ms": "0",
  "event.processing.failure.handling.mode": "fail",
  
  "tasks.max": "1"
}
```

## Critical Configuration Properties

| Property | Purpose | Example |
|----------|---------|---------|
| `database.server.name` | Logical namespace for Kafka topics | `sqlserver-prod` |
| `table.include.list` | Tables to monitor (schema.table format) | `dbo.customers,dbo.orders` |
| `snapshot.mode` | Initial data capture strategy | `initial` |
| `output.data.format` | Kafka message value format | `JSON`, `AVRO`, `PROTOBUF` |
| `decimal.handling.mode` | How to handle DECIMAL/NUMERIC types | `string`, `precise`, `double` |
| `binary.handling.mode` | How to handle binary columns | `bytes`, `base64`, `hex` |

## Additional Configuration Options

### Data Type Handling
- **`decimal.handling.mode`**: Options are `precise` (BigDecimal, default), `string`, or `double`
- **`binary.handling.mode`**: Options are `bytes` (default), `base64`, or `hex`
- **`time.precision.mode`**: Options are `adaptive` (default), `adaptive_time_microseconds`, or `connect`

### Snapshot Configuration
- **`snapshot.isolation.mode`**: Controls transaction isolation level during snapshot
  - `exclusive` (full consistency, locks tables)
  - `repeatable_read` (default, allows concurrent updates)
  - `snapshot`, `read_committed`, `read_uncommitted`
- **`snapshot.mode`**: 
  - `initial` (default) - snapshot + stream - Use "initial" to take a snapshot of existing data on first run.
  - `schema_only` - structure only, stream from start - Use "schema_only" to only capture schema changes without initial data.
  - `initial_only` - snapshot but no streaming

### Connection & Performance
- **`poll.interval.ms`**: Polling frequency for change events (default: 1000ms)
- **`max.batch.size`**: Maximum events per batch (default: 1000, max: 5000)
- **`heartbeat.interval.ms`**: Heartbeat frequency (0 = disabled)
- **`event.processing.failure.handling.mode`**: `fail`, `skip`, or `warn`

### Data Filtering
- **`table.include.list`**: Comma-separated list of tables to monitor (format: `schema.table`)
- **`table.exclude.list`**: Comma-separated list of tables to exclude
- **`column.exclude.list`**: Regex patterns for columns to exclude (format: `database.schema.table.column`)

### Output & Messaging
- **`after.state.only`**: Include only the final state (default: true)
- **`tombstones.on.delete`**: Generate tombstone events after deletes (default: true)
- **`provide.transaction.metadata`**: Store transaction metadata in dedicated topic (default: false)
- **`cleanup.policy`**: Topic cleanup - `delete` (default) or `compact`

## Deployment Steps (CLI)

```bash
# Create connector from config file
confluent connect cluster create --config-file sqlserver-cdc.json

# Check connector status
confluent connect cluster list

# View connector logs
confluent connect cluster logs <connector-id>

# Describe available properties
confluent connect plugin describe SqlServerCdcSource
```

## Important Considerations

### Database Requirements
- CDC must be enabled on the source database: `EXEC sys.sp_cdc_enable_db;`
- CDC must be enabled on specific tables: `EXEC sys.sp_cdc_enable_table @source_schema = 'dbo', @source_name = 'table_name', @role_name = NULL;`
- A database user with CDC permissions is required

### Network & Access
- Requires public network access or VPC/security group configuration
- Database must be reachable from Confluent Cloud infrastructure
- May require configuring static egress IP addresses for firewall rules

### Log Retention
- Large table snapshots may exceed transaction log retention
- Increase transaction log retention before snapshotting large tables
- Database server maintains redo and transaction logs during snapshot

### Limitations
- **Single Task Only**: `tasks.max` must be "1" per organization
- **Deprecated**: Plan migration to v2 before January 9, 2026
- **Max Message Size**: 8MB (basic/standard/enterprise), 20MB (dedicated clusters)

## Topic Naming Convention

Topics are automatically created with the pattern:
```
<database.server.name>.<schema_name>.<table_name>
```

Additional topics created:
- `dbhistory.<database.server.name>.<connect-id>` - Schema history (1 partition)
- `<database.server.name>-transaction` - Transaction metadata (if enabled)

## Example Kafka Topic Outputs

For a table `dbo.customers` with `database.server.name = sqlserver-prod`:
- Topic: `sqlserver-prod.dbo.customers`
- Key: Customer ID or composite key
- Value: Changed record in JSON/Avro format with operation type (`c`, `u`, `d`)

## Monitoring & Troubleshooting

### Check Connector Health
```bash
confluent connect cluster describe <connector-id>
```

### View Recent Logs
```bash
confluent connect cluster logs <connector-id> --tail 100
```

### Verify Topics Created
```bash
confluent kafka topic list --filter "sqlserver-prod"
confluent kafka topic consume sqlserver-prod.dbo.customers --from-beginning --max-messages 5
```

## Migration Path
For new deployments, consider using [Microsoft SQL Server CDC Source V2 (Debezium)](https://docs.confluent.io/cloud/current/connectors/cc-microsoft-sql-server-source-cdc-v2-debezium/index.html) which provides improved performance and features.

## References
- [Confluent Cloud Documentation](https://docs.confluent.io/cloud/current/connectors/cc-microsoft-sql-server-source-cdc-debezium.html)
- [Debezium SQL Server Documentation](https://debezium.io/documentation/reference/1.9/connectors/sqlserver.html)
- [AWS RDS SQL Server CDC Setup](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.SQLServer.CommonDBATasks.CDC.html)
