# Walking Skeleton

**Priority:** 4 — Validate the full stack end-to-end before building real features
**Phase:** 1 — Foundation (Week 4–7)

---

## Purpose

Stand up a minimal, working end-to-end pipeline using one test event before building any real integrations. Validates that all infrastructure components are connected and operational.

---

## Methodology: Walking Skeleton (Alistair Cockburn)

> *"A tiny implementation of the system that performs a small end-to-end function. It need not use the final architecture, but it should link together the main architectural components."*

The goal: **one event, flowing end-to-end**, before building anything real.

---

## Walking Skeleton Checklist

### Infrastructure
```
[ ] Kafka cluster running (local: Docker Compose; cloud: Confluent / MSK / Azure Event Hubs)
[ ] Schema Registry running and reachable
[ ] PostgreSQL instance running
[ ] Kong Gateway running with one route configured
[ ] Prometheus + Grafana running with one dashboard visible
[ ] GitHub Actions pipeline: lint → test → build → deploy to dev
[ ] Secrets manager configured (Vault / AWS Secrets Manager / Azure Key Vault)
[ ] Dev / Staging / Prod environments provisioned
```

### Code
```
[ ] One producer service: publishes a test event to a Kafka topic
[ ] One consumer service: reads the event and writes to PostgreSQL
[ ] One REST endpoint: exposed through Kong, returns data from PostgreSQL
[ ] Schema registered in Schema Registry for the test event
[ ] End-to-end test:
      trigger producer
      → verify event in Kafka topic
      → verify data written to PostgreSQL
      → verify API response through Kong
```

### Observability
```
[ ] Logs flowing to a central location (ELK, Datadog, CloudWatch)
[ ] Kafka consumer lag metric visible in Grafana
[ ] API latency metric visible in Grafana
[ ] At least one alert configured (consumer lag threshold)
[ ] Distributed trace visible for one request (Jaeger / Zipkin)
```

---

## Local Dev Environment (Docker Compose)

Every developer must be able to run the full stack locally with one command:

```bash
docker compose up
```

### Minimum `docker-compose.yml` Services

| Service | Image | Purpose |
|---|---|---|
| zookeeper | confluentinc/cp-zookeeper | Kafka coordination |
| kafka | confluentinc/cp-kafka | Event broker |
| schema-registry | confluentinc/cp-schema-registry | Schema validation |
| postgres | postgres:15 | Relational storage |
| kong | kong:latest | API gateway |
| konga | pantsel/konga | Kong admin UI |
| prometheus | prom/prometheus | Metrics collection |
| grafana | grafana/grafana | Metrics dashboards |
| producer-service | (your image) | Test event publisher |
| consumer-service | (your image) | Test event consumer |

---

## Definition of Done for Walking Skeleton

The skeleton is complete when:

1. A developer can run `docker compose up` and have the full stack running in under 5 minutes
2. The end-to-end test passes: event in → data in PostgreSQL → API response out
3. Consumer lag and API latency are visible in Grafana
4. GitHub Actions deploys a change to the dev environment on push to `dev` branch
5. A second developer can follow the onboarding guide and reproduce all of the above independently

---

## Skeleton vs. Production Differences to Note

| Concern | Skeleton | Production |
|---|---|---|
| Kafka replication | 1 (local) | 3+ brokers |
| PostgreSQL | Single instance | HA with replica |
| Kong | Basic routing | Auth plugins, rate limiting |
| Secrets | `.env` file | Vault / cloud secrets manager |
| Monitoring | Basic dashboard | Full alerting, on-call |
| TLS | Off | Enforced everywhere |

Document these gaps as tickets in the backlog to close during Phase 3 (Harden).

---

## Output of This Step

- Running local dev environment (Docker Compose)
- One end-to-end pipeline proven in dev environment
- CI/CD pipeline deploying to dev on every push
- Initial Grafana dashboard with Kafka and API metrics
- Developer onboarding guide validated by a second team member

---

## References

- Walking Skeleton — alistair.cockburn.us
- Confluent Docker Compose examples — docs.confluent.io
- Kong Docker setup — docs.konghq.com
- Prometheus + Grafana — prometheus.io / grafana.com
