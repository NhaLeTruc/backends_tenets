# Way of Working

**Priority:** 6 — Team process and governance established in Week 1
**Phase:** 0 — Established before first sprint

---

## Team Structure

| Role | Responsibilities |
|---|---|
| **Integration Lead / Architect** | Owns design decisions, API contracts, Kafka topic governance |
| **Backend / Integration Developers (x2–3)** | Build producers, consumers, REST APIs |
| **DevOps Engineer** | Infrastructure, CI/CD, Kubernetes, monitoring |
| **QA Engineer** | Contract testing, integration tests, load tests |
| **BA / Data Analyst** | Data mapping specs, stakeholder liaison, integration inventory |

---

## Delivery Method: 2-Week Sprints (Agile/Scrum)

Each sprint follows this rhythm:

| Day | Activity |
|---|---|
| Day 1 | Sprint Planning — pull from backlog, assign, estimate |
| Days 2–8 | Build — feature branches, PRs, code review |
| Day 9 | Internal Demo — show working integration to team |
| Day 10 | Stakeholder Demo + Retrospective |

**Treat each integration as a vertical slice:** design → build → test → deploy → monitor.

---

## Backlog Management

- Backlog is the **Integration Inventory** (see `1_Integration_Inventory_W1.md`) ranked by business value and risk
- Each integration becomes one or more user stories
- Stories follow: *"As [consumer system], I need [event/data] so that [business outcome]"*
- Priority order: highest business value + lowest technical risk first

---

## Branching Strategy

```
main        ← production-ready only; protected branch
dev         ← integration branch; auto-deploys to dev environment
feature/*   ← one branch per integration or feature
hotfix/*    ← production fixes only
```

**Rules:**
- `main` requires PR + 2 approvals + all CI checks passing
- `dev` requires PR + 1 approval + all CI checks passing
- Feature branches named: `feature/hr-employee-events`, `feature/finance-invoice-consumer`
- No direct commits to `main` or `dev`

---

## CI/CD Pipeline (GitHub Actions)

Every push to a feature branch triggers:
1. Lint (code style checks)
2. Unit tests
3. Contract tests (Pact)
4. Build Docker image
5. Push to container registry

Every merge to `dev` triggers:
1. All above steps
2. Integration tests against dev environment
3. Deploy to dev environment

Merge to `main` (via PR from `dev`) triggers:
1. All above steps
2. Deploy to staging
3. Manual approval gate
4. Deploy to production

---

## API Governance

- All Kafka topic schemas registered in **Schema Registry** before first publish
- All REST APIs documented in **OpenAPI specs** before build starts (design-first)
- API breaking changes require a **breaking change review** meeting before merging
- Schema changes follow the versioning rules in `2_Event_Schema_Design_W2.md`
- New Kafka topics require approval from the Integration Architect

---

## Code Review Standards

Every PR requires:
```
[ ] OpenAPI/AsyncAPI spec updated if contract changed
[ ] Unit tests cover new logic
[ ] No hardcoded secrets or credentials
[ ] Error handling: retries, dead-letter queue, logging
[ ] Structured logging (JSON format, include correlation_id)
[ ] No print/console.log left in code
[ ] Docker image builds successfully
```

---

## Communication

| Channel | Purpose |
|---|---|
| `#int-general` | Team-wide announcements |
| `#int-[domain]` | Per-domain channel (e.g. `#int-hr`, `#int-finance`) |
| `#int-incidents` | Incident alerts and response |
| Weekly stakeholder sync | Integration status, blockers, upcoming changes |
| PR comments | Technical decisions on specific changes |
| ADRs | Architectural decisions that affect the whole platform |

**Async-first:** Decisions made in PRs and ADRs, not lost in chat.

---

## Architecture Decision Records (ADRs)

For any non-trivial technical decision (e.g. why Kafka over RabbitMQ, why cursor pagination):

```markdown
# ADR-001: Use Kafka for event streaming

## Status
Accepted

## Context
We need async, decoupled communication between services with replay capability.

## Decision
Use Apache Kafka (Confluent Cloud) as the event streaming platform.

## Consequences
+ Replay capability for consumers
+ High throughput and durability
- Operational complexity vs. simpler queues
- Team needs Kafka training
```

Store ADRs in `/docs/adr/` in the repository.

---

## Definition of Done (DoD)

An integration is "Done" when:
```
[ ] OpenAPI/AsyncAPI spec written and reviewed
[ ] Producer and/or consumer implemented
[ ] Unit tests passing (>80% coverage on business logic)
[ ] Contract tests passing (Pact)
[ ] Integration tests passing in dev environment
[ ] Deployed to staging and smoke-tested
[ ] Grafana dashboard updated with new metrics
[ ] Runbook written for this integration
[ ] Deployed to production and monitored for 48 hours
[ ] Stakeholder sign-off received
```
