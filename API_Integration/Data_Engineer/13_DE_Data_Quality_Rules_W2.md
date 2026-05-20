# Data Quality Rules — Template & Best Practices

**Priority:** 13 — Define what "valid" data looks like before pipelines process it
**Owner:** Data Engineer
**Phase:** 0 — Week 2–3; enforced from first pipeline in Phase 2

---

## Purpose

Data Quality Rules define what constitutes a valid record at each stage of the pipeline. Rules are implemented as automated checks — failures route to the DLQ, trigger alerts, or are flagged for review depending on severity.

---

## Document Metadata

| Field | Value |
|---|---|
| Document Owner | |
| Last Updated | |
| Version | 1.0 |
| Review Cycle | Per integration onboarding + quarterly |
| Approved By | |

---

## Data Quality Dimensions

| Dimension | Definition | Example Failure |
|---|---|---|
| **Completeness** | Required fields are present and non-null | `employee_id` is null |
| **Accuracy** | Values conform to expected format or range | `email` fails RFC 5322 validation |
| **Consistency** | Related fields agree with each other | `termination_date` is before `hire_date` |
| **Uniqueness** | No duplicate records for the same business key | Two events with the same `event_id` |
| **Timeliness** | Data arrives within the expected window | Event timestamp is 48 hours old |
| **Referential Integrity** | Foreign keys resolve to known values | `department_code` not in reference table |
| **Conformity** | Values match allowed set or enumeration | `employment_type` = "CASUAL" (not in allowed list) |

---

## Severity Levels

| Severity | Meaning | Action on Failure |
|---|---|---|
| **Critical** | Record cannot be processed at all | Route to DLQ, alert on-call, do NOT process |
| **High** | Record is usable but data is materially wrong | Route to DLQ, alert data team, review before reprocessing |
| **Medium** | Record is usable; defect should be corrected at source | Process with warning flag, log issue, notify source system owner |
| **Low** | Minor anomaly; no action required but worth tracking | Process, log metric, review in weekly data quality report |

---

## Rule Definition Template

| Field | Description |
|---|---|
| **Rule ID** | Unique identifier (DQR-001) |
| **Rule Name** | Short descriptive name |
| **Topic / Entity** | Which Kafka topic or table this applies to |
| **Field(s)** | Field or fields involved |
| **Dimension** | Completeness / Accuracy / Consistency / Uniqueness / Timeliness / Referential Integrity / Conformity |
| **Rule Description** | Plain English statement of the rule |
| **Logic / Expression** | Precise technical expression of the check |
| **Severity** | Critical / High / Medium / Low |
| **Action on Failure** | Route to DLQ / Flag / Log / Alert |
| **Alert Recipient** | Who gets notified on failure |
| **Source of Rule** | Business requirement / Compliance / Technical constraint |
| **Implemented In** | Kafka Streams / dbt test / Great Expectations / custom validator |
| **Status** | Draft / Active / Deprecated |

---

## Data Quality Rules Table

### Topic: `hr.employee.hired`

| Rule ID | Rule Name | Field(s) | Dimension | Rule Description | Logic / Expression | Severity | Action | Alert Recipient |
|---|---|---|---|---|---|---|---|---|
| DQR-001 | Employee ID Required | employee_id | Completeness | employee_id must be present and non-empty | `employee_id IS NOT NULL AND employee_id != ''` | Critical | DLQ + Alert | Data Engineer |
| DQR-002 | Employee ID Format | employee_id | Accuracy | employee_id must be a valid UUID v4 | `employee_id MATCHES UUID_V4_REGEX` | Critical | DLQ + Alert | Data Engineer |
| DQR-003 | Duplicate Event Guard | event_id | Uniqueness | No two events with the same event_id should be processed | `event_id NOT IN processed_event_ids` | Critical | Drop + Log | Data Engineer |
| DQR-004 | Email Format | email | Accuracy | email must conform to RFC 5322 format | `email MATCHES EMAIL_REGEX` | High | DLQ | Data Engineer |
| DQR-005 | First Name Required | first_name | Completeness | first_name must be non-null and non-empty | `first_name IS NOT NULL AND TRIM(first_name) != ''` | High | DLQ | Data Engineer |
| DQR-006 | Last Name Required | last_name | Completeness | last_name must be non-null and non-empty | `last_name IS NOT NULL AND TRIM(last_name) != ''` | High | DLQ | Data Engineer |
| DQR-007 | Hire Date Required | hire_date | Completeness | hire_date must be present | `hire_date IS NOT NULL` | High | DLQ | Data Engineer |
| DQR-008 | Hire Date Format | hire_date | Accuracy | hire_date must be a valid ISO 8601 date | `hire_date MATCHES YYYY-MM-DD` | High | DLQ | Data Engineer |
| DQR-009 | Hire Date Not Future | hire_date | Accuracy | hire_date must not be more than 30 days in the future | `hire_date <= today() + 30 days` | Medium | Process + Flag | Data Team |
| DQR-010 | Employment Type Conformity | employment_type | Conformity | employment_type must be one of the allowed values | `employment_type IN ('FULL_TIME','PART_TIME','CONTRACTOR','INTERN')` | High | DLQ | Data Engineer |
| DQR-011 | Department Code Referential Integrity | department_code | Referential Integrity | department_code must exist in the department reference table | `department_code IN (SELECT code FROM department_ref)` | Medium | Process + Flag | Source System Owner |
| DQR-012 | Salary vs Currency Consistency | salary, currency_code | Consistency | If salary is not null, currency_code must also be not null | `IF salary IS NOT NULL THEN currency_code IS NOT NULL` | High | DLQ | Data Engineer |
| DQR-013 | Salary Range Plausibility | salary | Accuracy | Salary must be a positive number if provided | `salary IS NULL OR salary > 0` | High | DLQ | Data Engineer |
| DQR-014 | Currency Code Format | currency_code | Accuracy | currency_code must be a valid ISO 4217 3-letter code | `currency_code MATCHES [A-Z]{3} AND currency_code IN ISO4217_LIST` | Medium | Process + Flag | Data Engineer |
| DQR-015 | Event Timestamp Timeliness | timestamp | Timeliness | Event timestamp must not be older than 24 hours | `timestamp >= now() - 24 hours` | Medium | Process + Flag | Data Engineer |
| DQR-016 | Event Timestamp Not Future | timestamp | Accuracy | Event timestamp must not be in the future | `timestamp <= now() + 5 minutes` | High | DLQ | Data Engineer |

---

## Failure Handling Flow

```
Event arrives at consumer
        │
        ▼
  Run DQ Rules
        │
   ┌────┴────┐
   │         │
PASS        FAIL
   │         │
Process    Determine Severity
           │
      ┌────┴────────────┐
      │                 │
   Critical          Medium / Low
   or High               │
      │            Process + attach
   Route to         warning flag + log
     DLQ                 │
      │            Send to downstream
   Alert                 │
   on-call          Write DQ metric
      │             to Prometheus
   Human review
      │
  Fix + replay
  from DLQ
```

---

## DLQ Message Format

When a record is routed to the DLQ, enrich it with failure metadata:

```json
{
  "original_event": { },
  "dq_failure": {
    "rule_id": "DQR-004",
    "rule_name": "Email Format",
    "field": "email",
    "actual_value": "not-an-email",
    "severity": "High",
    "failed_at": "2026-05-20T10:05:00Z",
    "consumer_service": "it-provisioning-service",
    "topic": "hr.employee.hired",
    "partition": 2,
    "offset": 10045
  }
}
```

---

## Data Quality Metrics (Prometheus)

Expose these metrics per pipeline for Grafana dashboards:

| Metric Name | Type | Labels | Description |
|---|---|---|---|
| `dq_records_total` | Counter | topic, consumer | Total records processed |
| `dq_failures_total` | Counter | topic, consumer, rule_id, severity | Total DQ failures |
| `dq_failure_rate` | Gauge | topic, consumer | % of records failing DQ checks |
| `dq_dlq_size` | Gauge | topic | Current message count in DLQ |
| `dq_processing_latency_seconds` | Histogram | topic, consumer | Time spent in DQ checks |

**Alert thresholds:**
- `dq_failure_rate > 1%` over 5 minutes → Page data engineer
- `dq_dlq_size > 0` for Critical rules → Page on-call immediately

---

## Data Quality Report Template (Weekly)

| Metric | This Week | Last Week | Trend | Action |
|---|---|---|---|---|
| Total records processed | | | | |
| Total DQ failures | | | | |
| Overall failure rate | | | | |
| Critical failures | | | | |
| Top failing rule | | | | |
| DLQ messages resolved | | | | |
| DLQ messages pending | | | | |
| New rules added | | | | |
| Source issues reported to owners | | | | |

---

## Tools for Implementation

| Tool | Use Case |
|---|---|
| **Great Expectations** | Python-native DQ framework; integrates with pipelines |
| **Soda Core** | Declarative DQ checks; YAML-based rules |
| **dbt tests** | DQ checks on data already in PostgreSQL |
| **Apache Kafka Streams** | Inline DQ filtering and routing at stream processing layer |
| **Custom validator class** | Lightweight DQ in FastAPI/Spring Boot consumer before writing to DB |
