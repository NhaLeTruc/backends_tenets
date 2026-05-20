# API Integration — Overview & Core Concepts

**Priority:** 10 — Background reference; foundational knowledge
**Phase:** Pre-project — Read before Phase 0 begins

---

## What is API Integration?

Connecting two or more systems so they can exchange data and trigger actions — typically over HTTP (REST, GraphQL) or via event streaming (Kafka, AMQP).

---

## Core Mechanics

| Concept | Description |
|---|---|
| **Request/Response** | Client sends a request (GET, POST, PUT, DELETE); server responds with data (usually JSON) |
| **Authentication** | API keys, OAuth 2.0, JWT tokens, or Basic Auth |
| **Base URL + Endpoints** | `https://api.example.com/v1/users` |
| **Headers** | `Content-Type: application/json`, `Authorization: Bearer <token>` |
| **HTTP Status Codes** | 200 OK, 201 Created, 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Server Error |

---

## HTTP Status Codes Reference

| Range | Meaning | Common Codes |
|---|---|---|
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirect | 301 Moved Permanently, 304 Not Modified |
| 4xx | Client Error | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests |
| 5xx | Server Error | 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable |

---

## Common Integration Patterns

| Pattern | Description | When to Use |
|---|---|---|
| **Polling** | Repeatedly call an endpoint to check for updates | Source system has no webhook support |
| **Webhooks** | Server pushes events to your endpoint when something happens | Real-time, low-latency requirements |
| **Event Streaming (Kafka)** | Continuous stream of events; consumers read at their own pace | High volume, decoupled, replay needed |
| **ETL / Batch** | Extract, Transform, Load on a schedule | Large data volumes, overnight sync |
| **Request/Response** | Direct API call, wait for response | Low-latency queries, transactional operations |
| **Message Queue** | Async, guaranteed delivery (RabbitMQ, SQS) | Decoupled, durable, ordered processing |

---

## Integration Approaches

| Approach | When to Use |
|---|---|
| Direct HTTP calls | Simple, one-off integrations |
| SDK / client library | Official SDKs reduce boilerplate |
| API gateway | Centralised auth, rate limiting, routing |
| ETL pipeline | Bulk data sync between systems |
| Message queue / event stream | Async, decoupled integration |
| iPaaS (MuleSoft, Boomi) | Low-code, many out-of-box connectors |

---

## Key Concerns in Any Integration

### Error Handling
- Always implement retry logic with **exponential backoff**
- Define a **dead-letter queue (DLQ)** for messages that fail after retries
- Log all failures with enough context to replay or debug
- Use **correlation IDs** to trace a request across services

### Rate Limiting
- Respect `Retry-After` headers from external APIs
- Implement client-side rate limiting to avoid hitting limits
- Use a token bucket or leaky bucket algorithm for outbound requests

### Data Contracts
- Validate payloads at system boundaries — never trust the shape of external responses
- Use schema validation (JSON Schema, Avro) at the point of consumption
- Document contracts in OpenAPI (REST) and AsyncAPI (events)

### Security
- Never hardcode API keys or secrets — use environment variables or a secrets manager
- Validate and sanitise all incoming data before processing
- Use TLS (HTTPS) for all API communication
- Rotate secrets on a schedule; revoke immediately if compromised

### Idempotency
- Design consumers and endpoints to be **idempotent** — safe to call multiple times with the same result
- Use `idempotency-key` headers for mutation endpoints (POST, PUT)
- Track processed `event_id` values to prevent duplicate processing

### Timeouts
- Always set explicit timeouts on outbound HTTP calls — external APIs can hang
- Use circuit breakers (Resilience4j, Hystrix) to fail fast when a downstream is degraded

---

## Typical Modern Stack (This Project)

```
FastAPI / Spring Boot  →  PostgreSQL  →  Kafka  →  Kong Gateway  →  Docker/K8s  →  Prometheus/Grafana  →  GitHub Actions
```

**Best suited for:**
- Real-Time Data Pipelines
- Internal Enterprise Integration Hub
- Microservices platforms
- B2B API platforms
- Event-driven integrations

---

## Recommended Reading

| Resource | Why |
|---|---|
| *Designing Data-Intensive Applications* — Martin Kleppmann | Best book on Kafka, streaming, and data pipelines |
| *Enterprise Integration Patterns* — Hohpe & Woolf | Canonical reference for integration patterns |
| *Building Microservices* — Sam Newman | Service boundaries, APIs, event-driven design |
| Zalando RESTful API Guidelines | Practical, opinionated REST design guide |
| Confluent Developer Docs | Kafka patterns, schema registry, best practices |
| Google API Design Guide | Naming and REST pattern conventions |
| CloudEvents Spec | Vendor-neutral event envelope standard |
