# DML in Postgres

## What happens when a DML statement is executed in postgres

When a Data Manipulation Language (DML) statement (like INSERT, UPDATE, or DELETE) is executed in PostgreSQL, the following sequence of events generally occurs:

- **Parsing and Planning**: The DML statement is first parsed by the PostgreSQL server, which converts the SQL text into an internal representation. Then, the query planner analyzes this representation and generates an optimal execution plan for the statement, considering factors like table structure, indexes, and existing data.
- **Transaction Management**: DML statements are typically executed within the context of a transaction. If no explicit transaction is started (e.g., with <mark>BEGIN</mark>), PostgreSQL implicitly wraps the DML statement in its own transaction *(auto-commit behavior)*. This ensures atomicity, consistency, isolation, and durability (ACID properties).
- **Locking**: To maintain data integrity and prevent conflicts, PostgreSQL acquires locks on the affected data. For DML statements, this usually involves acquiring exclusive locks on the specific rows or pages being modified to prevent other concurrent transactions from modifying the same data simultaneously. Shared locks might also be acquired during reads that precede the modification.
- **Data Modification**: The planned execution is carried out, and the actual data in the table(s) is modified according to the DML statement.
  - <mark>INSERT:</mark> New rows are added to the specified table.
  - <mark>UPDATE:</mark> Existing rows are modified based on the WHERE clause and the new values provided.
  - <mark>DELETE:</mark> Rows matching the WHERE clause are removed from the table.
- **WAL (Write-Ahead Log) Entry**: Before the changes are written to the actual data files, an entry is written to the Write-Ahead Log (WAL). This ensures that even in case of a system crash, the database can recover by replaying the WAL and applying the committed changes.
- **Commit or Rollback**:
  - <mark>Commit:</mark> If the transaction is successfully completed, the changes are committed, making them permanent and visible to other transactions.
  - <mark>Rollback:</mark> If an error occurs or the user explicitly issues a ROLLBACK command, all changes made within that transaction are undone, and the database reverts to its state before the transaction began.
- **Index Updates (if applicable)**: If the modified data is part of an indexed column, the corresponding indexes are also updated to reflect the changes.
- **Visibility to Other Transactions**: Once a transaction is committed, the changes become visible to other transactions, depending on their isolation level.

---

## what happens when a update statement is executed in postgres

When an UPDATE statement is executed in PostgreSQL, the following sequence of events generally occurs:

- **Parsing and Planning**:
  - The UPDATE statement is parsed to check for syntax correctness.
  - PostgreSQL's query planner then analyzes the statement and determines the most efficient way to execute it, including which indexes to use and how to access the table data.
- **Row Identification**:
  - Based on the WHERE clause (if present), PostgreSQL identifies the specific rows in the target table that need to be updated. If no WHERE clause is specified, all rows in the table are targeted.
- **Concurrency Control (MVCC)**:
  - PostgreSQL uses Multi-Version Concurrency Control (MVCC). Instead of directly modifying the existing row, an UPDATE operation effectively creates a new version of the row.
  - The old version of the row is marked as "dead" or "obsolete" but is not immediately removed. This allows other concurrent transactions that started before the update to continue seeing the old version of the data, ensuring transaction isolation.
- **New Row Creation**:
  - A new row, containing the updated values for the specified columns, is inserted into the table. This new row has a new transaction ID (XID) and a pointer to the previous version.
- **Index Updates (if applicable)**:
  - If any of the updated columns are part of an index, the corresponding index entries are also updated to point to the new version of the row.
- **WAL Logging**:
  - The changes made by the UPDATE statement (the creation of the new row and marking of the old row) are written to the Write-Ahead Log (WAL) to ensure data durability and crash recovery.
- **Trigger Execution (if applicable)**:
  - If BEFORE UPDATE or AFTER UPDATE triggers are defined on the table, they are executed at the appropriate stage of the update process.
- **Result Return**:
  - The UPDATE statement returns a command tag indicating the number of rows that were affected (updated).
  - If a RETURNING clause is used, the specified values from the newly updated rows are returned to the client.
- **Vacuuming**:
  - Periodically, the autovacuum process or manual VACUUM commands run to reclaim space occupied by dead rows and update statistics, preventing excessive table bloat.
