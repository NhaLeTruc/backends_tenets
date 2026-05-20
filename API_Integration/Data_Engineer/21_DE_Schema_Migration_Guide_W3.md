# Schema Migration Guide — Template & Best Practices

**Priority:** 21 — Prevents breaking consumers when schemas evolve
**Owner:** Data Engineer
**Phase:** 0 — Procedures agreed before first schema is registered; executed as needed

---

## Purpose

Documents the process for safely evolving Kafka event schemas and PostgreSQL table schemas without breaking existing consumers or losing data. Schema changes are one of the highest-risk activities in an integration platform.

---

## Document Metadata

| Field | Value |
|---|---|
| Document Owner | |
| Last Updated | |
| Version | 1.0 |
| Schema Registry URL | |
| Compatibility Mode | BACKWARD (recommended default) |

---

## Part 1 — Kafka Schema (Avro) Migrations

### Compatibility Modes

Configure the Schema Registry to enforce the chosen compatibility mode per subject.

| Mode | What It Allows | Recommended For |
|---|---|---|
| **BACKWARD** (recommended) | New schema can read data written by previous schema | Most integrations — consumers upgrade first |
| **FORWARD** | Previous schema can read data written by new schema | Producers upgrade before consumers |
| **FULL** | Both backward and forward compatible | High-stability, long-lived topics |
| **NONE** | No compatibility check | Only for development topics — never production |

**Default:** Set `BACKWARD` on all production topics.

---

### What Is and Is Not a Breaking Change

| Change | Breaking? | Safe Under BACKWARD? |
|---|---|---|
| Add optional field with default | No | Yes |
| Add optional field without default | No | Yes (Avro uses null union) |
| Add required field (no default) | **Yes** | No — old data cannot be read |
| Remove a field | **Yes** | No — consumers expecting the field will fail |
| Rename a field | **Yes** | No — rename = remove + add |
| Change field type (e.g. int → string) | **Yes** | No |
| Change field from required to optional | No | Yes |
| Add a new enum value | **Yes** | No — old consumers may not handle it |
| Remove an enum value | **Yes** | No |

---

### Non-Breaking Change Process (Add Optional Field)

Use this for: adding a new optional field to an existing schema.

```
1. Update the Avro schema (add new field with default value or null union)
2. Register new schema version in Schema Registry
   → Schema Registry validates BACKWARD compatibility automatically
   → Reject if not compatible
3. Update Event Schema Catalogue (12_DE_Event_Schema_Catalogue_W2.md)
4. Update Data Dictionary (11_DE_Data_Dictionary_W1.md)
5. Update Data Lineage Map (14_DE_Data_Lineage_Map_W2.md)
6. Update Transformation Specs if the new field is consumed
7. Deploy producer with new field populated
8. Notify consumers of the new optional field (they can adopt at their own pace)
```

**Timeline:** Can be done in one sprint. No consumer coordination required.

---

### Breaking Change Process (New Topic Version)

Use this for: any breaking change — field removal, rename, type change, new required field.

```
Timeline: minimum 2 sprints (4 weeks)

Sprint N (Announce):
[ ] Data Engineer proposes change via PR — includes impact analysis
[ ] All consumer team leads notified in writing
[ ] Breaking change reviewed and approved by Integration Architect
[ ] Migration timeline agreed with all consumer teams

Sprint N+1 (Prepare):
[ ] New schema version registered as a NEW SUBJECT in Schema Registry
    (e.g. hr.employee.hired.v2-value, not hr.employee.hired-value)
[ ] New Kafka topic created: hr.employee.hired.v2
[ ] Producer updated to publish to BOTH v1 and v2 topics (dual-publish)
[ ] Consumer teams begin migration to v2 topic

Sprint N+2 (Cutover):
[ ] Verify all consumers reading from v2 topic (zero lag on v2, zero active on v1)
[ ] Stop dual-publishing — producer publishes to v2 only
[ ] v1 topic retention expires naturally (do not delete immediately)
[ ] v1 topic and schema deprecated in catalogue

Sprint N+3+ (Cleanup):
[ ] After v1 retention period has elapsed:
    [ ] Delete v1 topic
    [ ] Archive v1 schema in Schema Registry (set to DEPRECATED)
    [ ] Remove v1 consumer code from all services
    [ ] Update all documentation to reference v2 only
```

---

### Schema Registry CLI Commands

```bash
# Check current compatibility for a subject
curl -X GET http://schema-registry:8081/config/hr.employee.hired-value

# Set compatibility mode for a subject
curl -X PUT http://schema-registry:8081/config/hr.employee.hired-value \
  -H "Content-Type: application/json" \
  -d '{"compatibility": "BACKWARD"}'

# Register a new schema version
curl -X POST http://schema-registry:8081/subjects/hr.employee.hired-value/versions \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "<escaped-avro-schema-json>"}'

# Check if a schema is compatible before registering
curl -X POST http://schema-registry:8081/compatibility/subjects/hr.employee.hired-value/versions/latest \
  -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "<escaped-avro-schema-json>"}'

# List all versions of a subject
curl -X GET http://schema-registry:8081/subjects/hr.employee.hired-value/versions

# Get a specific version
curl -X GET http://schema-registry:8081/subjects/hr.employee.hired-value/versions/2
```

---

## Part 2 — PostgreSQL Table Migrations

Use **Flyway** or **Liquibase** for versioned, repeatable database migrations. Never alter tables manually in production.

### Migration File Naming Convention

```
Flyway:   V{version}__{description}.sql
Examples:
  V1__create_employees_table.sql
  V2__add_manager_id_to_employees.sql
  V3__create_index_employees_email.sql

Liquibase:
  db/changelog/changes/0001-create-employees-table.xml
```

### Safe Migration Patterns

| Operation | Safe Online? | Recommended Approach |
|---|---|---|
| Add nullable column | Yes | `ALTER TABLE employees ADD COLUMN manager_id UUID` |
| Add NOT NULL column with default | Yes (Postgres 11+) | `ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'` |
| Add NOT NULL column without default | No — locks table | Add as nullable first, backfill values, add NOT NULL constraint |
| Drop column | No — may break code | Deprecate in code first, then drop in a later migration |
| Rename column | No — breaks all queries | Add new column, dual-write, migrate reads, drop old column |
| Add index | Yes (use CONCURRENTLY) | `CREATE INDEX CONCURRENTLY idx_employees_email ON employees(email)` |
| Add foreign key | Risky on large tables | Add as NOT VALID, validate separately |
| Change column type | Depends | Add new column + migrate data + swap |

### Migration Checklist

```
[ ] Migration file follows naming convention
[ ] Migration is idempotent (safe to run twice — use IF NOT EXISTS, IF EXISTS)
[ ] Large table operations use CONCURRENTLY or are batched
[ ] Migration tested in dev → staging → prod (never skip staging)
[ ] Rollback SQL documented if migration is not auto-reversible
[ ] Transformation Specs updated if field names or types changed
[ ] Data Lineage Map updated
[ ] Application code deployed before migration runs (for column additions)
   OR after migration runs (for column removals)
[ ] Zero-downtime deployment plan confirmed with DevOps
```

### Flyway Migration Template

```sql
-- V2__add_manager_id_to_employees.sql
-- Adds optional manager_id foreign key to employees table
-- Safe: nullable column addition, no lock

ALTER TABLE employees
ADD COLUMN IF NOT EXISTS manager_id UUID;

COMMENT ON COLUMN employees.manager_id
    IS 'FK to employees.employee_id — the direct manager. Null for top-level employees.';
```

---

## Schema Migration Log

Track all schema changes across Kafka and PostgreSQL:

| Migration ID | Type | Subject / Table | Version / File | Change Type | Breaking? | Date | Author | Status |
|---|---|---|---|---|---|---|---|---|
| SM-001 | Kafka | hr.employee.hired | v1.0 | Initial | N/A | | | Done |
| SM-002 | PostgreSQL | employees | V1__create_employees_table.sql | Initial | N/A | | | Done |
| SM-003 | PostgreSQL | employees | V2__add_manager_id.sql | Add column | No | | | Planned |
| | | | | | | | | |
