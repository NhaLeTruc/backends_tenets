# Event Schema Design

**Priority:** 2 — Contracts must be agreed before any producer or consumer is built
**Phase:** 0 — Discovery & Design (Week 2–3)

---

## Purpose

Define and document the shape of every event that flows through Kafka. Schema agreements prevent rework and producer/consumer mismatches downstream.

---

## Methodology: Domain-Driven Design (DDD) + Event Storming

**Event Storming** (by Alberto Brandolini) is the most widely used technique for discovering events in a system.

### How to Run an Event Storming Session

1. Get developers, BAs, and domain experts in one room (or virtual board — Miro/Mural)
2. Use sticky notes by colour:
   - **Orange** — Domain Events (things that happened: `EmployeeHired`, `InvoiceApproved`)
   - **Blue** — Commands (actions that trigger events: `HireEmployee`)
   - **Yellow** — Actors (who triggers it: HR Manager, System)
   - **Pink** — External Systems (SAP, Salesforce)
3. Arrange on a timeline left to right
4. Identify bounded contexts — clusters of related events become Kafka topics

---

## Standard Event Envelope

All events must include this base envelope before the business payload:

```json
{
  "event_id": "uuid-v4",
  "event_type": "EmployeeHired",
  "event_version": "1.0",
  "source_system": "hr-service",
  "timestamp": "2026-05-20T10:00:00Z",
  "correlation_id": "uuid-v4",
  "payload": {}
}
```

> Adopt **CloudEvents spec** (cloudevents.io) as the envelope standard — vendor-neutral and widely supported.

---

## Schema Design Checklist

```
[ ] Event name follows past-tense verb convention (EmployeeHired, not HireEmployee)
[ ] Schema format chosen: Avro (Kafka standard) or JSON Schema
[ ] Required fields defined: event_id, event_type, timestamp, source_system, version
[ ] Business payload fields documented with types and nullability
[ ] Versioning strategy agreed: backward-compatible changes only?
[ ] Schema registered in Schema Registry before first publish
[ ] Breaking change process documented (new topic vs. version bump)
[ ] Consumer team has reviewed and signed off on schema
[ ] Sample payload written and reviewed
[ ] PII fields identified and masking/encryption decided
```

---

## Schema Versioning Rules

| Change Type | Safe? | Action |
|---|---|---|
| Add optional field | Yes | Bump minor version (1.0 → 1.1) |
| Add required field | No | New topic version or negotiated migration |
| Rename field | No | Deprecate old field, add new field, migrate consumers |
| Remove field | No | Deprecate first, remove after all consumers updated |
| Change field type | No | Treat as breaking change |

---

## Kafka Topic Naming Convention

```
{domain}.{entity}.{event}

Examples:
  hr.employee.hired
  finance.invoice.approved
  inventory.product.updated
```

---

## Schema Catalogue Template

| Field | Details |
|---|---|
| Topic Name | hr.employee.hired |
| Event Type | EmployeeHired |
| Schema Version | 1.0 |
| Producer Service | hr-service |
| Consumer Services | finance-service, it-provisioning-service |
| Schema Format | Avro / JSON Schema |
| PII Fields | email, national_id |
| Retention Policy | 7 days |
| Schema Registry ID | |

---

## Output of This Step

- Event catalogue (all events, topics, producers, consumers)
- Registered schemas in Schema Registry
- AsyncAPI spec per Kafka topic
- PII and data sensitivity map

---

## References

- CloudEvents Spec — cloudevents.io
- AsyncAPI 2.x — asyncapi.com
- Confluent Schema Registry Docs — docs.confluent.io
- Event Storming — eventstorming.com (Alberto Brandolini)
- *Designing Data-Intensive Applications* — Martin Kleppmann
