# Data Lineage Map — Template & Best Practices

**Priority:** 14 — Proves data traceability for debugging, auditing, and compliance
**Owner:** Data Engineer
**Phase:** 0 — Week 2; updated as each integration is built

---

## Purpose

The Data Lineage Map documents where every piece of data originates, how it is transformed, and where it lands. It is the primary tool for debugging data issues, satisfying compliance audits, and understanding the blast radius of a schema change.

---

## Document Metadata

| Field | Value |
|---|---|
| Document Owner | |
| Last Updated | |
| Version | 1.0 |
| Review Cycle | Updated per integration; quarterly review |
| Approved By | |

---

## System-Level Lineage Diagram

Document the high-level flow across all systems before going field-level.

```
┌─────────────┐     REST/DB      ┌──────────────────┐    Kafka Topic      ┌───────────────────┐
│  HR System  │ ──────────────►  │  hr-service      │ ─────────────────►  │ hr.employee.hired │
│  (Source)   │                  │  (Producer)      │                     │  (Kafka Topic)    │
└─────────────┘                  └──────────────────┘                     └─────────┬─────────┘
                                                                                     │
                              ┌──────────────────────────────────────────────────────┤
                              │                              │                        │
                              ▼                              ▼                        ▼
                  ┌───────────────────┐        ┌──────────────────────┐   ┌──────────────────────┐
                  │  finance-service  │        │ it-provisioning-svc  │   │   payroll-service    │
                  │  (Consumer)       │        │  (Consumer)          │   │   (Consumer)         │
                  └────────┬──────────┘        └──────────┬───────────┘   └──────────┬───────────┘
                           │                              │                           │
                           ▼                              ▼                           ▼
                  ┌────────────────┐          ┌────────────────────┐      ┌────────────────────┐
                  │  PostgreSQL    │          │  Active Directory   │      │  PostgreSQL        │
                  │  finance_db    │          │  (Provisioning)     │      │  payroll_db        │
                  └────────────────┘          └────────────────────┘      └────────────────────┘
```

---

## Integration Lineage Entry Template

One entry per integration. Copy this block for each.

---

### Integration: HR Employee Hired → Finance Service

#### Summary

| Field | Value |
|---|---|
| **Integration ID** | INT-001 |
| **Source System** | HR System |
| **Producer Service** | hr-service |
| **Kafka Topic** | hr.employee.hired |
| **Consumer Service** | finance-service |
| **Target System** | PostgreSQL — finance_db |
| **Target Table** | employees |
| **Trigger** | EmployeeHired event on Kafka topic |
| **Frequency** | Real-time (event-driven) |
| **Latency SLA** | < 5 minutes from event publish to DB write |
| **Transformation Applied** | Yes — field renaming, type conversion, enrichment |

---

#### Field-Level Lineage Table

| Source System | Source Table / Object | Source Field | Transformation | Target Table | Target Field | Target Type | Notes |
|---|---|---|---|---|---|---|---|
| HR System | Employee | EmpID | Cast integer → UUID v4 | employees | employee_id | UUID | See transform spec TRF-001 |
| HR System | Employee | FirstName | None | employees | first_name | VARCHAR(100) | PII — hashed in non-prod |
| HR System | Employee | LastName | None | employees | last_name | VARCHAR(100) | PII — hashed in non-prod |
| HR System | Employee | WorkEmail | Lowercase + trim | employees | email | VARCHAR(254) | PII — tokenised in non-prod |
| HR System | Employee | HireDate | Parse string → Date | employees | hire_date | DATE | ISO 8601 |
| HR System | Employee | DeptCode | None | employees | department_code | VARCHAR(10) | |
| HR System | Employee | EmpType | None | employees | employment_type | VARCHAR(20) | Validated against enum |
| Finance System | SalaryTable | BaseSalary | None | employees | salary | DECIMAL(15,2) | Null for contractors |
| Finance System | SalaryTable | CurrencyCode | None | employees | currency_code | CHAR(3) | ISO 4217 |
| hr-service (derived) | — | — | `NOW()` at consume time | employees | created_at | TIMESTAMPTZ | Insert timestamp |
| hr-service (derived) | — | — | `NOW()` at consume time | employees | updated_at | TIMESTAMPTZ | Last updated timestamp |
| Kafka envelope | — | event_id | None | employees | source_event_id | UUID | For idempotency and audit |

---

#### Lineage Narrative

```
1. HR admin creates employee in HR System (EmpID: 12345)
2. hr-service polls HR System REST API every 60 seconds for new employees
3. hr-service converts EmpID (integer) to UUID, constructs EmployeeHired event
4. hr-service publishes event to hr.employee.hired (Kafka) — partitioned by employee_id
5. finance-service consumes event from hr.employee.hired
6. finance-service validates payload against Data Quality Rules (DQR-001 to DQR-016)
7. finance-service maps source fields to finance_db.employees schema
8. finance-service checks idempotency: if source_event_id already exists in employees table, skip
9. finance-service writes new row to finance_db.employees
10. finance-service emits dq_records_total and processing latency metrics to Prometheus
```

---

#### Data Transformation Steps

| Step | Type | Description |
|---|---|---|
| 1 | Type conversion | EmpID integer → UUID v4 string |
| 2 | Normalisation | WorkEmail → lowercase + whitespace trim |
| 3 | Type conversion | HireDate string → ISO 8601 Date |
| 4 | Validation | employment_type → check against allowed enum |
| 5 | Enrichment | Add created_at and updated_at timestamps |
| 6 | Idempotency | Check source_event_id before insert |

---

#### PII Lineage

| PII Field | Source | In Transit (Kafka) | In Kafka (prod) | In PostgreSQL (prod) | In PostgreSQL (non-prod) |
|---|---|---|---|---|---|
| first_name | HR System | Encrypted (TLS) | Plaintext | Plaintext | Hashed |
| last_name | HR System | Encrypted (TLS) | Plaintext | Plaintext | Hashed |
| email | HR System | Encrypted (TLS) | Plaintext | Plaintext | Tokenised |
| salary | Finance System | Encrypted (TLS) | Plaintext | Plaintext | Redacted |

---

#### Audit Trail

Every row written to the target table must carry:

| Column | Value | Purpose |
|---|---|---|
| source_event_id | UUID from Kafka envelope | Trace back to originating event |
| source_system | "hr-service" | Identifies data origin |
| created_at | Timestamp at insert | When the record was created |
| updated_at | Timestamp at last update | When the record was last modified |
| _is_deleted | Boolean | Soft-delete flag (never hard-delete) |

---

## Lineage Master Index

Quick reference across all integrations:

| Integration ID | Source System | Topic | Consumer | Target | Last Updated |
|---|---|---|---|---|---|
| INT-001 | HR System | hr.employee.hired | finance-service | finance_db.employees | |
| INT-002 | HR System | hr.employee.hired | it-provisioning-service | Active Directory | |
| INT-003 | HR System | hr.employee.terminated | finance-service | finance_db.employees | |
| INT-004 | Finance System | finance.invoice.approved | erp-service | erp_db.invoices | |
| | | | | | |

---

## Lineage Review Checklist

Run when adding or changing any integration:

```
[ ] System-level diagram updated
[ ] Field-level lineage table complete for all fields
[ ] PII lineage documented (in transit, at rest, per environment)
[ ] Audit columns present in target table (source_event_id, created_at, updated_at)
[ ] Transformation steps documented and cross-referenced to Transformation Specs
[ ] Data Dictionary entries exist for all source and target fields
[ ] DQ rules defined for all required fields
[ ] Right-to-erasure path documented (how to delete a person's data end-to-end)
```
