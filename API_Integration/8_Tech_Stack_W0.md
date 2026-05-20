# Tech Stack & Tools Reference

**Priority:** 8 — Reference document; decisions made in Phase 0
**Phase:** 0 — Selected before Phase 1 begins

---

## Recommended Stack for This Project

> **Use Cases:** Real-Time Data Pipelines + Internal Enterprise Integration Hub

```
FastAPI / Spring Boot  →  PostgreSQL  →  Kafka  →  Kong Gateway  →  Docker/K8s  →  Prometheus/Grafana  →  GitHub Actions
```

---

## API Protocols & Standards

| Type | Tool/Standard | Notes |
|---|---|---|
| REST | OpenAPI 3.1 | Primary API style for internal services |
| Event Streaming | AsyncAPI 2.x | Documents Kafka topics |
| Schema Format | Apache Avro | Compact, schema-evolution-safe (Kafka) |
| Event Envelope | CloudEvents | Vendor-neutral standard event wrapper |

---

## API Gateway

| Tool | Notes |
|---|---|
| **Kong** | Recommended: open-source, plugin ecosystem, K8s-native |
| AWS API Gateway | If deploying to AWS |
| Azure API Management | If deploying to Azure |

---

## Event Streaming

| Tool | Notes |
|---|---|
| **Apache Kafka** | Core event broker |
| **Confluent Schema Registry** | Schema validation and versioning |
| **Confluent Cloud** | Managed Kafka (recommended for teams new to Kafka) |
| AWS MSK | Managed Kafka on AWS |
| Azure Event Hubs | Managed Kafka-compatible on Azure |

---

## Backend Frameworks

| Language | Framework | When to Use |
|---|---|---|
| Python | **FastAPI** | Lightweight services, data pipelines, rapid development |
| Java | **Spring Boot** | Enterprise integrations, existing Java ecosystem |
| Node.js | NestJS | If team is JS-first |
| Go | Gin / Fiber | High-throughput consumers where performance matters |

---

## Database

| Type | Tool | Use Case |
|---|---|---|
| Relational | **PostgreSQL** | Primary structured data store |
| Cache | **Redis** | Rate limiting, session data, short-lived state |
| Search | Elasticsearch | Log search, full-text event querying |

---

## Messaging & Queuing

| Tool | Use Case |
|---|---|
| **Kafka** | High-throughput real-time event streaming |
| **Dead-Letter Queue (DLQ)** | Separate Kafka topic for failed messages |
| Redis Pub/Sub | Lightweight, low-latency internal notifications |

---

## Authentication & Security

| Tool | Purpose |
|---|---|
| **OAuth 2.0 / OIDC** | Standard auth delegation |
| **JWT** | Stateless token auth for service-to-service |
| **Keycloak** | Self-hosted identity and auth server |
| Auth0 / Okta | Managed identity provider (if budget allows) |
| **HashiCorp Vault** | Secrets management (recommended) |
| AWS Secrets Manager | Cloud-native secrets if on AWS |

---

## Testing Tools

| Tool | Type | Notes |
|---|---|---|
| **Pytest + requests** | Unit + API tests | Python services |
| **REST Assured** | API tests | Java services |
| **Pact** | Contract tests | Consumer-driven contract testing |
| **Postman / Newman** | Manual + CI API tests | Smoke tests, exploratory |
| **k6** | Load testing | Scripted, developer-friendly |
| **Locust** | Load testing | Python-based, good for complex scenarios |
| **WireMock** | API mocking | Mock external systems in tests |

---

## Monitoring & Observability

| Tool | Purpose |
|---|---|
| **Prometheus** | Metrics collection |
| **Grafana** | Dashboards and alerting |
| **Jaeger** | Distributed tracing |
| **ELK Stack** (Elasticsearch + Logstash + Kibana) | Log aggregation and search |
| **PagerDuty** | Incident alerting and on-call management |
| Datadog | All-in-one (if budget allows) |

### Key Metrics to Monitor

| Metric | Tool | Alert Threshold |
|---|---|---|
| Kafka consumer lag | Prometheus / Grafana | > 1000 messages |
| API latency p99 | Prometheus / Grafana | > 2 seconds |
| Error rate | Prometheus / Grafana | > 1% over 5 minutes |
| DLQ message count | Prometheus / Grafana | > 0 (any failure is an alert) |
| PostgreSQL connection pool | Prometheus | > 80% utilized |

---

## Infrastructure & DevOps

| Tool | Purpose |
|---|---|
| **Docker** | Containerization |
| **Kubernetes (K8s)** | Container orchestration |
| **Helm** | Kubernetes package management |
| **Terraform** | Infrastructure as code |
| **GitHub Actions** | CI/CD pipelines |

---

## Documentation Tools

| Tool | Purpose |
|---|---|
| **Swagger Editor / Stoplight** | Write and validate OpenAPI specs |
| **AsyncAPI Studio** | Write and validate AsyncAPI specs |
| **Redoc** | Render OpenAPI docs for consumers |
| **Miro / Mural** | Event Storming and architecture workshops |
| **draw.io / Lucidchart** | C4 diagrams and data flow diagrams |

---

## Local Development

| Tool | Purpose |
|---|---|
| **Docker Compose** | Full local stack in one command |
| **Kafka CLI** (`kafka-console-producer`, `kafka-console-consumer`) | Test events locally |
| **Postman / Insomnia** | Manual API testing |
| **k9s** | Kubernetes CLI dashboard |

---

## References

- Confluent Developer Hub — developer.confluent.io
- Kong Docs — docs.konghq.com
- FastAPI Docs — fastapi.tiangolo.com
- Spring Boot Docs — docs.spring.io/spring-boot
- Prometheus Docs — prometheus.io/docs
- Terraform Docs — developer.hashicorp.com/terraform
