# Documentation Requirements

**Priority:** 7 — Know what to document before you start building
**Phase:** 0 — Structure established Week 1; populated throughout project

---

## Overview

Documentation is written alongside code, not after. Each integration is not "Done" until its documentation is complete (see Way of Working DoD in `6_Way_of_Working_W1.md`).

---

## Architecture & Design Documents

| Document | Owner | When Created | Where Stored |
|---|---|---|---|
| **Architecture Overview Diagram** | Integration Architect | Phase 0 | `/docs/architecture/` |
| **Integration Inventory** | BA + Architect | Phase 0, Week 1 | `/docs/integrations/inventory.md` |
| **Data Flow Diagrams** | Integration Developer | Per integration | `/docs/integrations/[integration-id]/` |
| **ADRs** | Integration Architect | As decisions are made | `/docs/adr/` |
| **Event Schema Catalogue** | Integration Developer | Phase 0, updated ongoing | `/docs/schemas/` |
| **C4 Context + Container Diagrams** | Integration Architect | Phase 0 | `/docs/architecture/` |

---

## API & Contract Documents

| Document | Owner | When Created | Where Stored |
|---|---|---|---|
| **OpenAPI Specs** (per service) | Backend Developer | Before implementation | `/services/[name]/openapi.yaml` |
| **AsyncAPI Specs** (per Kafka topic) | Integration Developer | Before first publish | `/docs/schemas/asyncapi/` |
| **Data Dictionary** | BA + Developer | Phase 0–2 | `/docs/data-dictionary.md` |
| **Consumer / Producer Registry** | Integration Architect | Updated ongoing | `/docs/schemas/registry.md` |

---

## Data Dictionary Template

For each field flowing through the system:

| Field | Source System | Type | Nullable | Description | PII? |
|---|---|---|---|---|---|
| employee_id | HR System | UUID | No | Unique identifier for employee | No |
| email | HR System | String | No | Work email address | Yes |
| hire_date | HR System | Date (ISO 8601) | No | Date employment started | No |
| salary | Finance | Decimal | Yes | Annual base salary | Yes |

---

## Operational Documents

| Document | Owner | When Created | Where Stored |
|---|---|---|---|
| **Runbooks** | DevOps + Developer | Per integration, Phase 2 | `/docs/runbooks/` |
| **Incident Response Playbook** | DevOps + Lead | Phase 3 | `/docs/runbooks/incident-response.md` |
| **Monitoring & Alerting Guide** | DevOps | Phase 1 (skeleton) | `/docs/monitoring/` |
| **On-Call Handbook** | DevOps Lead | Phase 4 | `/docs/runbooks/on-call.md` |

### Runbook Template (per integration)

```markdown
# Runbook: [Integration Name]

## Overview
Brief description of what this integration does.

## Normal Behaviour
What healthy looks like (metrics, log patterns).

## Common Issues

### Issue: Consumer lag is high
Symptoms: Grafana alert fires for consumer group [group-name]
Steps:
1. Check consumer service logs: `kubectl logs -l app=consumer-service`
2. Check Kafka topic lag: `kafka-consumer-groups.sh --describe --group [group]`
3. Scale consumers: `kubectl scale deployment consumer-service --replicas=3`

### Issue: Dead-letter queue accumulating
Symptoms: DLQ topic [topic.dlq] has growing message count
Steps:
1. Pull a sample message from DLQ and inspect the error field
2. Fix the root cause (schema mismatch, downstream system down)
3. Replay DLQ messages after fix is deployed

## Escalation
- Primary: [On-call DevOps]
- Secondary: [Integration Lead]
- Business contact: [System Owner]
```

---

## Development Documents

| Document | Owner | When Created | Where Stored |
|---|---|---|---|
| **Developer Onboarding Guide** | DevOps + Lead Developer | Phase 1 | `/docs/onboarding.md` |
| **Coding Standards** | Integration Architect | Phase 0 | `/docs/standards.md` |
| **Testing Strategy** | QA Engineer | Phase 0 | `/docs/testing-strategy.md` |
| **Deployment Guide** | DevOps | Phase 1 | `/docs/deployment.md` |

### Developer Onboarding Guide — Minimum Content

```
[ ] Prerequisites (Docker, kubectl, kafka-cli, git)
[ ] How to clone and set up the repo
[ ] How to run docker compose up (local stack)
[ ] How to publish a test event locally
[ ] How to run the test suite
[ ] How to deploy to dev
[ ] Who to ask for help and what channels to use
```

---

## Governance & Compliance Documents

| Document | Owner | When Created | Where Stored |
|---|---|---|---|
| **Data Lineage Map** | BA + Data Engineer | Phase 2 | `/docs/compliance/data-lineage.md` |
| **Security & Auth Policy** | Security Engineer | Phase 0 | `/docs/compliance/security-policy.md` |
| **Data Retention Policy** | Lead Architect + Legal | Phase 0 | `/docs/compliance/retention-policy.md` |
| **Change Management Process** | Integration Architect | Phase 0 | `/docs/standards.md` |

---

## Documentation Health Checks

Run these checks at the end of each sprint:

```
[ ] Every integration in production has a runbook
[ ] All OpenAPI/AsyncAPI specs reflect the current implementation
[ ] Schema catalogue is up to date with Schema Registry
[ ] Data dictionary covers all PII fields
[ ] ADR written for any major decision made this sprint
[ ] Onboarding guide tested with a new team member in the last month
```
