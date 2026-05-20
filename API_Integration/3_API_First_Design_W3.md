# API-First Design

**Priority:** 3 — Spec is the contract; write it before writing code
**Phase:** 0 — Discovery & Design (Week 3)

---

## Purpose

Define REST API contracts in OpenAPI before implementation. Consumers (frontend, partner teams, other services) build against a mock while the real service is being built — eliminating integration surprises.

---

## Methodology: API-First / Design-First

Popularized by Swagger/OpenAPI and adopted by Stripe, Twilio, and Atlassian. The spec is the single source of truth for a service's contract.

### API-First Workflow

1. Write OpenAPI spec (YAML) for REST endpoints
2. Write AsyncAPI spec for Kafka topics
3. Review spec with consumer teams
4. Generate mock server from spec (Prism, WireMock)
5. Consumers build against the mock
6. Implement the real service
7. Contract tests verify the real implementation matches the spec

---

## API Design Checklist

```
[ ] OpenAPI 3.x spec written before any code
[ ] Consistent naming: plural nouns for resources (/employees, /invoices)
[ ] HTTP verbs used correctly:
      GET    = read (no side effects)
      POST   = create
      PUT    = full replace
      PATCH  = partial update
      DELETE = remove
[ ] Pagination defined for all list endpoints (limit/offset or cursor)
[ ] Error response schema standardized (RFC 7807 Problem Details)
[ ] Auth scheme documented in spec (OAuth2, API Key, JWT)
[ ] Versioning strategy agreed: URL (/v1/) or header
[ ] All endpoints have request/response examples
[ ] Breaking vs. non-breaking change policy documented
[ ] Spec reviewed by at least one consumer team before implementation
[ ] Mock server generated and shared with consumers
```

---

## Standard Error Response (RFC 7807)

All error responses must follow this shape:

```json
{
  "type": "https://errors.example.com/validation-error",
  "title": "Validation Error",
  "status": 400,
  "detail": "The field 'email' is required.",
  "instance": "/v1/employees/hire"
}
```

---

## Versioning Strategy

| Strategy | Format | When to Use |
|---|---|---|
| URL versioning | `/v1/employees` | Recommended default — explicit and cacheable |
| Header versioning | `Accept: application/vnd.api+json;version=1` | When URLs must stay stable |
| Query param | `/employees?version=1` | Avoid — pollutes query space |

**Rule:** A breaking change always requires a new version. Non-breaking additions (new optional fields, new endpoints) do not.

### Breaking vs. Non-Breaking Changes

| Change | Breaking? |
|---|---|
| Add optional request field | No |
| Add response field | No |
| Remove request/response field | Yes |
| Rename field | Yes |
| Change field type | Yes |
| Change HTTP status code | Yes |
| Remove endpoint | Yes |

---

## Pagination Standard

Use `limit` / `offset` for simple cases; cursor-based for large or real-time datasets.

```json
{
  "data": [],
  "pagination": {
    "total": 1500,
    "limit": 50,
    "offset": 100,
    "next_cursor": "eyJpZCI6MTAwfQ=="
  }
}
```

---

## OpenAPI Spec Minimum Structure

```yaml
openapi: 3.1.0
info:
  title: Employee Service API
  version: 1.0.0
  description: Manages employee records

servers:
  - url: https://api.internal.example.com/v1

security:
  - bearerAuth: []

paths:
  /employees:
    get:
      summary: List employees
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
      responses:
        '200':
          description: Success
        '401':
          description: Unauthorized

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

## Tools

| Tool | Purpose |
|---|---|
| **Stoplight Studio** | Visual API design editor |
| **Swagger Editor** | OpenAPI spec editor (browser-based) |
| **Prism** | Mock server generated from OpenAPI spec |
| **WireMock** | API mocking for testing |
| **Redoc** | Render OpenAPI docs for consumers |
| **Spectral** | Lint OpenAPI specs for style violations |

---

## Output of This Step

- OpenAPI specs per REST service
- AsyncAPI specs per Kafka topic (from Step 2)
- Mock servers running for all APIs
- API design review sign-off from consumer teams

---

## References

- OpenAPI 3.1 Spec — openapi.org
- AsyncAPI 2.x Spec — asyncapi.com
- RFC 7807 Problem Details — datatracker.ietf.org/doc/html/rfc7807
- Google API Design Guide — cloud.google.com/apis/design
- Zalando RESTful API Guidelines — opensource.zalando.com/restful-api-guidelines
