# Implementation Plan: ScyllaDB to Postgres CDC Pipeline

**Branch**: `001-scylla-pg-cdc` | **Date**: 2025-12-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-scylla-pg-cdc/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a production-ready change data capture (CDC) pipeline that streams real-time change events from ScyllaDB to a Postgres data warehouse. The pipeline leverages Kafka Connect with Scylla CDC Source Connector and Postgres JDBC Sink Connector to achieve exactly-once semantics, automatic schema evolution, comprehensive observability (Prometheus, Grafana, Jaeger), and secure credential management via HashiCorp Vault. The system is fully testable locally via Docker Compose and managed through command-line scripts without requiring centralized APIs.

## Technical Context

**Language/Version**: Python 3.11+ (for custom glue code, reconciliation scripts), Bash/Shell (for operational scripts)
**Primary Dependencies**:
- Apache Kafka 3.6+ (message broker for change events)
- Kafka Connect 3.6+ (distributed connector framework)
- Confluent Hub Scylla CDC Source Connector (latest stable)
- Confluent Hub Postgres JDBC Sink Connector (latest stable)
- Kafka Schema Registry 7.5+ (Avro schema management)
- ScyllaDB 5.4+ (source database with CDC support)
- PostgreSQL 15+ (target data warehouse)
- HashiCorp Vault 1.15+ (secrets management)
- Prometheus 2.48+ (metrics collection)
- Grafana 10.2+ (visualization dashboards)
- Jaeger 1.51+ (distributed tracing)

**Storage**:
- Kafka topics (transient event storage, 24h retention minimum)
- PostgreSQL (target data warehouse + checkpoint metadata)
- Vault KV v2 (credentials storage)

**Testing**:
- pytest 7.4+ (Python unit/integration tests)
- Docker Compose 2.23+ (local test environment)
- testcontainers-python 3.7+ (integration test isolation)

**Target Platform**: Linux servers (Docker containerized), x86_64 architecture
**Project Type**: Single project (infrastructure/pipeline)
**Performance Goals**:
- 10,000+ events/second throughput
- <5 seconds p95 end-to-end latency
- <30 seconds recovery time from failures

**Constraints**:
- Exactly-once delivery semantics (no data loss/duplication)
- Zero-downtime schema evolution
- Minimum 4 CPU cores, 8GB RAM per environment
- Network: 100+ Mbps bandwidth, <10ms latency between components

**Scale/Scope**:
- Support 100+ ScyllaDB tables
- Handle 1TB+ daily change volume
- Operate 24/7 with 99.9% availability target

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Exactly-Once Semantics ✅

**Status**: PASS
**Implementation**: Kafka Connect with idempotent producers, Kafka transactions, and exactly-once semantics mode. Postgres JDBC Sink Connector with UPSERT operations based on primary keys. Checkpoint offsets stored in Kafka internal topics with atomic commits.

### Principle II: Schema Evolution & Backward Compatibility ✅

**Status**: PASS
**Implementation**: Kafka Schema Registry with Avro schemas enforcing compatibility rules. Connectors configured for schema auto-evolution. Schema changes validated before processing through registry compatibility checks.

### Principle III: Observable Pipelines ✅

**Status**: PASS
**Implementation**: Prometheus JMX exporters on Kafka Connect for metrics. Structured JSON logging with correlation IDs. Jaeger tracing integrated via OpenTelemetry. Grafana dashboards for lag, throughput, error rates. Health check endpoints on all components.

### Principle IV: Failure Isolation & Graceful Degradation ✅

**Status**: PASS
**Implementation**: Kafka Connect dead letter queues for poison messages. Connector-level circuit breakers with configurable retry policies (exponential backoff + jitter). Per-table connector instances for failure isolation. Kafka topic partitioning for bulkhead isolation.

### Principle V: Test-First Development ✅

**Status**: PASS
**Implementation**: Hybrid testing approach - unit tests for custom Python reconciliation code (TDD), integration tests for connector configurations after setup. Docker Compose enables local contract and chaos testing.

### Principle VI: Stateless Processing with Externalized State ✅

**Status**: PASS
**Implementation**: Kafka Connect framework inherently stateless with offsets externalized to Kafka internal topics. Connector worker nodes horizontally scalable. Reconciliation scripts stateless, reading state from Postgres checkpoint table.

### Principle VII: Performance Profiling & Capacity Planning ✅

**Status**: PASS
**Implementation**: Performance SLOs defined (<5s p95 latency, 10k events/sec). Prometheus metrics for continuous monitoring. Load testing framework using testcontainers. Capacity planning documented in quickstart.md with scaling guidelines.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
/
├── docker/
│   ├── docker-compose.yml           # Full local environment orchestration
│   ├── docker-compose.test.yml      # Test-specific overrides
│   ├── scylla/
│   │   └── init.cql                 # ScyllaDB schema initialization
│   ├── postgres/
│   │   └── init.sql                 # Postgres schema initialization
│   ├── kafka-connect/
│   │   ├── Dockerfile               # Custom Connect image with connectors
│   │   └── connectors/              # Connector configurations (JSON)
│   ├── vault/
│   │   ├── config.hcl               # Vault server configuration
│   │   └── init-secrets.sh          # Bootstrap script for dev secrets
│   ├── prometheus/
│   │   └── prometheus.yml           # Scrape configs for all services
│   └── grafana/
│       ├── datasources.yml          # Prometheus/Jaeger datasources
│       └── dashboards/              # Pre-built CDC monitoring dashboards
│
├── scripts/
│   ├── setup-local.sh               # Initialize local environment
│   ├── deploy-connector.sh          # Deploy/update connector instance
│   ├── reconcile.py                 # On-demand reconciliation script
│   ├── schedule-reconciliation.sh   # Cron wrapper for scheduled reconciliation
│   ├── health-check.sh              # Pipeline health verification
│   ├── backup-offsets.sh            # Checkpoint backup utility
│   └── chaos-test.sh                # Failure injection for testing
│
├── src/
│   ├── reconciliation/
│   │   ├── __init__.py
│   │   ├── comparer.py              # Source/sink data comparison logic
│   │   ├── differ.py                # Discrepancy detection algorithms
│   │   └── repairer.py              # Automated repair strategies
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── metrics.py               # Custom metric collectors
│   │   └── alerts.py                # Alert rule definitions
│   └── utils/
│       ├── __init__.py
│       ├── vault_client.py          # Vault credential retrieval
│       ├── schema_validator.py      # Schema compatibility checks
│       └── correlation.py           # Correlation ID injection/extraction
│
├── tests/
│   ├── unit/
│   │   ├── test_comparer.py
│   │   ├── test_differ.py
│   │   ├── test_vault_client.py
│   │   └── test_schema_validator.py
│   ├── integration/
│   │   ├── test_end_to_end.py       # Full pipeline flow tests
│   │   ├── test_schema_evolution.py # Schema change handling tests
│   │   ├── test_failure_recovery.py # Restart/recovery tests
│   │   └── fixtures/
│   │       ├── sample_data.sql      # Test data for ScyllaDB
│   │       └── expected_results.sql # Expected Postgres state
│   └── contract/
│       ├── test_scylla_connector.py # Source connector contract tests
│       └── test_postgres_sink.py    # Sink connector contract tests
│
├── configs/
│   ├── connectors/
│   │   ├── scylla-source.json       # Scylla CDC Source config template
│   │   └── postgres-sink.json       # Postgres Sink config template
│   ├── kafka/
│   │   └── server.properties        # Kafka broker configuration
│   └── connect/
│       └── connect-distributed.properties # Kafka Connect worker config
│
├── docs/
│   ├── architecture.md              # System architecture overview
│   ├── runbook.md                   # Operational procedures
│   ├── troubleshooting.md           # Common issues and solutions
│   └── scaling.md                   # Capacity planning guide
│
├── .env.example                     # Environment variable template
├── requirements.txt                 # Python dependencies
├── pytest.ini                       # Pytest configuration
└── README.md                        # Project overview and quickstart
```

**Structure Decision**: Single project infrastructure layout optimized for CDC pipelines. The structure separates:
- **docker/**: Complete containerized environment for local development and testing
- **scripts/**: CLI-driven operational commands (no centralized API)
- **src/**: Minimal custom Python code (reconciliation, monitoring utilities)
- **tests/**: Comprehensive test suite (unit, integration, contract)
- **configs/**: Declarative connector and infrastructure configurations
- **docs/**: Operational documentation and runbooks

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**Status**: No violations. All constitution principles satisfied.

The CDC pipeline architecture leverages proven open-source components (Kafka Connect, Scylla CDC Connector, Postgres JDBC Sink) which inherently satisfy the constitution requirements:

- **Exactly-once semantics**: Built into Kafka Connect framework
- **Schema evolution**: Handled by Schema Registry + connector auto-evolution
- **Observability**: JMX metrics, structured logging, distributed tracing
- **Failure isolation**: Dead letter queues, circuit breakers, per-table connectors
- **Test-first development**: Hybrid approach (TDD for custom code, integration tests for connectors)
- **Stateless processing**: Kafka Connect architecture with externalized offsets
- **Performance profiling**: SLOs defined, Prometheus metrics, load testing

No custom complexity introduced. Minimal custom code (reconciliation scripts only, ~10% of total codebase).
