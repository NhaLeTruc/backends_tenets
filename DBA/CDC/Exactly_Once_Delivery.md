# Exactly Once Delivery in CDC Context

## Overview

**Exactly-once delivery** is a semantic guarantee that ensures every change event from a source database appears in the downstream system **exactly once** - no duplicates, no missed changes. This is a critical requirement for maintaining data consistency in Change Data Capture (CDC) pipelines, especially in financial systems, order processing, and any domain where duplicate records cause problems.

### Delivery Guarantees Spectrum

In distributed systems, delivery semantics exist on a spectrum:

- **At-most-once**: Changes may be lost, but no duplicates. ❌ High risk for CDC (data loss)
- **At-least-once**: No changes are lost, but duplicates may occur. ⚠️ Default for most CDC systems (including Debezium)
- **Exactly-once**: Every change delivered exactly once. ✅ Perfect consistency but hardest to implement

## Why Exactly-Once is Hard

Achieving exactly-once delivery requires solving the **two-phase problem**:

1. **Source Reading**: Extracting changes from the database without losing or duplicating any
2. **Sink Writing**: Ensuring changes reach the destination exactly once, even on failure

The challenge: If the source connector crashes after reading a batch but before committing its offset, what happens?

- **At-least-once**: Re-read and re-send the batch (duplicates allowed)
- **Exactly-once**: Must guarantee the batch was delivered AND committed before re-reading

## Debezium's Approach to Exactly-Once Delivery

### Debezium's Native Guarantee

**Debezium provides at-least-once delivery guarantees by design.** It does NOT implement an internal deduplication layer. However, Debezium connectors can participate in Kafka Connect's exactly-once delivery mechanism when deployed in the Kafka Connect framework.

### How Debezium Achieves Exactly-Once (via Kafka Connect)

Debezium leverages **Kafka Connect's exactly-once delivery framework** introduced in [KIP-618](https://cwiki.apache.org/confluence/display/KAFKA/KIP-618%3A+Exactly-Once+Support+for+Source+Connectors), which builds on Kafka's transaction support from [KIP-98](https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging).

#### The Architecture

```
┌─────────────────────┐
│  Source Database    │
│  (PostgreSQL, etc)  │
└──────────┬──────────┘
           │
           │ Read Changes
           ▼
┌──────────────────────────────────┐
│    Debezium Source Connector     │
│  (Snapshot + Incremental Polling)│
└──────────┬───────────────────────┘
           │
           │ Transactional Publish (Kafka TX)
           │ - Source offset + change events  
           │ - All-or-nothing semantics
           ▼
┌──────────────────────────────────┐
│  Kafka Broker with Transactions  │
│  (Single atomic write)           │
└──────────┬───────────────────────┘
           │
           │ Consume with Isolation
           │ (Read Committed)
           ▼
┌──────────────────────────────────┐
│    Sink Connector / Consumer     │
│  (Idempotent writes)             │
└──────────────────────────────────┘
```

### Key Mechanisms for Exactly-Once in Debezium

#### 1. **Kafka Connect Transactional Publishing**

When exactly-once is enabled:

- Debezium reads a batch of changes from the source database
- It publishes these changes to Kafka **within a single Kafka transaction**
- The source connector's offset is committed **atomically** with the change events
- This ensures: Changes reach Kafka exactly once before the offset advances

```
Transaction {
  Insert offset=100 to Kafka
  Insert 5 change events to Kafka
  Commit atomically
}
```

If the connector crashes mid-transaction, the entire batch is rolled back - Kafka sees nothing, and the offset doesn't advance. Upon restart, the connector re-reads from the last safe offset.

#### 2. **Transaction Boundary Setting**

Debezium uses the `transaction.boundary` configuration to define atomic units:

```properties
# Default: transaction.boundary=poll
# Means: Each poll() cycle is one atomic transaction
```

Each invocation of the connector's `poll()` method (which fetches changes) becomes a single Kafka transaction. This ensures logical consistency.

#### 3. **Poll-Based Change Batching**

Debezium's polling model naturally creates transaction boundaries:

```
Poll #1 → Read rows 1-100 → Single TX
Poll #2 → Read rows 101-200 → Single TX
Poll #3 → Read rows 201-300 → Single TX
```

Each poll is atomic - all changes in a poll reach Kafka and the offset advances, or none do.

#### 4. **Offset Tracking with Source Info**

Debezium includes **source metadata** with each change event:

```json
{
  "before": null,
  "after": {"id": 1, "name": "Alice"},
  "source": {
    "version": "2.x",
    "connector": "postgresql",
    "name": "production",
    "ts_ms": 1671234567890,
    "txId": 12345,
    "lsn": 9876543210,
    "xmin": null
  },
  "op": "c",
  "ts_ms": 1671234567890
}
```

This source metadata enables **sink connectors to detect duplicates** using idempotent operations:

```sql
-- Sink: PostgreSQL
INSERT INTO replicated_table (id, name)
VALUES (1, 'Alice')
ON CONFLICT (id) DO UPDATE SET name = 'Alice'
WHERE source_ts_ms = 1671234567890;
-- Idempotent: Duplicate events are harmless
```

#### 5. **Read Committed Isolation in Kafka**

Consumers reading from Kafka with exactly-once delivery use **Read Committed isolation level**:

- Only see messages that have been successfully committed (inside completed transactions)
- Automatically skip aborted/rolled-back messages
- Prevents seeing partial or failed writes

### Supported Debezium Connectors for Exactly-Once

The following Debezium source connectors support exactly-once delivery:

- ✅ PostgreSQL
- ✅ MySQL
- ✅ MariaDB
- ✅ Oracle
- ✅ SQL Server
- ✅ MongoDB

## Configuration for Exactly-Once Delivery

### Prerequisites

1. **Kafka Broker**: Running with transaction support (Kafka 2.0+)
2. **Kafka Connect**: Version 3.3.0 or higher
3. **Kafka Mode**: Must be **distributed mode** (not standalone)

### Kafka Connect Worker Configuration

Enable exactly-once in the **Kafka Connect worker properties** (`connect-distributed.properties` or environment):

```properties
# Enable exactly-once delivery support globally
exactly.once.source.support=enabled

# Optional: ACL configuration for transaction isolation
```

All workers in the cluster must have this enabled for consistency.

### Debezium Source Connector Configuration

Enable exactly-once for a specific connector in the **connector config**:

```json
{
  "name": "postgres-cdc-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "localhost",
    "database.port": 5432,
    "database.user": "postgres",
    "database.password": "password",
    "database.dbname": "mydb",
    "publication.name": "dbz_publication",
    
    // Exactly-once configuration
    "exactly.once.support": "required",
    
    // Transaction boundary (poll is default)
    "transaction.boundary": "poll",
    
    // Additional tuning for exactly-once
    "max.batch.size": 5000,
    "poll.interval.ms": 1000,
    "snapshot.mode": "initial"
  }
}
```

**Key Parameters:**

| Parameter | Value | Notes |
|-----------|-------|-------|
| `exactly.once.support` | `required` | Enforces exactly-once; connector fails if not supported |
| `transaction.boundary` | `poll` | Default; defines atomic unit as one poll cycle |
| `max.batch.size` | 1-5000 | Number of rows per transaction (larger = fewer TX, lower latency) |
| `poll.interval.ms` | 100-5000 | Frequency of polling the source DB |

## How Exactly-Once Works in Practice

### Scenario: PostgreSQL → Kafka → PostgreSQL

```
Time  | PostgreSQL (Source) | Debezium         | Kafka               | Consumer
------|---------------------|------------------|---------------------|-------------
T1    | WAL: Write row#100  |                  |                     |
T2    | WAL: Write row#101  |                  |                     |
T3    |                     | Poll()→Read#100,#101 |                 |
T4    |                     | Begin TX         | [In progress]       |
T5    |                     | Publish changes  | [Buffered]          |
T6    |                     | Publish offset   | [Buffered]          |
T7    |                     | Commit TX        | Atomic write        | [Waiting]
T8    |                     |                  | Changes committed   | Read from TX
T9    |                     |                  |                     | Idempotent insert
T10   |                     |                  |                     | Commit sink
```

**What happens if Debezium crashes at T5?**
- Transaction is automatically rolled back
- Offset is NOT advanced
- Kafka sees nothing
- On restart: Debezium re-reads from same WAL position
- **Result: Exactly-once achieved ✅**

**What happens if Kafka broker crashes at T7?**
- Transaction not fully committed
- Debezium polls again (still within transaction timeout window)
- Publishes same changes again within new transaction
- Kafka deduplicates based on `idempotent.producer` flag
- **Result: Exactly-once achieved ✅**

## Known Issues and Caveats

⚠️ **Important**: Kafka Connect's exactly-once delivery relies on Kafka's transaction protocol. Recent Jepsen analyses have identified potential issues in Kafka transaction implementations:

- [KAFKA-17734](https://issues.apache.org/jira/browse/KAFKA-17734)
- [KAFKA-17754](https://issues.apache.org/jira/browse/KAFKA-17754)
- [KAFKA-17582](https://issues.apache.org/jira/browse/KAFKA-17582)

**Recommendation**: While Kafka Connect exactly-once is generally reliable, there are known edge cases in Kafka's transaction protocol. For absolute correctness, consider:

1. **Comprehensive testing** with failure scenarios
2. **Sink-side deduplication** using business keys and timestamps
3. **Monitoring** for duplicate detection
4. **Keeping Kafka updated** to latest patch versions

## Comparison: Exactly-Once vs At-Least-Once

| Aspect | At-Least-Once | Exactly-Once |
|--------|---------------|--------------|
| **Setup Complexity** | Simple; default | Complex; requires Kafka 3.3+, distributed mode |
| **Latency** | Lower (no transactions) | Higher (transaction overhead) |
| **Throughput** | Higher | Lower (atomic batches) |
| **Duplicate Handling** | Downstream must handle | Kafka + Debezium guarantee |
| **Cost** | Lower | Higher (more Kafka broker overhead) |
| **Correctness** | Good for analytics | Required for transactional systems |
| **Failure Recovery** | Simple replay | Complex (transaction rollback) |

## When to Use Exactly-Once

✅ **Use Exactly-Once for:**
- Financial transactions and payments
- Order processing systems
- Inventory management
- Account balance updates
- Any domain where duplicates violate business logic

❌ **At-Least-Once is acceptable for:**
- Analytics and data warehousing
- Logs and events
- Time-series metrics
- Immutable append-only streams

## Implementation Checklist

- [ ] Kafka cluster version 2.0+ with transaction support
- [ ] Kafka Connect version 3.3.0+
- [ ] Kafka Connect in distributed mode
- [ ] `exactly.once.source.support=enabled` in worker config
- [ ] `exactly.once.support=required` in Debezium connector config
- [ ] `transaction.boundary=poll` (explicit or default)
- [ ] Sink has idempotent write logic (business key + timestamp)
- [ ] Monitoring for duplicate detection
- [ ] Tested failure scenarios (broker crash, connector crash, network partition)
- [ ] Documentation of transaction semantics for team

## References

- **Debezium EOS Documentation**: https://debezium.io/documentation/reference/stable/configuration/eos.html
- **KIP-618**: Exactly-Once Support for Source Connectors
- **KIP-98**: Exactly Once Delivery and Transactional Messaging in Kafka
- **Kafka Transactions**: https://kafka.apache.org/documentation/#transactions
