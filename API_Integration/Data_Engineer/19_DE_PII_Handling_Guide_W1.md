# PII & Data Masking Handling Guide — Template & Best Practices

**Priority:** 19 — Compliance and legal requirement; must be agreed before any pipeline touches PII
**Owner:** Data Engineer + Security Engineer + Compliance
**Phase:** 0 — Week 1; reviewed by legal/compliance before Phase 2 begins

---

## Purpose

Documents every PII field in the platform, its classification, masking rules per environment, and the procedures for handling data subject rights requests (right to access, right to erasure). Non-compliance with GDPR / HIPAA / local regulations is a legal risk.

---

## Document Metadata

| Field | Value |
|---|---|
| Document Owner | Data Engineer |
| Compliance Reviewer | |
| Legal Reviewer | |
| Last Updated | |
| Version | 1.0 |
| Applicable Regulations | GDPR / HIPAA / PDPA / Other |
| Review Cycle | Annually + whenever new PII fields are added |

---

## PII Classification Levels

| Level | Definition | Examples | Treatment |
|---|---|---|---|
| **None** | Not personal data | department_code, invoice_number | No special handling |
| **PII** | Directly or indirectly identifies a person | name, email, phone, home address | Mask in non-prod; encrypt at rest |
| **Sensitive PII** | Legally protected categories | salary, medical condition, religion, ethnicity | Redact in non-prod; encrypt at rest; strict access controls |
| **Restricted** | High-risk identifiers | national_id, passport, biometric, payment card | Tokenise; encrypt; access audit log required |

---

## Masking Techniques

| Technique | Description | When to Use | Reversible? |
|---|---|---|---|
| **Hashing** | One-way SHA-256 (or similar) of value | Names, IDs for non-prod testing | No |
| **Tokenisation** | Replace value with a random token; real value in secure vault | Email, national_id | Yes (via vault lookup) |
| **Redaction** | Replace with fixed string: `[REDACTED]` | Financial values, health data in logs | No |
| **Truncation** | Keep only partial value (e.g. last 4 digits) | Phone numbers, credit cards | No |
| **Pseudonymisation** | Replace with consistent fake value (same input = same fake output) | Test data generation | No (without mapping) |
| **Encryption** | AES-256 or similar; requires key management | Restricted fields at rest | Yes (with key) |
| **Nulling** | Replace with NULL | Fields not needed in non-prod | No |

---

## PII Field Inventory

| Field ID | Field Name | Entity | PII Level | Masking (Dev) | Masking (Staging) | Masking (Prod) | Encryption at Rest | Access Restricted To | Regulation |
|---|---|---|---|---|---|---|---|---|---|
| FLD-002 | first_name | Employee | PII | Hash | Hash | Plaintext | No | HR, Finance, IT | GDPR |
| FLD-003 | last_name | Employee | PII | Hash | Hash | Plaintext | No | HR, Finance, IT | GDPR |
| FLD-004 | email | Employee | PII | Tokenise | Tokenise | Plaintext | No | HR, IT | GDPR |
| FLD-007 | salary | Employee | Sensitive PII | Redact | Redact | Plaintext | Yes | Finance, Payroll | GDPR |
| FLD-011 | national_id | Employee | Restricted | Tokenise | Tokenise | Tokenise | Yes | HR only | GDPR, local law |
| FLD-015 | home_address | Employee | PII | Nulling | Nulling | Plaintext | No | HR only | GDPR |
| | | | | | | | | | |

---

## Environment PII Rules

| Environment | Rule |
|---|---|
| **Production** | Real data. TLS everywhere. Encryption at rest for Sensitive/Restricted fields. Access audit log for Restricted fields. |
| **Staging** | Masked data only. No real PII. Use tokenised/hashed values generated from prod schema. |
| **Dev / Local** | Fully synthetic data. No real PII permitted. Developers must not copy prod data to local machines. |

---

## Data Subject Rights Procedures

### Right to Access (GDPR Article 15)
When a data subject requests a copy of their data:

```
1. Identify all systems holding data for the subject (use Data Lineage Map)
2. Query PostgreSQL: SELECT * FROM employees WHERE employee_id = '[id]'
3. Query Kafka: check if events with employee_id are within retention window
4. Compile report in standard format
5. Deliver within 30 days
6. Log the request and response in the access log
```

### Right to Erasure / Right to Be Forgotten (GDPR Article 17)
When a data subject requests deletion:

```
1. Verify the request is legitimate and authorised
2. Identify all locations holding data (Data Lineage Map + PII Field Inventory)
3. PostgreSQL: SET _is_deleted = TRUE, NULL all PII fields WHERE employee_id = '[id]'
   (soft delete — do NOT hard delete; audit trail must remain)
4. Kafka: Kafka topics with time-based retention will expire naturally.
   If compacted topics: publish a tombstone event (null value, same key)
5. DLQ topics: manually remove any events containing the subject's data
6. Schema Registry: schemas do not contain personal data — no action needed
7. Logs: redact PII from log entries older than retention policy
8. Document the erasure action with timestamp and operator
9. Notify the data subject of completion within 30 days
```

### Tombstone Event for Kafka Compacted Topics

```json
{
  "event_id": "uuid-v4",
  "event_type": "EmployeeDataErased",
  "event_version": "1.0",
  "source_system": "data-governance-service",
  "timestamp": "2026-05-20T10:00:00Z",
  "payload": {
    "employee_id": "a1b2c3d4-...",
    "erasure_reason": "GDPR_RIGHT_TO_ERASURE",
    "erased_at": "2026-05-20T10:00:00Z"
  }
}
```

---

## PII Access Controls

| Data Level | Who Can Access (Prod) | Access Type | Audit Log Required |
|---|---|---|---|
| PII | Application service accounts only | Service-to-DB | No |
| Sensitive PII | Finance, Payroll service accounts | Service-to-DB | Yes |
| Restricted | HR service account only | Service-to-DB | Yes — every query logged |
| All PII | No developer direct DB access to prod | — | — |

**Rule:** Developers must never have direct SELECT access to production tables containing PII. All access must be via the application layer.

---

## PII Compliance Checklist

Complete before any integration that handles PII goes to production:

```
[ ] All PII fields identified and added to PII Field Inventory
[ ] Applicable regulations confirmed with legal (GDPR, HIPAA, PDPA, etc.)
[ ] Masking rules implemented and verified in dev and staging
[ ] Encryption at rest configured for Sensitive and Restricted fields
[ ] TLS enforced on all Kafka and PostgreSQL connections
[ ] Access controls reviewed — no developer has direct prod PII access
[ ] Audit logging enabled for Restricted field access
[ ] Right to erasure procedure documented and tested in staging
[ ] Data retention periods set on Kafka topics and PostgreSQL tables
[ ] Legal/compliance sign-off obtained before production deployment
[ ] Non-prod environments confirmed to contain no real PII
```
