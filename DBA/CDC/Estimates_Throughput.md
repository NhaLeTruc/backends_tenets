# Throughput Determinants

## Database-Level Factors

1. **Transaction Log Scan Performance**
   - SQL Server reads the transaction log to capture changes
   - Log file I/O speed (SSD vs HDD) directly impacts scan rate
   - Transaction log contention affects throughput
   - Query: `SELECT * FROM sys.dm_io_virtual_file_stats(NULL, NULL)` to monitor disk I/O

2. **Change Volume (DML Operations)**
   - INSERT rate: Number of new rows per second
   - UPDATE rate: Frequency of row modifications
   - DELETE rate: Row deletions per second
   - **Formula**: Total throughput (events/sec) = (INSERTs + UPDATEs + DELETEs) per second

3. **Table Characteristics**
   - **Row size**: Larger rows = more bytes to transfer, slower processing
   - **Number of tables**: Connector processes all monitored tables sequentially
   - **Number of columns**: More columns = larger serialized records
   - **Index coverage**: Clustered index affects scan efficiency

4. **CDC Configuration Impact**
   - Tables with CDC enabled have overhead for change tracking
   - Query: `SELECT object_name(object_id), is_tracked_by_cdc FROM sys.tables WHERE database_id=db_id()`
   - CDC retention period: Longer retention = larger CT tables, slower queries

## Connector Configuration Factors

1. **Polling & Batching**
   - **`poll.interval.ms`**: Time between polls (default 1000ms)
     - Lower values (e.g., 500ms) = higher throughput but more overhead
     - Higher values = less frequent polling, potential latency increase
   - **`max.batch.size`**: Events per batch (default 1000, max 5000)
     - Larger batches = higher throughput, higher memory usage
     - Smaller batches = lower latency, more overhead

2. **Network Bandwidth**
   - Database to Confluent Cloud connection bandwidth
   - Latency between SQL Server and Kafka broker
   - Network packet loss, retries add overhead
   - Typical: 1Gbps network = ~100-125 MB/s theoretical limit

3. **Output Format**
   - **JSON**: Fastest serialization, smallest footprint
   - **STRING**: Similar to JSON
   - **AVRO**: Compact binary, moderate serialization cost
   - **PROTOBUF**: Compact, higher serialization overhead
   - **JSON_SR (JSON Schema)**: Schema Registry lookup adds latency
   - Serialization overhead: ~5-20ms per batch

4. **Message Size Impact**
   - Average record size in bytes affects network throughput
   - **Formula**: Network throughput (MB/s) = Events/sec × Average record size (KB) / 1024
   - Max message size limits: 8MB (standard), 20MB (dedicated)

5. **Snapshot Phase**
   - Initial snapshot throughput much lower than streaming
   - Large tables can take hours to snapshot
   - Snapshot rate ~1000-5000 rows/sec depending on row size and CPU

## Infrastructure Factors

1. **SQL Server Hardware**
   - CPU cores: Single-threaded connector uses only 1 core per task
   - Memory: Sufficient buffer pool for transaction log reading
   - Disk I/O: Transaction log on fast SSD critical
   - Network card: Full duplex Gigabit minimum

2. **Confluent Cluster Resources**
   - Broker throughput capacity (dependent on cluster tier)
   - Network egress bandwidth limits
   - Basic/Standard: ~5-10 MB/s per connector
   - Enterprise/Dedicated: Higher limits available

3. **Java/JVM Settings**
   - Heap memory for connector task
   - GC pauses can reduce throughput
   - Default heap may be insufficient for high-volume workloads

## Filtering & Processing Factors

- **Column exclusion**: Reduces record size, increases throughput
- **Table filtering**: Monitoring fewer tables = less work per poll
- **Tombstone events**: Additional records (deletes), slight throughput reduction
- **After-state-only**: Reduces record size if true (default)

## Estimating SQL Server CDC Throughput

### Step 1: Measure Source Database Change Rate

```sql
-- Query transaction log to estimate change rate
-- Run this query multiple times during peak hours

-- Method 1: Query CDC tables directly
SELECT 
  OBJECT_NAME(ct.object_id) AS TableName,
  COUNT(*) AS ChangeCount,
  MAX(ct.__$seq_val) AS MaxSeqVal
FROM cdc.dbo_YourTable_CT ct
WHERE ct.__$operation IN (2, 3, 4)  -- 2=DELETE, 3=INSERT, 4=UPDATE
AND ct.__$start_lsn > 
  (SELECT MAX(__$start_lsn) FROM cdc.dbo_YourTable_CT) - 1000
GROUP BY OBJECT_NAME(ct.object_id);

-- Method 2: Monitor DMVs for transaction rate
SELECT 
  DB_NAME(database_id) AS DatabaseName,
  SUM(user_updates) AS TotalUserUpdates,
  SUM(user_inserts) AS TotalUserInserts,
  SUM(user_deletes) AS TotalUserDeletes
FROM sys.dm_db_index_usage_stats
WHERE database_id = DB_ID('YourDatabase')
  AND last_user_update > DATEADD(HOUR, -1, GETDATE())
GROUP BY database_id;

-- Method 3: Estimate average row size
SELECT 
  OBJECT_NAME(ips.object_id) AS TableName,
  SUM(ips.avg_total_user_size * ips.row_count) / 1024 / 1024 AS TableSizeMB,
  AVG(ips.avg_total_user_size) AS AvgRowSizeBytes,
  ips.row_count
FROM sys.dm_db_partition_stats ips
WHERE OBJECTPROPERTY(ips.object_id, 'IsUserTable') = 1
GROUP BY ips.object_id;
```

### Step 2: Calculate Expected Throughput

#### Snapshot Phase (Initial Load)

```
Snapshot Throughput = (Total Rows / Average Row Size in MB) / Time in Seconds

Example:
- 10 million rows, average 2KB per row = 20 GB total
- Expected scan rate: 5000 rows/sec
- Time to snapshot: (10,000,000 rows) / 5000 rows/sec = 2000 seconds ≈ 33 minutes

Network throughput during snapshot:
= 5000 rows/sec × 2 KB/row = 10 MB/sec (well within network limits)
```

#### Streaming Phase (Ongoing Changes)

```
Peak Streaming Throughput = Changes per Second × Average Record Size

Example:
- INSERT rate: 1000/sec
- UPDATE rate: 500/sec  
- DELETE rate: 200/sec
- Total changes: 1700 changes/sec
- Average serialized record: 3 KB (with overhead)
- Throughput: 1700 × 3 KB = 5.1 MB/sec

Latency = poll.interval.ms + processing_time
- Default: 1000ms + ~50-200ms = 1.05-1.2 seconds (end-to-end)
```

### Step 3: Validate Connector Configuration for Target Throughput

```json
{
  "poll.interval.ms": "500",
  "max.batch.size": "5000",
  
  "output.data.format": "JSON",
  "binary.handling.mode": "base64",
  "after.state.only": true,
  
  "column.exclude.list": "dbo\\..*\\.(large_blob|unused_.*|internal_.*)",
  
  "decimal.handling.mode": "string",
  "provide.transaction.metadata": false
}
```

### Step 4: Load Testing & Validation

```bash
# 1. Monitor connector throughput
confluent connect cluster logs <connector-id> --tail 100 | grep -i "poll\|batch"

# 2. Check consumer lag
confluent kafka consumer-group list | grep connect

# 3. Monitor topic message rates
watch -n 1 'confluent kafka topic describe sqlserver-prod.dbo.large_table | grep "Message count"'

# 4. Measure end-to-end latency
# Timestamp in source = connector write timestamp
# Calculate: Kafka message timestamp - database change time

# 5. Monitor database CPU/IO during CDC capture
# Run these queries during peak load:
SELECT 
  s.session_id,
  s.login_name,
  r.status,
  r.wait_time_ms,
  r.cpu_time,
  st.text
FROM sys.dm_exec_sessions s
JOIN sys.dm_exec_requests r ON s.session_id = r.session_id
CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) st
WHERE s.database_id = DB_ID('YourDatabase');
```

## Throughput Optimization Checklist

| Factor | Optimization | Expected Impact |
|--------|-------------|-----------------|
| `max.batch.size` | Increase from 1000 to 5000 | +300-400% throughput |
| `poll.interval.ms` | Decrease from 1000 to 500 | +50-100% throughput |
| Output format | Switch JSON to AVRO | +15-25% throughput |
| Row exclusion | Use `column.exclude.list` | +10-30% throughput (depends on excluded size) |
| Table scope | Reduce `table.include.list` | +Proportional reduction |
| Record compression | Enable on Kafka producer | +20-40% throughput (at cost of CPU) |
| Network | Dedicated connection | +10-20% throughput |
| SQL Server | Enable transaction log backup | Reduces CT table bloat |

## Typical Throughput Benchmarks

- **Small tables** (<1M rows): 10K-50K events/sec
- **Medium tables** (1M-100M rows): 5K-20K events/sec
- **Large tables** (>100M rows): 1K-10K events/sec
- **Network bottleneck** typical at: 100-500 MB/sec (Gigabit network)
- **Latency** (snapshot to Kafka): 50-500ms depending on network and batch size
