# CDC and DDL statements

## How do cdc methods handle DDL statements

Change Data Capture (CDC) methods handle Data Definition Language (DDL) statements in various ways, depending on the specific CDC implementation and the type of DDL operation.

### General Approaches

Detection and Controlled Shutdown: Many CDC systems detect DDL changes that affect the structure of tracked tables. When such a DDL statement is encountered, the CDC replication for the affected subscription or table may initiate a controlled shutdown. This ensures that all transactions up to the point of the DDL change are applied to the target before replication stops. The system typically logs an error or warning indicating the DDL change and the shutdown.

### Metadata Update Requirement

After a DDL change, the CDC system's metadata, which describes the source table's structure, often needs to be updated to reflect the new definition. Failing to update the metadata can lead to errors in log reading and potential data loss if subsequent DML operations are not correctly interpreted.

### Specific DDL Handling

The behavior can vary based on the DDL operation:

- **Adding Columns**: Some CDC systems may continue tracking changes but ignore the new column until the metadata is updated. Others might require a re-synchronization or a specific update process to include the new column in the replication.
- **Dropping Columns**: CDC might continue tracking, but replicate NULL values for the dropped column in change tables until the metadata is updated.
- **Modifying Column Data Types or Lengths**: This often requires metadata updates and potentially re-initialization or specific handling to ensure data integrity during replication.
- **Creating, Dropping, or Renaming Tables**: These operations typically require explicit configuration or re-configuration within the CDC system to include or exclude the affected tables from replication.

### Examples of Specific CDC Implementations

- **SQL Server CDC**: Primarily designed for DML, it can capture certain DDL operations like adding, dropping, or altering columns on tracked tables. Other DDL operations, such as creating or dropping tables, may not be directly captured by the CDC feature itself but require manual intervention or external mechanisms.
- **Oracle CDC Connector (e.g., for Confluent Platform)**: Offers configuration options like oracle.dictionary.mode to handle DDL changes. In auto mode, it can dynamically switch between using the online catalog and archived redo logs to process DDL statements and then revert.
- **IBM CDC Replication**: Detects DDL changes, initiates a controlled shutdown, and requires the user to update table definitions in the metadata to continue replication after a DDL event.

> In summary, while CDC primarily focuses on DML operations, DDL statements are handled through detection, controlled shutdowns, and a requirement for metadata updates to ensure continued and accurate data replication.

---
---

## How do cdc methods handle schema evolution

### Common approaches

- **Schema Registries**: Tools like Avro and Protobuf are often used with a schema registry (e.g., Confluent Schema Registry) to enforce compatibility rules and manage schema versions, ensuring data consistency across the pipeline.
- **Automated Detection and Restart**: Some CDC connectors automatically detect schema changes and restart the pipeline to resolve issues like added columns or renamed columns.
- **Transformations**: Transformations are used to handle specific changes:
- **New columns**: Added columns can be set to a default value or handled by the new schema.
- **Dropped columns**: Dropped columns are often handled as "soft deletes," where new rows are populated with NULL for the deleted column.
- **Renamed columns**: A lookup table or mapping can be used to map the new column name to the old one to maintain consistency downstream.
- **Dynamic Schema Application**: Dynamic schemas can be handled by using a control table to store schema definitions and applying them to incoming CDC events, often using functions like from_json().
- **Evolve Mode**: In some systems like Apache Flink CDC, a specific "evolve mode" automatically applies upstream schema change events to the downstream sink, failing the pipeline if a compatibility issue arises.
- **Schema Validation**: You can implement schema validation early in the process to catch mismatches, either by pausing the pipeline to alert developers or by applying automated transformations.
- **Monitoring and Alerting**: Monitoring tools provide dashboards and alerts to track schema changes, errors, and pipeline health, allowing for faster troubleshooting and proactive problem-solving.
- **Contract Testing**: Contract testing can be used to ensure that source and destination systems maintain compatibility guarantees and avoid breaking changes

---
