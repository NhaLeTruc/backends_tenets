# Postgres wal_level

The wal_level parameter in PostgreSQL controls the amount of information written to the Write-Ahead Log (WAL). This parameter can only be set at server start and influences the capabilities available for data recovery, replication, and logical decoding.

## There are three main values for wal_level

- **minimal**
This level logs only the information necessary to recover from a crash or immediate shutdown. It generates the least amount of WAL volume and can significantly speed up operations that create or rewrite permanent relations, such as <mark>CREATE TABLE, CLUSTER, REINDEX, and TRUNCATE</mark>, by omitting row information in the WAL for these transactions. However, minimal WAL does not contain enough information for point-in-time recovery or streaming binary replication.
  
- **replica**
This is the default value. It writes enough data to support WAL archiving and replication, including running read-only queries on a standby server. This level is <mark>required for continuous archiving (archive_mode) and streaming binary replication</mark>.
  
- **logical**
This level includes all the information logged by replica, plus additional information required to support logical decoding. Logical decoding allows for the extraction of persistent changes to a database's tables into a coherent format, <mark>enabling features like logical replication and change data capture (CDC)</mark>.

> Each wal_level includes the information logged by all lower levels. For example, logical includes everything in replica and minimal. The choice of wal_level depends on the specific requirements for data recovery, replication, and integration with other systems.

---

## Different transaction isolation levels

The four standard SQL transaction isolation levels are Read Uncommitted, Read Committed, Repeatable Read, and Serializable, which range from the least to most strict. Each level determines how a transaction interacts with concurrent transactions, with higher levels providing greater data consistency but potentially lower performance, and lower levels increasing performance at the cost of potential anomalies like dirty reads, nonrepeatable reads, and phantom reads.

### Read Uncommitted

- **Description**: The least strict level, allowing a transaction to read data from other transactions that have not yet been committed.
- **Anomalies allowed**: All three: Dirty Reads, Nonrepeatable Reads, and Phantoms.
- **Pros**: High performance and concurrency.
- **Cons**: Can lead to reading data that is later rolled back, which technically never existed.

### Read Committed

- **Description**: A transaction can only read data that has been committed by other transactions.
- **Anomalies allowed**: Nonrepeatable Reads and Phantoms.
- **Anomalies prevented**: Dirty Reads.
- **Pros**: Improves on Read Uncommitted by preventing dirty reads.
- **Cons**: A transaction can see the same row change between its reads, which is a nonrepeatable read.

### Repeatable Read

- **Description**: Guarantees that if a transaction reads a row multiple times, it will get the same data each time.
- **Anomalies allowed**: Phantoms.
- **Anomalies prevented**: Dirty Reads and Nonrepeatable Reads.
- **Pros**: Prevents both dirty and nonrepeatable reads.
- **Cons**: A transaction might re-execute a query and see a new row that was inserted by another committed transaction—a phantom read.

### Serializable

- **Description**: The strictest level. It guarantees that concurrent transactions will produce the same result as if they were executed one after another (serially).
- **Anomalies allowed**: None.
- **Anomalies prevented**: Dirty Reads, Nonrepeatable Reads, and Phantoms.
- **Pros**: Provides the highest level of data consistency and is the easiest to reason about.
- **Cons**: Lowest performance due to heavy locking and potential for one transaction to block another.
