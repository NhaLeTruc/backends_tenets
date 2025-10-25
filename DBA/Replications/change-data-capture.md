# Change Data Capture (CDC)

## Overview

Change Data Capture (CDC) is a design pattern that tracks and captures changes made to data in a database, enabling real-time data integration and synchronization between systems.

## Key Concepts

### Types of CDC

- Log-based CDC
- Trigger-based CDC
- Timestamp-based CDC
- Snapshot-based CDC

### Core Benefits

- Real-time data replication
- Minimal impact on source systems
- Reduced load on databases
- Audit trail capabilities
- Data consistency across systems

## Implementation Approaches

### Database-Level CDC

- Oracle CDC
- SQL Server CDC
- PostgreSQL logical replication
- MySQL binlog

### Tool-Based CDC

- Debezium
- Apache Kafka Connect
- Attunity
- Striim

## Best Practices

1. Monitor CDC performance
2. Handle failure scenarios
3. Maintain data consistency
4. Consider data retention policies
5. Plan for scalability

## Common Use Cases

- Data replication
- ETL processes
- Microservices data synchronization
- Real-time analytics
- Audit logging

-----------------------------------

## PostgreSQL Overview

Change Data Capture (CDC) is a design pattern that tracks and captures changes made to data in a database, enabling other systems to respond to those changes in real-time or near real-time. CDC is crucial for data integration, replication, and building event-driven architectures.

## Core Concepts

- **Change tracking**: Monitoring inserts, updates, and deletes
- **Change capture**: Recording the changes with metadata
- **Change delivery**: Propagating changes to target systems
- **Consistency**: Ensuring data integrity across systems

## PostgreSQL CDC Approaches

### 1. Write-Ahead Log (WAL) Based

PostgreSQL's WAL can be used to capture changes at the transaction level.

```sql
-- Enable logical replication
ALTER SYSTEM SET wal_level = logical;

-- Create publication for specific tables
CREATE PUBLICATION my_publication FOR TABLE users, orders;

-- Create replication slot
SELECT pg_create_logical_replication_slot('my_slot', 'pgoutput');
```

Key tools:

- **Debezium**: Popular open-source platform
- **wal2json**: Converts WAL to JSON format
- **pgoutput**: Native logical decoding plugin

### 2. Trigger-Based Approach

```sql
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log(table_name, operation, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(NEW));
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log(table_name, operation, old_data, new_data)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log(table_name, operation, old_data)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD));
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### 3. Application-Level CDC

- Dual-write pattern
- Outbox pattern using message queues
- Event sourcing with append-only logs

### Best Practices

1. Monitor replication lag
2. Handle schema changes gracefully
3. Implement error handling and retry mechanisms
4. Consider impact on database performance
5. Plan for scaling and high availability

### Common Tools

- Debezium
- AWS DMS
- Kafka Connect
- Airbyte
- Fivetran

## Performance Considerations

- WAL-based CDC has minimal impact on source database
- Trigger-based approach adds overhead to transactions
- Consider batch processing for high-volume changes
- Monitor disk space for audit logs
