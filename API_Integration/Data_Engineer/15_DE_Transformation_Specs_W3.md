# Transformation Specs — Template & Best Practices

**Priority:** 15 — Documents every mapping decision so logic is reviewable and maintainable
**Owner:** Data Engineer
**Phase:** 0 — Week 3; one spec per integration before build begins

---

## Purpose

The Transformation Spec is the technical blueprint for how data moves from source to target. It documents every field mapping, business rule, type conversion, enrichment, and error handling decision — so developers can implement it correctly and reviewers can audit it.

**Rule:** A developer should be able to implement a pipeline from the Transformation Spec alone, without asking the data engineer to explain anything verbally.

---

## Document Metadata

| Field | Value |
|---|---|
| Document Owner | |
| Last Updated | |
| Version | 1.0 |
| Review Cycle | Updated per schema or business rule change |
| Approved By | |
| Related Schema | `12_DE_Event_Schema_Catalogue_W2.md` |
| Related DQ Rules | `13_DE_Data_Quality_Rules_W2.md` |
| Related Lineage | `14_DE_Data_Lineage_Map_W2.md` |

---

## Transformation Spec Entry Template

One spec per integration (source → target pair). Copy this block for each.

---

### Spec: TRF-001 — HR Employee Hired → finance_db.employees

#### Summary

| Field | Value |
|---|---|
| **Spec ID** | TRF-001 |
| **Integration ID** | INT-001 |
| **Source** | Kafka topic: `hr.employee.hired` |
| **Target** | PostgreSQL: `finance_db.employees` |
| **Consumer Service** | finance-service |
| **Trigger** | New message consumed from `hr.employee.hired` |
| **Operation Type** | Upsert (insert new; update if employee_id already exists) |
| **Idempotency Key** | `source_event_id` — skip if already processed |
| **Transaction Boundary** | One Kafka message = one DB transaction |

---

#### Field Mapping Table

| # | Source Field | Source Type | Transformation Type | Transformation Logic | Target Field | Target Type | Nullable | On Null / Error |
|---|---|---|---|---|---|---|---|---|
| 1 | `payload.employee_id` | String (UUID) | Direct map | None | `employee_id` | UUID | NOT NULL | Route to DLQ (DQR-001) |
| 2 | `payload.first_name` | String | Trim | `TRIM(first_name)` | `first_name` | VARCHAR(100) | NOT NULL | Route to DLQ (DQR-005) |
| 3 | `payload.last_name` | String | Trim | `TRIM(last_name)` | `last_name` | VARCHAR(100) | NOT NULL | Route to DLQ (DQR-006) |
| 4 | `payload.email` | String | Normalise | `LOWER(TRIM(email))` | `email` | VARCHAR(254) | NOT NULL | Route to DLQ (DQR-004) |
| 5 | `payload.hire_date` | String | Parse date | `DATE(hire_date)` — ISO 8601 parse | `hire_date` | DATE | NOT NULL | Route to DLQ (DQR-007) |
| 6 | `payload.department_code` | String | Direct map | None | `department_code` | VARCHAR(10) | NOT NULL | Route to DLQ if null; flag if not in ref table (DQR-011) |
| 7 | `payload.employment_type` | String | Validate enum | Must be in `['FULL_TIME','PART_TIME','CONTRACTOR','INTERN']` | `employment_type` | VARCHAR(20) | NOT NULL | Route to DLQ (DQR-010) |
| 8 | `payload.salary` | Double / null | Direct map | None | `salary` | DECIMAL(15,2) | NULLABLE | Null allowed for contractors |
| 9 | `payload.currency_code` | String / null | Uppercase + validate | `UPPER(TRIM(currency_code))` — validate ISO 4217 | `currency_code` | CHAR(3) | NULLABLE | Null only if salary is also null (DQR-012) |
| 10 | `event_id` (envelope) | String (UUID) | Direct map | None | `source_event_id` | UUID | NOT NULL | Route to DLQ if missing |
| 11 | `source_system` (envelope) | String | Direct map | None | `source_system` | VARCHAR(50) | NOT NULL | Default: `'hr-service'` |
| 12 | Derived | — | System timestamp | `NOW()` at time of DB write | `created_at` | TIMESTAMPTZ | NOT NULL | — |
| 13 | Derived | — | System timestamp | `NOW()` at time of DB write | `updated_at` | TIMESTAMPTZ | NOT NULL | — |
| 14 | Derived | — | Default value | `FALSE` | `_is_deleted` | BOOLEAN | NOT NULL | — |

---

#### Transformation Logic — Detail

**TRF-001-A: Employee ID**
- Source: `payload.employee_id` — already a UUID v4 string from hr-service (conversion from integer done upstream in producer)
- Action: Validate UUID v4 format. If invalid, route to DLQ.
- No transformation needed at consumer.

**TRF-001-B: Email Normalisation**
```python
email = event.payload.email.strip().lower()
# Validate format
if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
    raise DQValidationError(rule_id='DQR-004', field='email', value=email)
```

**TRF-001-C: Hire Date Parsing**
```python
from datetime import date
hire_date = date.fromisoformat(event.payload.hire_date)
# Raises ValueError if format is invalid → route to DLQ
```

**TRF-001-D: Salary + Currency Consistency**
```python
salary = event.payload.salary        # May be None
currency = event.payload.currency_code  # May be None

if salary is not None and currency is None:
    raise DQValidationError(rule_id='DQR-012', field='currency_code')

if currency is not None:
    currency = currency.strip().upper()
    if currency not in ISO_4217_CODES:
        raise DQValidationError(rule_id='DQR-014', field='currency_code', value=currency)
```

**TRF-001-E: Idempotency Check**
```python
existing = db.query(
    "SELECT 1 FROM employees WHERE source_event_id = %s",
    [event.event_id]
)
if existing:
    logger.info(f"Duplicate event {event.event_id} — skipping")
    return  # Acknowledge Kafka message, do not write to DB
```

**TRF-001-F: Upsert Logic**
```sql
INSERT INTO employees (
    employee_id, first_name, last_name, email,
    hire_date, department_code, employment_type,
    salary, currency_code, source_event_id,
    source_system, created_at, updated_at, _is_deleted
)
VALUES (...)
ON CONFLICT (employee_id)
DO UPDATE SET
    first_name       = EXCLUDED.first_name,
    last_name        = EXCLUDED.last_name,
    email            = EXCLUDED.email,
    hire_date        = EXCLUDED.hire_date,
    department_code  = EXCLUDED.department_code,
    employment_type  = EXCLUDED.employment_type,
    salary           = EXCLUDED.salary,
    currency_code    = EXCLUDED.currency_code,
    updated_at       = NOW();
```

---

#### Enrichment Sources

| Enrichment | Source | When Applied | Failure Handling |
|---|---|---|---|
| Department name lookup | `finance_db.department_ref` | After insert, async | If not found, log warning — do not fail pipeline |
| ISO 4217 validation | Static code list (bundled in service) | At validation step | Route to DLQ on mismatch |

---

#### Error Handling Summary

| Failure Type | Action | Topic / Location |
|---|---|---|
| DQ validation failure (Critical/High) | Route original event + error metadata to DLQ | `hr.employee.hired.dlq` |
| DB connection failure | Retry with exponential backoff (3 attempts, 1s/2s/4s) | Retry in-process |
| DB deadlock | Retry once after 100ms | Retry in-process |
| Duplicate event (idempotency) | Acknowledge and skip — do not write | Log only |
| Unknown exception | Route to DLQ + alert on-call | `hr.employee.hired.dlq` + PagerDuty |

---

#### Processing Order & Ordering Guarantees

- Events are partitioned by `employee_id` — all events for the same employee arrive in order within a partition
- Consumer reads one partition sequentially — ordering per employee is guaranteed
- Do NOT process events for the same `employee_id` in parallel

---

#### Target Table DDL

```sql
CREATE TABLE employees (
    employee_id       UUID          PRIMARY KEY,
    first_name        VARCHAR(100)  NOT NULL,
    last_name         VARCHAR(100)  NOT NULL,
    email             VARCHAR(254)  NOT NULL UNIQUE,
    hire_date         DATE          NOT NULL,
    department_code   VARCHAR(10)   NOT NULL,
    employment_type   VARCHAR(20)   NOT NULL,
    salary            DECIMAL(15,2),
    currency_code     CHAR(3),
    source_event_id   UUID          NOT NULL UNIQUE,
    source_system     VARCHAR(50)   NOT NULL DEFAULT 'hr-service',
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    _is_deleted       BOOLEAN       NOT NULL DEFAULT FALSE
);

CREATE INDEX idx_employees_email          ON employees (email);
CREATE INDEX idx_employees_department     ON employees (department_code);
CREATE INDEX idx_employees_hire_date      ON employees (hire_date);
CREATE INDEX idx_employees_source_event   ON employees (source_event_id);
```

---

#### Transformation Spec Checklist

Run before handing spec to developers for implementation:

```
[ ] Every source field has a target field (or explicit "not mapped" with reason)
[ ] Every target NOT NULL field has an "on null" action defined
[ ] All type conversions have explicit logic (no ambiguous "convert as needed")
[ ] Idempotency key identified and logic documented
[ ] Upsert vs insert-only vs insert-or-ignore decision made and documented
[ ] Ordering guarantees documented (or explicitly "unordered")
[ ] All enrichment sources listed with failure handling
[ ] Error routing documented for each failure type
[ ] Target DDL reviewed and matches field mapping table
[ ] DQ rule IDs cross-referenced for each field
[ ] Spec reviewed by the developer who will implement it
[ ] Spec signed off by Integration Architect
```

---

## Transformation Spec Index

| Spec ID | Integration ID | Source | Target | Consumer Service | Status |
|---|---|---|---|---|---|
| TRF-001 | INT-001 | hr.employee.hired | finance_db.employees | finance-service | Draft |
| TRF-002 | INT-002 | hr.employee.hired | Active Directory | it-provisioning-service | Not Started |
| TRF-003 | INT-003 | hr.employee.terminated | finance_db.employees | finance-service | Not Started |
| | | | | | |
