# Integration Inventory

**Priority:** 1 — Most critical first step before any code is written
**Phase:** 0 — Discovery & Design (Week 1–3)

---

## Purpose

Identify every system involved, what data it owns, what events it produces, and what it needs from other systems. This prevents building in isolation and discovering incompatibilities late.

---

## Methodology: System Landscape Mapping

Borrowed from **SAP Integration Assessment** and **TOGAF** (The Open Group Architecture Framework).

### How to Conduct It

1. Run a **stakeholder workshop** — invite owners of each system (ERP, CRM, HR, Finance, etc.)
2. For each system, answer:
   - What data does it own?
   - What events does it produce? (e.g. `EmployeeHired`, `InvoiceApproved`)
   - What data does it need from other systems?
   - What are its technical capabilities? (REST, SFTP, DB, webhook?)
3. Draw a **Context Diagram** — boxes for systems, arrows for data flows
4. Prioritize integrations by business value and technical risk

---

## Integration Inventory Checklist

For each integration, capture:

```
[ ] Source system name and owner
[ ] Target system name and owner
[ ] Trigger (event-driven, scheduled, on-demand)
[ ] Frequency (real-time, hourly, daily, batch)
[ ] Data direction (one-way, bidirectional)
[ ] Data volume (records per day/hour)
[ ] Latency requirement (milliseconds, seconds, minutes)
[ ] Criticality (business-critical, nice-to-have)
[ ] Auth method supported by source/target
[ ] Existing API/connector available?
[ ] Data sensitivity (PII, financial, public)
[ ] Error handling expectation (retry, alert, fail-silent)
```

---

## Integration Inventory Template

| Field | Value |
|---|---|
| Integration ID | INT-001 |
| Source System | |
| Source Owner | |
| Target System | |
| Target Owner | |
| Trigger Type | Event / Scheduled / On-Demand |
| Frequency | Real-time / Hourly / Daily / Batch |
| Direction | One-way / Bidirectional |
| Volume (records/day) | |
| Latency Requirement | |
| Criticality | Business-critical / Nice-to-have |
| Auth Method | REST / SFTP / DB / Webhook |
| Existing Connector | Yes / No |
| Data Sensitivity | PII / Financial / Internal / Public |
| Error Handling | Retry / Alert / Fail-silent |
| Status | Not Started / In Progress / Done |

---

## Diagramming Standards

- **C4 Model** (c4model.com) — Context → Container → Component → Code
- **ArchiMate** — Enterprise architecture notation for system relationships
- **TOGAF ADM** — Phase B covers business architecture including integration landscape

---

## Output of This Step

- Completed integration inventory spreadsheet/table
- Context diagram showing all systems and data flows
- Prioritized integration backlog (highest business value + lowest risk first)

---

## References

- TOGAF ADM — opengroup.org
- C4 Model — c4model.com
- ArchiMate — opengroup.org/archimate
