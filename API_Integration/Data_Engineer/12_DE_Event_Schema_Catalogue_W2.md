# Event Schema Catalogue — Template & Best Practices

**Priority:** 12 — Register schemas before any producer publishes
**Owner:** Data Engineer
**Phase:** 0 — Week 2; one entry per Kafka topic

---

## Purpose

The Event Schema Catalogue is the authoritative registry of every Kafka topic in the platform — its schema, producers, consumers, versioning history, and operational metadata. No topic goes to production without an entry here.

---

## Document Metadata

| Field | Value |
|---|---|
| Document Owner | |
| Last Updated | |
| Version | 1.0 |
| Review Cycle | Every sprint |
| Schema Registry URL | |

---

## Topic Master List

Quick-reference index of all topics:

| Topic Name | Domain | Event Type | Producer | Consumers | Version | Status |
|---|---|---|---|---|---|---|
| hr.employee.hired | HR | EmployeeHired | hr-service | finance-service, it-provisioning | 1.0 | Active |
| hr.employee.terminated | HR | EmployeeTerminated | hr-service | finance-service, it-provisioning, payroll | 1.0 | Active |
| finance.invoice.approved | Finance | InvoiceApproved | finance-service | erp-service, reporting-service | 1.1 | Active |
| | | | | | | |

---

## Schema Entry Template

Copy this block for each Kafka topic.

---

### Topic: `{domain}.{entity}.{event}`

#### Topic Metadata

| Field | Value |
|---|---|
| **Topic Name** | hr.employee.hired |
| **Domain** | HR |
| **Event Type** | EmployeeHired |
| **Description** | Published when a new employee record is created and confirmed in the HR system |
| **Trigger** | HR admin saves a new employee record with status = Active |
| **Producer Service** | hr-service |
| **Consumer Services** | finance-service, it-provisioning-service, payroll-service |
| **Schema Format** | Avro |
| **Schema Registry Subject** | hr.employee.hired-value |
| **Current Schema Version** | 1.0 |
| **Kafka Partition Key** | employee_id |
| **Partition Count** | 6 |
| **Replication Factor** | 3 |
| **Retention Period** | 7 days |
| **Compaction Policy** | Delete (time-based) |
| **Max Message Size** | 1 MB |
| **Throughput Estimate** | ~50 events/day average; ~200 peak |
| **Criticality** | Business-critical |
| **SLA** | Consumer must process within 5 minutes of publish |
| **DLQ Topic** | hr.employee.hired.dlq |
| **Status** | Active |
| **Created Date** | |
| **Schema Owner** | |

---

#### Event Envelope

All events must include the standard envelope (CloudEvents-aligned):

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "EmployeeHired",
  "event_version": "1.0",
  "source_system": "hr-service",
  "timestamp": "2026-05-20T10:00:00Z",
  "correlation_id": "7f3d9a20-b123-4c56-8901-abcdef012345",
  "payload": {}
}
```

---

#### Avro Schema (v1.0)

```json
{
  "type": "record",
  "name": "EmployeeHired",
  "namespace": "com.example.hr",
  "doc": "Published when a new employee record is confirmed in the HR system",
  "fields": [
    {
      "name": "event_id",
      "type": "string",
      "doc": "UUID v4 unique identifier for this event"
    },
    {
      "name": "event_type",
      "type": "string",
      "default": "EmployeeHired"
    },
    {
      "name": "event_version",
      "type": "string",
      "default": "1.0"
    },
    {
      "name": "source_system",
      "type": "string",
      "doc": "Name of the service that published this event"
    },
    {
      "name": "timestamp",
      "type": "string",
      "doc": "ISO 8601 UTC timestamp of when the event occurred"
    },
    {
      "name": "correlation_id",
      "type": ["null", "string"],
      "default": null,
      "doc": "Used to trace this event across services"
    },
    {
      "name": "payload",
      "type": {
        "type": "record",
        "name": "EmployeeHiredPayload",
        "fields": [
          {"name": "employee_id",      "type": "string",           "doc": "UUID v4 — canonical employee identifier"},
          {"name": "first_name",       "type": "string",           "doc": "Legal first name — PII"},
          {"name": "last_name",        "type": "string",           "doc": "Legal last name — PII"},
          {"name": "email",            "type": "string",           "doc": "Work email address — PII"},
          {"name": "hire_date",        "type": "string",           "doc": "ISO 8601 date (YYYY-MM-DD)"},
          {"name": "department_code",  "type": "string",           "doc": "Department reference code"},
          {"name": "employment_type",  "type": "string",           "doc": "FULL_TIME | PART_TIME | CONTRACTOR | INTERN"},
          {"name": "salary",           "type": ["null", "double"], "default": null, "doc": "Annual base salary — Sensitive. Null for contractors"},
          {"name": "currency_code",    "type": ["null", "string"], "default": null, "doc": "ISO 4217 currency code"}
        ]
      }
    }
  ]
}
```

---

#### Sample Event Payload

```json
{
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "event_type": "EmployeeHired",
  "event_version": "1.0",
  "source_system": "hr-service",
  "timestamp": "2026-05-20T09:15:00Z",
  "correlation_id": "7f3d9a20-b123-4c56-8901-abcdef012345",
  "payload": {
    "employee_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "first_name": "Jane",
    "last_name": "Smith",
    "email": "jane.smith@example.com",
    "hire_date": "2026-06-01",
    "department_code": "ENG-001",
    "employment_type": "FULL_TIME",
    "salary": 95000.00,
    "currency_code": "USD"
  }
}
```

---

#### Field-Level PII Map

| Field | PII? | Classification | Masking in Transit | Masking at Rest |
|---|---|---|---|---|
| employee_id | No | None | None | None |
| first_name | Yes | PII / Name | Hash in non-prod | Hash in non-prod |
| last_name | Yes | PII / Name | Hash in non-prod | Hash in non-prod |
| email | Yes | PII / Email | Tokenise in non-prod | Tokenise in non-prod |
| hire_date | No | None | None | None |
| department_code | No | None | None | None |
| employment_type | No | None | None | None |
| salary | Yes | Sensitive / Financial | Redact in non-prod | Redact in non-prod |
| currency_code | No | None | None | None |

---

#### Consumer Contracts

| Consumer Service | Fields Consumed | Latency Requirement | Idempotent? | DLQ Handler |
|---|---|---|---|---|
| finance-service | employee_id, hire_date, salary, currency_code | < 5 minutes | Yes (employee_id) | finance team |
| it-provisioning-service | employee_id, email, department_code | < 5 minutes | Yes (employee_id) | DevOps team |
| payroll-service | employee_id, hire_date, salary, currency_code, employment_type | < 1 hour | Yes (employee_id) | Payroll team |

---

#### Schema Version History

| Version | Date | Author | Change Type | Change Description |
|---|---|---|---|---|
| 1.0 | | | Initial | Initial schema release |
| | | | | |

**Change Types:** `non-breaking-addition` / `deprecation` / `breaking` (breaking = new topic version)

---

#### Breaking Change Process

1. Data Engineer proposes change in PR with impact analysis
2. All consumer team leads notified minimum **2 sprints** in advance
3. Integration Architect approves
4. New schema version registered in Schema Registry
5. Old version deprecated with sunset date communicated
6. Consumers migrate before sunset date
7. Old schema version removed from registry after all consumers migrated

---

## Schema Health Checklist

Run before registering any new schema:

```
[ ] Schema registered in Schema Registry (not just documented here)
[ ] Avro schema passes compatibility check (BACKWARD compatible)
[ ] Sample payload validated against schema
[ ] All PII fields identified and masking rules confirmed with compliance
[ ] DLQ topic created and named correctly ({topic-name}.dlq)
[ ] Consumer contracts reviewed and signed off by consumer team leads
[ ] Retention period confirmed with data engineer and compliance
[ ] Partition key chosen intentionally (not random) — affects ordering guarantees
[ ] AsyncAPI spec updated to reflect this topic
[ ] Data Dictionary updated for all fields in payload
```
