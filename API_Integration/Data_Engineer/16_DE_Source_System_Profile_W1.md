# Source System Profile — Template & Best Practices

**Priority:** 16 — Know your source before building anything against it
**Owner:** Data Engineer
**Phase:** 0 — Week 1; one profile per source system

---

## Purpose

The Source System Profile captures everything a data engineer needs to know about a source system before building a pipeline against it — its technical capabilities, data quality characteristics, known issues, and contact information. Prevents surprises mid-build.

---

## Source System Profile Template

One entry per source system. Copy this block for each.

---

### System: HR System

#### System Overview

| Field | Value |
|---|---|
| **System Name** | HR System |
| **System ID** | SYS-001 |
| **Vendor / Product** | e.g. Workday / SAP SuccessFactors / Custom |
| **Version** | |
| **Environment URLs** | Dev: / Staging: / Prod: |
| **System Owner** | Name + team |
| **Technical Contact** | Name + email + Slack |
| **Business Contact** | Name + email |
| **Criticality** | Business-critical / Important / Nice-to-have |
| **Uptime SLA** | e.g. 99.5% |
| **Maintenance Window** | e.g. Sundays 02:00–04:00 UTC |

---

#### Connectivity

| Field | Value |
|---|---|
| **Integration Method** | REST API / GraphQL / SOAP / SFTP / Direct DB / Webhook |
| **API Base URL** | |
| **API Version** | e.g. v2 |
| **API Documentation URL** | |
| **Authentication Method** | OAuth 2.0 / API Key / Basic Auth / mTLS |
| **Auth Token Endpoint** | |
| **Token Expiry** | e.g. 3600 seconds |
| **Credential Location** | HashiCorp Vault path / AWS Secrets Manager ARN |
| **IP Allowlisting Required** | Yes / No |
| **VPN Required** | Yes / No |
| **Rate Limit** | e.g. 1000 requests/minute |
| **Rate Limit Headers** | e.g. `X-RateLimit-Remaining` |

---

#### Data Extraction

| Field | Value |
|---|---|
| **Extraction Pattern** | Event-driven (webhook/poll) / Scheduled batch / CDC / Manual export |
| **Change Detection Method** | `updated_at` timestamp / Changelog table / Webhook / Full extract + diff |
| **Supports Incremental Load** | Yes / No |
| **Supports Full Reload** | Yes / No |
| **Pagination Style** | Offset/limit / Cursor / Page number / None |
| **Max Page Size** | e.g. 500 records |
| **Date Filter Field** | e.g. `updatedSince` query param |
| **Soft Delete Support** | Yes (`is_deleted` flag) / No (hard deletes only) |
| **Historical Data Available** | Yes — from [date] / No |
| **Backfill Required** | Yes / No |
| **Estimated Backfill Volume** | e.g. 50,000 employee records |

---

#### Data Volume & Throughput

| Metric | Value |
|---|---|
| **Total Records (current)** | |
| **New Records per Day (avg)** | |
| **New Records per Day (peak)** | |
| **Update Rate per Day (avg)** | |
| **Delete Rate per Day (avg)** | |
| **Peak Load Times** | e.g. Monday morning 08:00–09:00 |
| **Batch Job Schedules** | e.g. nightly payroll run at 23:00 |

---

#### Data Quality Assessment

Rate each dimension 1 (poor) to 5 (excellent) based on your assessment:

| Dimension | Rating (1–5) | Notes |
|---|---|---|
| Completeness | | % of required fields populated |
| Accuracy | | Known bad data, stale records |
| Consistency | | Cross-field consistency issues |
| Uniqueness | | Duplicate record frequency |
| Timeliness | | How current the data is |
| Referential Integrity | | FK violations, orphaned records |

**Known Data Quality Issues:**

| Issue ID | Field | Description | Frequency | Workaround |
|---|---|---|---|---|
| SQ-001 | | | | |

---

#### Available Entities / Endpoints

| Entity | Endpoint / Table | Approx. Row Count | Notes |
|---|---|---|---|
| Employee | `GET /v2/employees` | 5,000 | Requires `dept` scope |
| Department | `GET /v2/departments` | 120 | Reference data — changes rarely |
| Job Title | `GET /v2/job-titles` | 80 | Reference data |
| Leave Record | `GET /v2/leave` | 45,000 | Requires `leave` scope |

---

#### Schema / Field Inventory

List all fields from the source that are candidates for integration:

| Source Field | Source Type | Nullable | Description | Maps To (canonical) |
|---|---|---|---|---|
| EmpID | INT | No | Internal employee identifier | employee_id |
| FirstName | VARCHAR(100) | No | Legal first name | first_name |
| LastName | VARCHAR(100) | No | Legal last name | last_name |
| WorkEmail | VARCHAR(254) | No | Work email | email |
| HireDate | VARCHAR (YYYY-MM-DD) | No | Date employment started | hire_date |
| DeptCode | VARCHAR(10) | No | Department reference | department_code |
| Status | VARCHAR(20) | No | Active / Inactive / OnLeave | is_active (derived) |

---

#### Contacts & Escalation

| Role | Name | Contact | Availability |
|---|---|---|---|
| System Owner | | | Business hours |
| Technical Lead | | | Business hours |
| On-Call Support | | | 24/7 (for prod outages) |
| Schema Change Approver | | | Business hours |

---

#### Source System Assessment Checklist

Complete before building any pipeline against this system:

```
[ ] API documentation reviewed and accessible
[ ] Auth credentials obtained and stored in secrets manager
[ ] Rate limits confirmed and respected in pipeline design
[ ] Change detection method confirmed (updated_at field exists and is reliable)
[ ] Soft delete behaviour confirmed
[ ] Backfill volume estimated
[ ] Known data quality issues documented
[ ] Peak load times identified (avoid extraction during peak)
[ ] Contact list complete
[ ] Test connection to dev environment successful
[ ] Sample data extracted and reviewed
[ ] PII fields identified and confirmed with compliance
[ ] Schema dump / field list obtained from system owner
```
