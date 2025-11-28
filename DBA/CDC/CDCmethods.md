# Different Methods to Implement CDC

## CDC in Postgres with

### 1. Triggers

Trigger-based Change Data Capture (CDC), also known as ‘Event Sourcing’, is a method used to capture changes in large databases and can be applied to PostgreSQL. It relies on its dedicated event log as the primary source of information. In this approach, triggers are an integral part of each database transaction, promptly capturing events as they happen. Think of a trigger as a set of automatic instructions for a database. It tells the database to do something automatically when a specific action happens, like when new data is added, existing data is updated, or data is deleted. These triggers can be linked to various parts of the database, like tables or views. Triggers for Postgres CDC can be set to run before or after actions like adding, updating, or deleting data.  They can also be set to run for each individual change, or just once for a group of changes. Additionally, you can specify that a trigger should only run if certain conditions are met, like if specific columns are changed. Triggers can even be set up to respond to actions like clearing out (TRUNCATE) all data in a table.

#### Advantages of Trigger-based Postgres CDC

- Postgres CDC using Triggers is extremely dependable and thorough.
- One significant advantage of the Trigger-based CDC approach is that, unlike transaction logs, everything happens within the SQL system.
- Shadow tables offer an unchangeable, comprehensive record of every transaction. How to Make PostgreSQL CDC to Kafka Easy (2 Methods)
- Instantly captures changes and allows for real-time processing of events.
- Triggers can detect different types of events: when new data is added, when data is updated, or when data is deleted.
- By default, the PostgreSQL Trigger function used in this method adds extra information to the events, like what caused the change, the ID of the transaction, or the name of the user involved.
- Triggers require making changes to the PostgreSQL database itself.

#### Disadvantages of Trigger-based Postgres CDC

- If you want to send change events to a different data storage system, you would have to create a separate process that regularly checks the table where the trigger function records the changes in the Postgres database (in this case, ‘audit.logged_actions’).
- Dealing with triggers adds more complexity in the management of your system.
- Using triggers can slow down the main Postgres database because these triggers run on the database itself and any operations executed, create an additional burden on the main database, increasing the overall time taken. To mitigate this performance impact, a common practice is to create a separate table that mirrors the main table and implement triggers on this secondary table. Synchronizing data between the master and secondary tables can be accomplished using the Postgres logical replication feature.
- On the flip side, if you want changes to be mirrored in a destination beyond the PostgreSQL instance where the trigger operates, you’ll require a separate data pipeline. This secondary pipeline will search for changes and update the target database accordingly.
- The process of establishing and overseeing triggers and multiple data replication pipelines for the target database can result in heightened operational challenges and complexity.

### 2. Queries or Timestamp Column

The Query-based method in Postgres CDC involves tracking changes by querying an update timestamp column in the monitored database table that indicates the last time a row was changed. For this custom method you must have a timestamp column in your table. Database designers usually name such columns as LAST_UPDATE, DATE_MODIFIED, etc. Whenever a record is inserted or modified, the update timestamp column is updated to reflect the date and time of the change. Recurring queries are made to PostgreSQL using this timestamp column to fetch all records that have been modified since the last query, effectively capturing changes made to the data. Alternatively, scripts are also used to monitor changes in the timestamp column and record these changes in a target database. This approach is, however, effort-intensive and would demand a lot of time and work from the developer.

#### Advantages of Query-based Postgres CDC

- It is an easy method.
- You can construct it using your own application logic.
- No external tools are necessary.

#### Disadvantages of Query-based Postgres CDC

- To implement query-based CDC, there must be a column (such as LAST_UPDATE) that tracks the time of the last modification for each record in the table.
- Query-based CDC in Postgres introduces extra overhead to the database.
- This Postgres CDC method necessitates usage of CPU resources for scanning tables to identify altered data and maintenance resources to ensure the consistent application of the LAST_UPDATE column across all source tables.
- Query-based CDC in Postgres is prone to errors and can lead to issues with data consistency.
- Implementing CDC in PostgreSQL based on queries can be achieved without making any alterations to the existing schema, provided that the tables include a timestamp column indicating when rows were last modified.
- Query-based CDC implementations rely on the query layer for data extraction, which imposes additional strain on the PostgreSQL database.
- The absence of a LAST_UPDATE timestamp for deleted rows means that DML operations like “DELETE” won’t be transmitted to the target database unless supplementary scripts are employed to track deletions.

### 3. Logical Decoding

Postgres Logical Replication also known as Logical Decoding in PostgreSQL, captures and records all database activities using the Write-Ahead Log (WAL). This feature has been available since PostgreSQL version 9.4, enabling efficient and secure data replication between different PostgreSQL instances, even on separate physical machines. It operates by creating a log of database activities without impacting performance. To implement it, an output plugin is installed, and a subscription model with publishers and subscribers is used.
For versions older than 10, you need to manually install plugins like wal2json or decoderbufs, while version 10 and later include the default pgoutput plugin. Additionally, output plugins can transform events, such as INSERTs, UPDATEs, and DELETEs, into more user-friendly formats like JSON. However, it’s essential to note that table creation and modification steps are not captured by these events. Many managed PostgreSQL services, including AWS RDS, Google Cloud SQL, and Azure Database, support Logical Replication. The following list outlines the pros and cons of employing PostgreSQL’s Logical Replication for implementing Change Data Capture.

#### Advantages of Postgres Logical Replication for CDC

- Leveraging log-based CDC facilitates the real-time capture of data changes in an event-driven manner. This ensures that downstream applications consistently access the most up-to-date data from PostgreSQL.
- Log-based CDC has the capability to detect all types of change events within PostgreSQL, including INSERTs, UPDATEs, and DELETEs.
- Consuming events through Logical Replication essentially involves direct access to the file system, preserving the performance of the PostgreSQL database.

#### Disadvantages of Postgres Logical Replication for CDC

- One should note that Logical Replication is not available in very old versions of PostgreSQL, specifically those predating version 9.4.
- Developers are required to devise complex logic for processing these events and subsequently converting them into statements for the target database. Depending on the specific use case, this may extend project timelines.

### 4. Table Differencing

Another Postgres CDC approach involves using utilities like table ‘tablediff’ to compare data between two tables to identify mismatched rows. Subsequently, scripts can be employed to apply these differences from the source table to the target table. While this method is more effective than ‘Timestamps’ CDC for handling deleted rows, it has its shortcomings.

The incremental or table differencing method involves comparing a copy of the source table with a previous version of the same table to identify any variances. To achieve this, two copies of the table need to be kept in the database. This process is conducted at regular intervals to capture disparities between the tables, delivering the most recent inserts and updates found in the new version of the table. This is achieved through the utilization of native SQL scripts, ensuring a precise representation of alterations.

You can use the below query to compare the two similar tables using MINUS operator. It returns all rows in table “Source Table” that do not exist or changed in the other table.

```SQL
SELECT * FROM <schema>.<"source_table_name">
MINUS
SELECT * FROM <schema>.<"old_version_source_table_name">;
```

One major issue is the significant CPU resource consumption required to identify differences, and this overhead increases proportionally with the volume of data. Analytics queries against the source database or production environment can also impact application performance negatively. To mitigate these problems, some choose to periodically export the database to a staging environment for comparison. However, this approach results in escalating transfer costs as data volumes grow.

Moreover, the Table Diff method is incapable of capturing intermediate changes in data. For instance, if someone updates a field but subsequently reverts it to its original value, a simple comparison won’t capture these change events. Additionally, the diff method introduces latency in the Postgres CDC process and cannot operate in real-time.

#### Advantages of Table Differencing in Postgres CDC

- It offers a precise view of modified data exclusively through the use of native SQL scripts.

#### Disadvantages of Table Differencing in Postgres CDC

- The need for storage capacity grows due to the requirement of maintaining three copies of the data sources utilized in this Postgres CDC method: the original data, the previous snapshot, and the current snapshot.
- As a Postgres CDC method, Table Diff struggles to perform efficiently in applications characterized by high transactional workloads.
