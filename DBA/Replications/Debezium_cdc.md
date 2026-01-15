# Notes on Debezium Connectors managed cdc pipeline

Yes, in a CDC pipeline managed by Debezium connectors, the sink PostgreSQL database's pg_subscription would be empty.

Here's why:

Debezium uses a different replication mechanism than PostgreSQL native logical replication:

Debezium approach: Debezium reads changes from the source database (SQL Server in your case) via its native CDC/log mechanisms, publishes them to Kafka, and then a Kafka Connect sink connector (like the JDBC sink) writes them to PostgreSQL using standard SQL INSERT/UPDATE/DELETE statements.

PostgreSQL native logical replication: pg_subscription is part of PostgreSQL's built-in logical replication system, where PostgreSQL subscribes directly to a publication on another PostgreSQL server using the CREATE SUBSCRIPTION command.

So your sink PostgreSQL sees the incoming data as regular DML operations from the Kafka Connect sink connector, not as a logical replication subscription. The pg_subscription catalog will remain empty unless you've separately configured native PostgreSQL logical replication for something else.

