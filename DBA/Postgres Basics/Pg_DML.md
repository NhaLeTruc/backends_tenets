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

## what happens when a insert statement is executed in postgres

When an INSERT statement is executed in PostgreSQL, a series of steps occur to add new data to a table:

- **Parsing and Analysis**: PostgreSQL receives the INSERT query and analyzes its syntax and semantics, identifying the target table, columns, and values.

- **Schema and Permission Checks**: The system verifies the existence of the specified table and columns and checks if the user has the necessary privileges to perform an INSERT operation on that table and its columns.

- **Data Validation**: The data types of the provided values are validated against the data types of the corresponding target columns. Constraints (e.g., NOT NULL, UNIQUE, CHECK, foreign key constraints) are also checked to ensure data integrity. Default values are applied to columns not explicitly provided in the INSERT statement.

- **Row Insertion**: If all checks pass, the new row is written to the appropriate data blocks within PostgreSQL's shared buffers. This involves updating internal data structures and potentially modifying index entries if indexes are defined on the table.

- **Transaction Management**: The INSERT operation typically occurs within the context of a transaction. If the transaction is committed, the changes are permanently written to disk. If the transaction is rolled back, the inserted row is discarded.

- **Trigger Execution (Optional)**: If AFTER INSERT triggers are defined on the table, they are automatically fired after the row has been successfully inserted.

- **Return Value (Optional)**: If the INSERT statement includes a RETURNING clause, the specified values from the newly inserted row(s) are returned to the client.

## what happens when a delete statement is executed in postgres

When a DELETE statement is executed in PostgreSQL, the following actions occur:

- **Concurrency Control (MVCC)**: PostgreSQL utilizes Multi-Version Concurrency Control (MVCC). Instead of physically removing the data immediately, the DELETE operation marks the identified rows as "dead" or "invisible" to new transactions. This allows other concurrent transactions that started before the DELETE to still see the old versions of the data, ensuring data consistency and preventing locking issues.

- **Index Updates**: If the deleted rows contain values that are part of an index, the index entries corresponding to those rows are also marked as "dead" or updated to reflect the deletion.

- **Foreign Key Checks**: If the table has foreign key constraints, PostgreSQL checks to ensure that deleting the rows does not violate these constraints. This might involve checking for dependent rows in other tables or, if ON DELETE CASCADE is specified, recursively deleting dependent rows.

- **Transaction Management**: The DELETE operation is typically part of a transaction. The changes are not permanently applied to the database until a COMMIT statement is issued. If a ROLLBACK command is executed before COMMIT, the changes made by the DELETE statement are undone, and the deleted rows are restored.

- **Disk Space Reclamation (VACUUM)**: While the DELETE statement marks rows as dead, it does not immediately reclaim the disk space occupied by those rows. This space becomes available for reuse by new data inserted into the table, but a VACUUM or VACUUM FULL operation is required to fully reclaim the space and reduce the physical size of the table and its indexes on disk. VACUUM FULL also rewrites the entire table, which can be more disruptive but offers full space reclamation.

- **Returning Deleted Data (Optional)**: If the RETURNING clause is used with the DELETE statement, PostgreSQL returns the specified columns (or all columns with *) of the deleted rows as part of the query result.
