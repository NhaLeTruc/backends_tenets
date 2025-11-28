# How often does postgres reconcile transactions

PostgreSQL fundamentally operates by treating every SQL statement within a transaction. The concept of "reconciling transactions" in PostgreSQL isn't a periodic, scheduled event in the way a system might periodically run a cleanup task. Instead, it's an inherent part of how transactions are managed and how concurrency is handled.

## Here's how it works

- **Autocommit Mode**

By default, PostgreSQL operates in <mark>"autocommit"</mark> mode. This means that if you execute a single SQL statement without explicitly starting a transaction block <mark>(using BEGIN or START TRANSACTION)</mark>, that single statement is treated as a complete transaction, implicitly beginning and committing (if successful) immediately.

In this scenario, there's no "reconciliation" needed for that individual statement as its effect is immediately made permanent or rolled back if an error occurs.

- **Transaction Blocks**

When you explicitly start a transaction block with <mark>BEGIN or START TRANSACTION</mark>, all subsequent statements within that block are treated as a single, atomic unit. These statements are not made permanent until a <mark>COMMIT</mark> command is issued.

If an error occurs within the block, or if a <mark>ROLLBACK</mark> command is issued, all changes made within that transaction block are undone.

- **Concurrency Control (MVCC)**

PostgreSQL uses <mark>Multi-Version Concurrency Control (MVCC)</mark>. This means that each transaction operates on a "snapshot" of the database's committed state at a particular instant. This mechanism largely prevents transactions from interfering with each other and avoids the need for frequent "reconciliation" in the sense of resolving conflicts between concurrent operations.

If conflicts do arise (e.g., a serialization error at a higher isolation level), PostgreSQL will automatically roll back the conflicting transaction.

### Distributed Transactions (e.g., EDB Postgres Distributed)

In more advanced, distributed PostgreSQL setups (like EDB Postgres Distributed), there are mechanisms for managing and reconciling transaction states across multiple nodes, especially in scenarios like origin node failures.

This involves tracking prepared transactions and ensuring consistent commit or rollback decisions across the cluster, often leveraging protocols like Raft. This "reconciliation" happens as needed to maintain consistency in a distributed environment, not on a fixed schedule.

> In essence, PostgreSQL handles transaction integrity and consistency continuously as transactions are processed, rather than through a separate, scheduled "reconciliation" process for individual transactions. The need for explicit reconciliation primarily arises in distributed setups to ensure global consistency during failures.

---
---

## MVCC

An <mark>MVCC (Multiversion Concurrency Control)</mark> snapshot is a point-in-time, read-only copy of a database used by a transaction to ensure consistent data reads while allowing other transactions to continue modifying the data. Instead of using locks for reading, MVCC creates versions of data rows, so a transaction can see a consistent view of the database as it was when the transaction or statement began, without being blocked by or blocking other concurrent transactions.

### How MVCC snapshots work

- **Multiple versions**
When a row is updated, the old version isn't immediately deleted. Instead, a new version is created and the old one is kept for transactions that might still need it.

- **Transaction start**
A transaction gets a "snapshot" of the database, which is a consistent view of the data as of a specific moment, usually the start of the transaction or a specific SQL statement.

- **Data visibility**
Visibility rules determine which version of a row a transaction can "see" based on the transaction's ID and the creation and deletion/update IDs of the row versions.

- **No blocking**
Readers don't block writers because they operate on their own snapshot, and writers don't block readers because they don't need to acquire locks on data that is being read.

- **Consistency**
This approach ensures that a transaction always sees a consistent view of the data, preventing anomalies that can occur with traditional locking mechanisms.

### Key takeaway

> MVCC snapshots are fundamental to high-performance databases by enabling concurrent reads and writes. They provide transaction isolation by giving each transaction its own consistent view of the data, eliminating the need for read locks and improving performance in high-concurrency environments.
