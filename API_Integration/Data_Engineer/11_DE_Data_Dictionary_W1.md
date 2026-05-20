# Data Dictionary — Template & Best Practices

**Priority:** 11 — Must exist before any schema or pipeline is built
**Owner:** Data Engineer
**Phase:** 0 — Week 1; updated continuously throughout project

---

## Purpose

The Data Dictionary is the single source of truth for every field in the integration platform. It eliminates ambiguity between source systems, integration developers, and consumers.

**Rule:** No field enters a Kafka schema or PostgreSQL table without a row in the Data Dictionary first.

---

## Document Metadata

| Field | Value |
|---|---|
| Document Owner | |
| Last Updated | |
| Version | 1.0 |
| Review Cycle | Every sprint |
| Approved By | |

---

## Data Dictionary Template

### Column Definitions

| Column | Description |
|---|---|
| **Field ID** | Unique identifier for the field (e.g. FLD-001) |
| **Field Name** | Canonical name used in the integration layer (snake_case) |
| **Display Name** | Human-readable name for documentation |
| **Source System** | System where this field originates |
| **Source Field Name** | Exact field name in the source system (may differ from canonical) |
| **Data Type** | Canonical type: String, Integer, Decimal, Boolean, Date, DateTime, UUID |
| **Format** | Pattern or format constraint (e.g. ISO 8601, E.164 phone, UUID v4) |
| **Max Length** | Maximum character/byte length (Strings) |
| **Nullable** | Yes / No — can this field be null in the integration layer |
| **Default Value** | Value to use if source is null (if applicable) |
| **PII Classification** | None / PII / Sensitive / Restricted |
| **PII Type** | Name / Email / Phone / NationalID / Financial / Health / Location |
| **Masking Rule** | None / Hash / Redact / Tokenise / Truncate |
| **Description** | Business definition — what this field means, not just its name |
| **Accepted Values** | Enum values or value range if constrained |
| **Validation Rule** | Specific validation logic (e.g. must be > 0, must match regex) |
| **Business Key** | Yes / No — is this field part of the business identifier |
| **Source of Truth** | Which system is authoritative if the field exists in multiple systems |
| **Related Fields** | Other fields this field depends on or is derived from |
| **Notes** | Known quirks, edge cases, source data quality issues |

---

## Data Dictionary Table

| Field ID | Field Name | Display Name | Source System | Source Field Name | Data Type | Format | Max Length | Nullable | Default Value | PII Class | PII Type | Masking Rule | Description | Accepted Values | Validation Rule | Business Key | Source of Truth | Related Fields | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FLD-001 | employee_id | Employee ID | HR System | EmpID | UUID | UUID v4 | 36 | No | — | None | — | None | Unique identifier for an employee in the integration layer | — | Must be valid UUID v4 | Yes | HR System | — | Source uses integer; convert to UUID at ingestion |
| FLD-002 | first_name | First Name | HR System | FirstName | String | — | 100 | No | — | PII | Name | Hash | Legal first name of the employee | — | Non-empty | No | HR System | last_name | |
| FLD-003 | last_name | Last Name | HR System | LastName | String | — | 100 | No | — | PII | Name | Hash | Legal last name of the employee | — | Non-empty | No | HR System | first_name | |
| FLD-004 | email | Work Email | HR System | WorkEmail | String | RFC 5322 | 254 | No | — | PII | Email | Tokenise | Primary work email address | — | Valid email format | Yes | HR System | — | Personal email is in a separate field; do not use |
| FLD-005 | hire_date | Hire Date | HR System | HireDate | Date | ISO 8601 (YYYY-MM-DD) | — | No | — | None | — | None | Date employment officially started | — | Must not be in the future | No | HR System | termination_date | |
| FLD-006 | department_code | Department Code | HR System | DeptCode | String | — | 10 | No | — | None | — | None | Code identifying the employee's department | See Department Reference Table | Must exist in department reference | No | HR System | department_name | |
| FLD-007 | salary | Annual Salary | Finance System | BaseSalary | Decimal | — | — | Yes | null | Sensitive | Financial | Redact | Annual base salary in local currency | — | Must be > 0 if not null | No | Finance System | currency_code | Null for contractors |
| FLD-008 | currency_code | Currency Code | Finance System | CurrencyCode | String | ISO 4217 | 3 | Yes | null | None | — | None | ISO currency code for the salary field | USD, EUR, GBP, SGD, AUD | Must be valid ISO 4217 | No | Finance System | salary | |
| FLD-009 | employment_type | Employment Type | HR System | EmpType | String | — | 20 | No | — | None | — | None | Classification of employment arrangement | FULL_TIME, PART_TIME, CONTRACTOR, INTERN | Must be one of accepted values | No | HR System | — | |
| FLD-010 | is_active | Is Active | HR System | Status | Boolean | — | — | No | — | None | — | None | Whether the employee is currently active | true, false | — | No | HR System | termination_date | Derived from Status = 'Active' in source |

---

## PII Classification Guide

| Classification | Definition | Examples | Minimum Masking |
|---|---|---|---|
| **None** | Not personal data | department_code, product_id | None |
| **PII** | Directly identifies an individual | name, email, phone, address | Hash or Tokenise |
| **Sensitive** | Financial, health, or legally protected | salary, medical_condition | Redact |
| **Restricted** | National ID, passport, biometric | national_id, fingerprint | Tokenise + Encrypt |

---

## Data Type Reference

| Canonical Type | Description | Example |
|---|---|---|
| String | Variable-length text | "John Smith" |
| Integer | Whole number | 42 |
| Decimal | Floating-point (use for money) | 95000.00 |
| Boolean | true / false | true |
| Date | Calendar date, no time | 2026-01-15 |
| DateTime | Date + time, always UTC, ISO 8601 | 2026-01-15T08:30:00Z |
| UUID | UUID v4 string | 550e8400-e29b-41d4-a716-446655440000 |
| JSON | Nested structure | {"key": "value"} |
| Array | List of values | ["a", "b", "c"] |

---

## Known Source Data Quality Issues Log

Document known issues in source systems so consumers are not surprised:

| Issue ID | Source System | Field Affected | Issue Description | Frequency | Workaround | Status |
|---|---|---|---|---|---|---|
| DQ-001 | HR System | hire_date | ~2% of records have hire_date in the future due to advance entry | Occasional | Flag and hold until date arrives | Open |
| DQ-002 | Finance System | salary | Null for all contractors — expected, not a defect | Always | Treat null as valid for contractors | Documented |
| DQ-003 | HR System | department_code | Legacy codes (pre-2020) not in current reference table | Rare | Map legacy codes using translation table | Open |

---

## Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | | | Initial draft |
| | | | |
