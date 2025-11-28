# Postgres redo log vs undo log

In PostgreSQL, the concepts of <mark>"redo log"</mark> and <mark>"undo log"</mark> are primarily handled through its <mark>Write-Ahead Log (WAL)</mark> and <mark>Multi-Version Concurrency Control (MVCC)</mark> architecture. While other database systems like Oracle or MySQL's InnoDB engine explicitly maintain separate redo and undo logs, PostgreSQL's approach is integrated.

## Redo Log (PostgreSQL's WAL)

- **Purpose**: To ensure data durability and crash recovery. It records all changes made to the database before those changes are applied to the actual data files.

- **Mechanism**: PostgreSQL's WAL acts as the redo log. Every modification to data (inserts, updates, deletes) is first written to the WAL. This ensures that even if a system crash occurs before data files are fully updated, the committed changes can be replayed from the WAL during recovery, bringing the database to a consistent state.

- **Content**: Contains enough information to reconstruct the effects of committed transactions.

## Undo Log (PostgreSQL's MVCC)

- **Purpose**: To support transaction isolation and rollbacks of uncommitted transactions.

- **Mechanism**: PostgreSQL's MVCC provides the functionality typically associated with undo logs. Instead of recording "before images" in a separate undo log, MVCC creates new versions of rows for updates and deletions, leaving older versions visible to concurrent transactions that started before the change. If a transaction needs to roll back, the system simply discards the uncommitted new versions, and the older, committed versions remain available.

- **Content**: Older versions of data rows, which serve as the "before images" for transactions that might need to roll back or for concurrent transactions needing a consistent snapshot.

## Key Differences and PostgreSQL's Approach

- **Explicit Logs vs. Integrated Mechanism**: Other databases often have distinct physical files for redo and undo logs. PostgreSQL uses the WAL for redo functionality and relies on its MVCC architecture for undo capabilities, where older versions of data are maintained within the data pages themselves rather than in a separate undo log.

- **Recovery and Rollback**: In a crash recovery scenario, PostgreSQL uses the WAL to replay committed changes (redo). For uncommitted transactions, the new versions created by MVCC are simply ignored or cleaned up, effectively achieving the "undo" without needing a dedicated undo log.

- **Concurrency Control**: MVCC is central to how PostgreSQL manages concurrency and provides transaction isolation, which is a primary function of undo logs in other systems. It allows multiple transactions to access different versions of the same data without blocking each other.
