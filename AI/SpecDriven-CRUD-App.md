# Spec Kit

## What is Spec-Driven Development?

Spec-Driven Development flips the script on traditional software development. For decades, code has been king — specifications were just scaffolding we built and discarded once the "real work" of coding began. Spec-Driven Development changes this: specifications become executable, directly generating working implementations rather than just guiding them.

## Get started

```bash
# If not installed
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

specify init crud-postgres-app
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd crud-postgres-app && code .
# optional
specify check
```

## Constitution

Use the `/speckit.constitution` command to create your project's governing principles and development guidelines that will guide all subsequent development.

```bash
/speckit.constitution Create principles focused on clean code, strict TDD adherent, decoupled architecture, site reliability engineering or SRE, observability, and web security best practice for  an generic ecommerce website.
```

## Specify

Use the `/speckit.specify` command to describe what you want to build. Focus on the what and why, not the tech stack.

```txt
/speckit.specify Build an generic ecommerce website with these qualities:

## Core System Architecture

**Multi-tier service architecture with clear boundaries** - I'd build the system as loosely coupled services, each owning specific business capabilities. This isolation prevents cascading failures and enables independent scaling and deployment. Services would include product catalog, inventory management, cart/checkout, payment processing, order fulfillment, user accounts, and search/recommendations.

**Asynchronous event-driven communication** - Services communicate through message queues and event streams rather than synchronous calls where possible. This decoupling improves resilience, allows retry mechanisms, and prevents one slow service from blocking others. Order placement, for example, would emit events that trigger inventory updates, payment processing, and fulfillment workflows independently.

## Reliability & Resilience

**Circuit breakers and graceful degradation** - Every service interaction includes circuit breakers that open when error rates exceed thresholds. When payment processing is down, customers can still browse products and add to cart. When recommendations fail, the site shows default popular products instead of erroring out.

**Idempotent operations everywhere** - All critical operations (payments, order placement, inventory updates) are idempotent with unique request IDs. This prevents double charges when customers retry submissions and enables safe automatic retries during transient failures.

**Rate limiting and backpressure mechanisms** - Implement tiered rate limiting at multiple levels - per user, per API endpoint, and global limits. This protects against both malicious attacks and legitimate traffic spikes. Services communicate backpressure upstream when overwhelmed.

**Bulkheading and resource isolation** - Separate thread pools, connection pools, and compute resources for different operation types. Slow search queries won't starve checkout processes. Background batch jobs run on isolated infrastructure from customer-facing services.

## Observability & Monitoring

**Distributed tracing across all services** - Every request generates a unique trace ID that follows it through all service hops. This enables quick root cause analysis when issues arise and helps identify performance bottlenecks across the entire request flow.

**Structured logging with correlation** - All logs include structured metadata (user ID, session ID, trace ID, business context) enabling powerful queries. Instead of grepping through text logs, you can instantly find all operations for a specific order or customer.

**Business and technical metrics** - Beyond system metrics (CPU, memory, latency), track business KPIs in real-time: cart abandonment rates, payment success rates, search-to-purchase conversion, inventory turnover. Sudden changes in business metrics often indicate technical issues before they trigger system alerts.

**Synthetic monitoring and real user monitoring** - Continuously run synthetic transactions (browse → add to cart → checkout) from multiple geographic locations. Combine this with real user performance data to understand actual customer experience.

**Error budgets and SLOs** - Define service level objectives for critical user journeys (99.9% success rate for checkout, p99 latency under 2s for product pages). Track error budgets to balance reliability work against feature development.

## Security Architecture

**Zero-trust internal network** - Services authenticate and authorize every request, even internal ones. No implicit trust based on network location. Each service has its own credentials and limited permissions.

**Encryption everywhere** - TLS for all network communication, encryption at rest for all data stores. Sensitive data like payment tokens are additionally encrypted at the application level with separate key management.

**Input validation and parameterized queries** - Every service validates inputs against strict schemas. All database queries use parameterized statements or ORMs that prevent injection attacks. API gateways enforce request schemas before routing.

**Secrets management and rotation** - No hardcoded credentials anywhere. All secrets stored in a centralized vault with automatic rotation. Services authenticate using short-lived tokens rather than long-lived credentials.

**PCI compliance isolation** - Payment processing runs in an isolated, highly restricted environment. The main application never touches raw credit card data, only tokens. This minimizes PCI compliance scope and reduces security risk.

## Data Management

**CQRS pattern for read/write separation** - Separate optimized read models from write models. Product catalog reads come from denormalized, cached views while inventory updates go through a different path with stronger consistency guarantees.

**Event sourcing for critical operations** - Store all state changes as events for orders and payments. This provides complete audit trails, enables replay for debugging, and supports compensating transactions when needed.

**Multi-region data replication** - Replicate data across regions for disaster recovery and to serve customers from nearby locations. Implement clear strategies for handling split-brain scenarios and ensuring eventual consistency.

## Performance & Scalability

**Intelligent caching hierarchy** - Multiple cache layers from CDN for static assets, to application-level caches for database queries, to browser caching. Cache invalidation strategies that balance freshness with performance.

**Database connection pooling and query optimization** - Careful management of database connections with pooling, query timeouts, and automatic slow query detection. Read replicas for reporting and analytics to avoid impacting transactional workloads.

**Capacity planning and auto-scaling** - Predictive scaling based on historical patterns (Black Friday traffic is predictable) combined with reactive auto-scaling for unexpected spikes. Regular load testing to validate scaling assumptions.

## Operational Excellence

**Immutable infrastructure and GitOps** - All infrastructure defined as code, version controlled, and deployed through automated pipelines. No manual changes to production systems. Every deployment is reproducible and auditable.

**Canary deployments and feature flags** - New code gradually rolls out to small percentages of traffic with automatic rollback on error threshold breaches. Feature flags enable instant disabling of problematic features without deployments.

**Runbooks and automated remediation** - Documented procedures for common issues with as much automation as possible. When disk space alerts fire, automated cleanup runs before paging on-call. When services crash, they automatically restart with exponential backoff.

**Chaos engineering practices** - Regularly inject failures in production (carefully) to verify resilience mechanisms work. Randomly kill services, introduce network latency, and fill up disks to ensure the system degrades gracefully.
```

## Clarify

Clarify and de-risk specification (run before /plan)

```bash
/speckit.clarify
```

## Plan

Use the `/speckit.plan` command to provide your tech stack and architecture choices.

```txt
/speckit.plan Build the generic ecommerce website using this tech stack:

## Local Testing:

**Docker Compose images**
- postgres:15-alpine
- mongo:7
- redis:7-alpine
- opensearchproject/opensearch:2
- bitnami/kafka:latest
- rabbitmq:3-management-alpine
- prom/prometheus
- grafana/grafana-oss
- jaegertracing/all-in-one
- minio/minio

## Core Application Stack

**Backend Services**
- **Go** for high-performance services (payment processing, inventory, checkout)
- **Node.js/TypeScript** for API Gateway and BFF layers
- **Python/FastAPI** for ML services (recommendations, search)
- **Rust** (optional) for extremely performance-critical components

**Frontend**
- **Next.js 14** (open source) for main customer site
- **React Native** for mobile apps
- **Remix** (open source) for admin dashboards
- **Vue.js with Nuxt** as alternative for specific microsites

## Data Layer

**Primary Databases**
- **PostgreSQL 15** for transactional data
  - **Citus** extension for horizontal scaling (open source)
  - **TimescaleDB** extension for time-series data
  - **PgBouncer** for connection pooling
- **MongoDB Community Edition** for product catalog
  - Self-hosted cluster with replica sets
- **CockroachDB** as alternative for distributed SQL

**Caching & Session Storage**
- **Redis** (open source) for caching and sessions
  - **KeyDB** as multi-threaded Redis alternative
- **DragonflyDB** for Redis-compatible, more efficient caching
- **Apache Druid** for real-time analytics (open source)
- **ClickHouse** for analytical workloads

**Search & Recommendations**
- **OpenSearch** (Elasticsearch fork) for product search
  - Fully open source, no license restrictions
- **Meilisearch** for simpler search needs
  - Typo-tolerant, fast, easy to use
- **Apache Solr** as mature alternative
- **Qdrant** or **Weaviate** for vector search (AI-powered recommendations)

## Message Queue & Event Streaming

- **Apache Kafka** for event streaming
  - **Redpanda** as Kafka-compatible alternative (no Zookeeper needed)
- **RabbitMQ** for traditional messaging
- **NATS** for lightweight, high-performance messaging
- **Apache Pulsar** as unified streaming/queuing platform

## Infrastructure & Orchestration

**Container Orchestration**
- **Kubernetes** (K8s) self-hosted or using free tiers
  - **K3s** for lightweight production deployments
  - **MicroK8s** for edge deployments
- **Istio** service mesh (open source)
  - **Linkerd** as lighter-weight alternative
  - **Cilium** for eBPF-based networking and observability
- **ArgoCD** for GitOps deployments
- **Flux** as ArgoCD alternative

**Infrastructure as Code**
- **OpenTofu** (Terraform open-source fork)
- **Terraform** (open source core)
- **Pulumi** (open source version)
- **Ansible** for configuration management
- **Crossplane** for Kubernetes-native infrastructure management

## Observability Stack

**Metrics & Monitoring**
- **Prometheus** + **Grafana** for metrics and visualization
- **VictoriaMetrics** for long-term metrics storage
  - More efficient than Prometheus for storage
- **Thanos** for Prometheus high availability
- **Mimir** (Grafana) for scalable Prometheus storage

**Logging**
- **Fluentd** or **Fluent Bit** for log collection
- **OpenSearch** + **OpenSearch Dashboards** for log analysis
- **Grafana Loki** for cost-effective logging
  - Integrates perfectly with Grafana
- **Vector** by Datadog (open source) for log pipeline

**Tracing**
- **OpenTelemetry** for instrumentation
- **Jaeger** for distributed tracing
- **Grafana Tempo** for cloud-native tracing
- **Apache SkyWalking** for APM and tracing
- **SigNoz** for complete observability (metrics, traces, logs)

**Error Tracking**
- **Sentry** (self-hosted open source version)
- **GlitchTip** (Sentry-compatible alternative)
- **Rollbar** (open source version)

## Security & Compliance

**Secrets Management**
- **HashiCorp Vault** (open source version)
- **Infisical** (open-source secret management)
- **Sealed Secrets** for Kubernetes
- **Mozilla SOPS** for encrypted secrets in Git
- **Bitwarden** Secrets Manager (open source)

**Security Scanning**
- **Trivy** for vulnerability scanning
- **Grype** + **Syft** for container scanning
- **Clair** for container vulnerability analysis
- **Falco** for runtime security
- **OWASP ZAP** for security testing
- **Nuclei** for vulnerability scanning
- **Semgrep** for static code analysis

**WAF & Protection**
- **ModSecurity** with **OWASP Core Rule Set**
- **Coraza** (ModSecurity-compatible WAF)
- **Shadow Daemon** for web application firewall
- **CrowdSec** for collaborative security

## API Gateway & Edge

**API Management**
- **Kong Gateway** (open source version)
- **Apache APISIX** for API gateway
- **Tyk** (open source gateway)
- **KrakenD** for API gateway with backend for frontend
- **Envoy Proxy** for service proxy

**CDN & Static Assets**
- **Cloudflare** (free tier - 10,000 requests/day)
- **jsDelivr** (free CDN for open source)
- **Fastly** (free tier available)
- Self-hosted CDN using:
  - **Varnish Cache** for HTTP acceleration
  - **nginx** with caching modules

**Image Processing**
- **Thumbor** for image optimization
- **Imaginary** for fast image processing
- **ImageMagick** or **Sharp** for image manipulation

**Testing Tools**
- **k3s** or **kind** for local Kubernetes
- **LocalStack** (Community Edition) for AWS emulation
- **TestContainers** for integration testing
- **WireMock** for API mocking
- **MinIO** for S3-compatible storage
- **MailHog** or **MailCatcher** for email testing

**Load Testing**
- **k6** (open source) for load testing
- **Locust** for distributed load testing
- **Apache JMeter** for comprehensive testing
- **Vegeta** for HTTP load testing
- **Grafana k6** for modern load testing

## CI/CD Pipeline

**CI/CD Platform**
- **GitLab CE** (Community Edition) self-hosted
- **Jenkins** with Blue Ocean UI
- **Drone CI** (open source)
- **Woodpecker CI** (Drone fork)
- **Gitea** + **Gitea Actions** (GitHub alternative)
- **Forgejo** (Gitea fork) with actions

**Quality Gates**
- **SonarQube** Community Edition
- **CodeCov** (limited free tier) or **Codecov** self-hosted
- **Lighthouse** CI for performance
- **BackstopJS** for visual regression testing
- **Percy** (free tier) or **Playwright** for visual testing

## Supporting Services

**Feature Flags**
- **Unleash** (open source feature flags)
- **Flagsmith** (open source)
- **Flipt** (open source feature flags)
- **GrowthBook** (open source A/B testing)

**Email & Communications**
- **Postal** (open source mail server)
- **Haraka** for SMTP
- **Mautic** for marketing automation
- **Listmonk** for newsletters
- **SendPortal** for email marketing

**Chat & Support**
- **Chatwoot** (open source customer support)
- **Rocket.Chat** for team communication
- **Papercups** for customer chat
- **Matrix/Synapse** for decentralized chat

**Payment Processing**
- **Kill Bill** (open source billing platform)
- **Medusa** (open source commerce engine)
- **BTCPay Server** for cryptocurrency
- Integration with **Stripe** using their free tier (pay per transaction)

**Analytics**
- **Plausible** or **Umami** for privacy-focused analytics
- **Matomo** (formerly Piwik) for comprehensive analytics
- **PostHog** (open source) for product analytics
- **Apache Superset** for business intelligence
- **Metabase** for data visualization
- **Cube.js** for analytics API layer

**CMS & Content**
- **Strapi** or **Directus** for headless CMS
- **Ghost** for content management
- **Payload CMS** for TypeScript-based CMS

## Additional Open Source Tools

**Workflow Orchestration**
- **Apache Airflow** for data pipelines
- **Temporal** for distributed workflows
- **n8n** for workflow automation
- **Apache NiFi** for data flow

**Business Intelligence**
- **Redash** for SQL queries and dashboards
- **Apache Superset** for data exploration
- **Metabase** for business analytics

**Rate Limiting & Throttling**
- **Redis** with Lua scripts
- **Bucket4j** for Java applications
- **express-rate-limit** for Node.js

**Documentation**
- **Docusaurus** for documentation sites
- **Swagger/OpenAPI** with **Redoc** or **Swagger UI**
- **MkDocs** with Material theme

## Cost-Free Cloud Options

For teams that prefer managed services with free tiers:

**Hosting**
- **Fly.io** (free tier with 3 shared VMs)
- **Railway** (free tier available)
- **Render** (free tier for web services)
- **Oracle Cloud** (generous always-free tier)

**Databases**
- **Supabase** (PostgreSQL, 500MB free)
- **PlanetScale** (MySQL-compatible, free tier)
- **Neon** (PostgreSQL, free tier)
- **MongoDB Atlas** (512MB free tier)

**Observability**
- **Grafana Cloud** (free tier with limits)
- **New Relic** (free tier with 100GB/month)
- **Honeycomb** (free tier available)
```

## Task and Implement

Use `/speckit.tasks` to create an actionable task list from your implementation plan.

```bash
/speckit.tasks
```

Validate alignment & surface inconsistencies (read-only)

```bash
/speckit.analyze
```

Use `/speckit.implement` to execute all tasks and build your feature according to the plan.

```bash
/speckit.implement
```
