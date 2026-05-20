# Project Timeline

**Priority:** 5 — Planning reference for the full project
**Phase:** 0 — Established in Week 1

---

## Use Cases Covered

- Real-Time Data Pipelines
- Internal Enterprise Integration Hub

---

## Phase Overview

| Phase | Name | Weeks | Goal |
|---|---|---|---|
| 0 | Discovery & Design | 1–3 | Know what to build before building it |
| 1 | Foundation | 4–7 | Prove the stack works end-to-end |
| 2 | Core Integrations | 8–16 | Build the first high-priority integrations |
| 3 | Expand & Harden | 17–24 | Onboard remaining systems, add resilience |
| 4 | Stabilize & Handover | 25–28 | Ops-ready, team trained, project closed |

---

## Phase 0 — Discovery & Design (Weeks 1–3)

**Goal:** Know every system, data flow, and contract before writing code.

- [ ] Run stakeholder workshops to identify all source and target systems
- [ ] Complete Integration Inventory (see `1_Integration_Inventory_W1.md`)
- [ ] Run Event Storming session; identify all domain events
- [ ] Define and register initial event schemas (see `2_Event_Schema_Design_W2.md`)
- [ ] Write OpenAPI specs for all REST APIs (see `3_API_First_Design_W3.md`)
- [ ] Draw Context and Container diagrams (C4 Model)
- [ ] Confirm tech stack and cloud/infrastructure approach
- [ ] Set up source control, branch strategy, and environments (dev/staging/prod)
- [ ] Draft project documentation structure (see `7_Documentation_Requirements_W1.md`)

**Milestone:** Integration Inventory complete + all schemas and API specs reviewed and signed off.

---

## Phase 1 — Foundation (Weeks 4–7)

**Goal:** One event flowing end-to-end through the full stack.

- [ ] Provision Kafka cluster (cloud or self-hosted)
- [ ] Provision Schema Registry
- [ ] Provision PostgreSQL (with HA plan for prod)
- [ ] Deploy Kong API Gateway with base auth policy
- [ ] Set up CI/CD pipelines (GitHub Actions: lint → test → build → deploy to dev)
- [ ] Deploy Prometheus + Grafana with initial dashboards
- [ ] Implement Walking Skeleton (see `4_Walking_Skeleton_W4.md`)
- [ ] Validate local dev environment (`docker compose up`)
- [ ] Onboard all developers to local environment

**Milestone:** Walking Skeleton end-to-end test passes in dev. CI/CD deploys on push.

---

## Phase 2 — Core Integrations (Weeks 8–16)

**Goal:** First 2–3 highest-priority integrations in production.

- [ ] Build Producer services for priority integrations
- [ ] Build Consumer services for priority integrations
- [ ] Configure Kong routes and auth for exposed APIs
- [ ] Write consumer-driven contract tests (Pact)
- [ ] Write integration tests per integration
- [ ] Deploy to staging; run load tests (k6/Locust)
- [ ] Security review: auth, secrets, data masking (see `9_IT_Roles_W0.md`)
- [ ] Deploy first integrations to production
- [ ] Monitor for 1 week before declaring stable

**Milestone:** First integrations live in production, monitored, and stable.

---

## Phase 3 — Expand & Harden (Weeks 17–24)

**Goal:** All integrations onboarded; system resilient under failure.

- [ ] Onboard remaining systems and integrations from the inventory
- [ ] Implement dead-letter queues (DLQ) for all Kafka consumers
- [ ] Implement retry logic with exponential backoff
- [ ] Add circuit breakers for downstream API calls
- [ ] Full security review and penetration test
- [ ] Performance and load testing across all integrations
- [ ] Tune Kafka partition counts and consumer group scaling
- [ ] Finalize all runbooks and incident response playbooks
- [ ] Complete monitoring dashboards and alert tuning

**Milestone:** All integrations in production. System handles failure gracefully.

---

## Phase 4 — Stabilize & Handover (Weeks 25–28)

**Goal:** Operations team can own and run the platform independently.

- [ ] All operational runbooks complete and reviewed
- [ ] On-call rotation established and trained
- [ ] Post-implementation review conducted
- [ ] Architecture documentation finalized
- [ ] Lessons learned documented
- [ ] Handover to operations team signed off by stakeholders

**Milestone:** Project closed. Platform owned by operations team.

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Source system has no API | Medium | High | Plan SFTP/DB fallback in inventory phase |
| Schema changes break consumers | Medium | High | Schema Registry + contract tests |
| Kafka cluster sizing wrong | Low | High | Load test in Phase 3 before full rollout |
| Team unfamiliar with Kafka | Medium | Medium | Walking Skeleton in Phase 1 as learning exercise |
| Stakeholder unavailability for workshops | Medium | Medium | Schedule workshops in Week 1 |
| Integration scope creep | High | Medium | Lock inventory in Phase 0; change requests go through backlog |
