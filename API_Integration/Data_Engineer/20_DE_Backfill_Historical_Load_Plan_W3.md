# Backfill & Historical Load Plan — Template & Best Practices

**Priority:** 20 — Prevents data gaps when a new integration goes live against an existing system
**Owner:** Data Engineer
**Phase:** 0 — Assessed Week 3; executed in Phase 2 before go-live

---

## Purpose

When a new integration connects to a system that already has existing data, a backfill is required to load historical records before the real-time pipeline takes over. Without a plan, the target system starts with an incomplete view of the world.

---

## Document Metadata

| Field | Value |
|---|---|
| Document Owner | |
| Last Updated | |
| Version | 1.0 |
| Approved By | |

---

## Backfill Decision Checklist

Answer these before committing to a backfill:

```
[ ] Does the target system need historical data to function correctly?
[ ] How far back does the business need? (all time / 2 years / 1 year)
[ ] Is historical data available in the source system?
[ ] Is the source system able to serve a bulk extract without impacting production?
[ ] What is the volume? (record count + estimated GB)
[ ] Is the historical schema compatible with the current integration schema?
[ ] Is there a maintenance window available for the backfill extract?
[ ] Can the backfill be paused and resumed if something fails mid-run?
[ ] Is the target system able to accept the bulk load without degrading?
[ ] Are idempotency checks in place so a re-run does not create duplicates?
```

---

## Backfill Plan Template

One plan per integration that requires a backfill.

---

### Backfill: BF-001 — HR Employee Historical Load → finance_db.employees

#### Overview

| Field | Value |
|---|---|
| **Backfill ID** | BF-001 |
| **Integration ID** | INT-001 |
| **Source System** | HR System |
| **Target** | finance_db.employees |
| **Historical Range** | All active employees as of go-live date |
| **Estimated Volume** | 5,000 employees |
| **Estimated Data Size** | ~5 MB |
| **Extraction Method** | Bulk REST API extract (paginated) |
| **Load Method** | Direct PostgreSQL COPY / bulk insert via consumer service |
| **Idempotency Key** | employee_id — upsert, never duplicate |
| **Planned Execution Date** | Before go-live, during Phase 2 staging validation |
| **Execution Window** | Off-peak: Saturday 02:00–06:00 UTC |
| **Estimated Duration** | ~30 minutes |
| **Owner** | Data Engineer |
| **Approver** | Integration Architect |

---

#### Backfill Strategy

**Chosen approach:** Paginated REST API extract → transform → bulk upsert to PostgreSQL

**Why not Kafka:** Historical data should bypass Kafka for backfill. Publishing 5,000 events to Kafka just for a one-time load creates unnecessary noise, inflates consumer lag metrics, and risks triggering downstream side effects (e.g. payroll system should not re-onboard every employee).

**Kafka cutover:** After the backfill completes and is validated, the real-time Kafka consumer takes over for all new events from that point forward.

---

#### Execution Steps

```
Pre-backfill:
[ ] Confirm backfill volume with source system owner
[ ] Verify target table is empty or idempotency logic is in place
[ ] Disable any triggers or side effects in the target system during load
[ ] Take a snapshot/backup of the target table before starting
[ ] Agree extraction window with source system owner (avoid peak hours)
[ ] Confirm read-only access credentials to source system are available

Extraction:
[ ] Extract all records from source in batches of 500
[ ] Apply the same transformation logic as the real-time pipeline (TRF-001)
[ ] Apply the same data quality rules (DQR-001 to DQR-016)
[ ] Log records that fail DQ checks to a backfill_errors table, do not abort
[ ] Write successfully transformed records to a staging table first

Validation (on staging table):
[ ] Record count matches source system export count
[ ] Spot-check 10 random records against source system manually
[ ] All required fields populated (no unexpected nulls)
[ ] No duplicate employee_id values in staging table
[ ] DQ error log reviewed — failures understood and accepted or corrected

Load (staging → target):
[ ] INSERT INTO employees SELECT * FROM employees_backfill_staging
    ON CONFLICT (employee_id) DO NOTHING
[ ] Confirm row count in target matches staging
[ ] Re-enable any disabled triggers

Post-backfill:
[ ] Run reconciliation query: count in source vs. count in target
[ ] Start real-time Kafka consumer (offset = latest)
[ ] Monitor consumer lag for first 30 minutes
[ ] Archive backfill staging table (rename, do not drop)
[ ] Document actual vs. estimated duration and volume
[ ] Sign off with Integration Architect and Source System Owner
```

---

#### Reconciliation Query

Run after backfill to verify completeness:

```sql
-- Count comparison
SELECT
    (SELECT COUNT(*) FROM employees_backfill_staging) AS backfill_count,
    (SELECT COUNT(*) FROM employees)                   AS target_count,
    (SELECT COUNT(*) FROM employees_backfill_staging) -
    (SELECT COUNT(*) FROM employees)                   AS discrepancy;

-- Check for records in backfill but not in target (missed inserts)
SELECT s.employee_id
FROM employees_backfill_staging s
LEFT JOIN employees t ON s.employee_id = t.employee_id
WHERE t.employee_id IS NULL;

-- Check for nulls in required fields
SELECT COUNT(*) FROM employees
WHERE employee_id IS NULL
   OR first_name IS NULL
   OR last_name IS NULL
   OR email IS NULL;
```

---

#### Rollback Plan

If the backfill produces incorrect data:

```sql
-- Option 1: Truncate and re-run (if target was empty before backfill)
TRUNCATE TABLE employees;

-- Option 2: Restore from pre-backfill snapshot
-- Restore from PostgreSQL backup taken before backfill started

-- Option 3: Delete only backfill records (if mixed with existing data)
DELETE FROM employees
WHERE source_system = 'hr-service-backfill'
  AND created_at BETWEEN '[backfill_start]' AND '[backfill_end]';
```

---

## Backfill Registry

| Backfill ID | Integration | Source | Target | Volume | Status | Executed Date | Executed By |
|---|---|---|---|---|---|---|---|
| BF-001 | INT-001 | HR System | finance_db.employees | 5,000 rows | Planned | | |
| BF-002 | INT-004 | Finance System | erp_db.invoices | 50,000 rows | Not Started | | |
| | | | | | | | |
