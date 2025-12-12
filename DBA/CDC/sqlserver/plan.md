# Implementation Plan: SQL Server to PostgreSQL CDC Pipeline

**Branch**: `001-sqlserver-pg-cdc` | **Date**: 2025-12-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-sqlserver-pg-cdc/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a production-grade Change Data Capture (CDC) pipeline that captures real-time changes (inserts, updates, deletes) from SQL Server and replicates them to PostgreSQL data warehouse. The pipeline uses Debezium SQL Server connector to capture CDC events, streams them through Kafka, and loads them into PostgreSQL via JDBC Sink connector. The system includes comprehensive observability (Prometheus, Grafana, Jaeger), secure credential management (HashiCorp Vault), automated reconciliation, schema evolution handling, and robust error recovery with dead letter queues. All components run in Docker Compose for local testing, with management via Bash/Python scripts (no centralized API).

## Technical Context

**Language/Version**: Python 3.11 for custom tooling (reconciliation, management scripts), Bash for operations
**Primary Dependencies**:
- Debezium 2.5+ (SQL Server CDC Source Connector from Confluent Hub)
- Kafka Connect 3.6+ with PostgreSQL JDBC Sink Connector (Confluent Hub)
- Apache Kafka 3.6+, Confluent Schema Registry 7.5+
- HashiCorp Vault 1.15+ for secrets management
- Prometheus 2.48+, Grafana 10.2+, Jaeger 1.51+ for observability

**Storage**:
- Source: SQL Server 2019+ (with CDC enabled)
- Target: PostgreSQL 15+
- Kafka topics for change event streams
- Vault for credential storage

**Testing**:
- pytest for Python reconciliation tool and scripts
- Testcontainers for integration tests
- Contract tests for Debezium source and JDBC sink configurations
- End-to-end tests simulating full replication lifecycle

**Target Platform**: Linux containers (Docker Compose locally, Kubernetes-ready for production)

**Project Type**: Infrastructure/data pipeline - single project structure with tooling separated by concern

**Performance Goals**:
- Throughput: 10,000 rows/sec sustained
- Replication lag: <5 minutes (p95)
- Reconciliation scan: 1M rows in <10 minutes
- Resource usage: 4GB RAM, 2 CPU cores per connector instance

**Constraints**:
- Must use open-source components only
- Minimal custom code (prefer configuration over code)
- Docker Compose-based local environment
- Script-based management (no web UI or management API)
- All credentials via Vault (no plaintext secrets)

**Scale/Scope**:
- Initial: 10-50 tables, 100K-1M rows per table
- Supports horizontal scaling by topic partitioning
- Designed for OLTP-to-OLAP workload patterns

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Test-Driven Development (NON-NEGOTIABLE)
- ✅ **PASS**: All custom code (reconciliation tool, management scripts) will follow TDD
- ✅ **PASS**: Contract tests for connector configurations
- ✅ **PASS**: Integration tests for end-to-end replication flows
- ✅ **PASS**: Configuration validation tests before deployment

**Testing Strategy**:
- Contract tests: Validate Debezium source schema, JDBC sink schema compatibility
- Integration tests: Testcontainers spin up SQL Server, Kafka, PostgreSQL, verify replication
- Unit tests: Python reconciliation tool (row count comparison, checksum validation)
- E2E tests: Full pipeline with schema evolution, failure scenarios, reconciliation

### II. Data Integrity First
- ✅ **PASS**: Debezium captures all CDC events with LSN tracking (idempotency)
- ✅ **PASS**: Kafka provides durable, ordered event log
- ✅ **PASS**: JDBC sink uses upsert mode for idempotent writes
- ✅ **PASS**: Reconciliation tool validates row counts and checksums
- ✅ **PASS**: Dead letter queue for failed transformations
- ✅ **PASS**: Checkpoint tracking via Kafka Connect offsets

**Data Integrity Mechanisms**:
- Source validation: Debezium verifies SQL Server CDC table structure
- Transform validation: Schema Registry enforces Avro schema contracts
- Sink validation: PostgreSQL constraints and unique indexes
- Audit trail: All events logged with LSN, timestamp, transaction ID

### III. Clean, Maintainable Code
- ✅ **PASS**: Minimal custom code - 90% configuration, 10% tooling
- ✅ **PASS**: Python scripts follow PEP 8, max function length 50 lines
- ✅ **PASS**: Bash scripts follow Google Shell Style Guide
- ✅ **PASS**: All scripts documented with usage examples in quickstart.md
- ✅ **PASS**: Configuration as code (YAML/JSON) with validation schemas

**Code Organization**:
- Reconciliation tool: Single-purpose module (<500 lines)
- Management scripts: Atomic operations (deploy, scale, reconcile, monitor)
- Configuration: Declarative connector configs with comments

### IV. Robust Error Handling & Observability
- ✅ **PASS**: Structured JSON logging from all components
- ✅ **PASS**: Prometheus metrics: lag, throughput, error rate, resource usage
- ✅ **PASS**: Grafana dashboards for real-time monitoring
- ✅ **PASS**: Jaeger distributed tracing for event lineage
- ✅ **PASS**: Alerting rules for lag, errors, downtime
- ✅ **PASS**: Dead letter queue with error context

**Observability Stack**:
- Logs: All components → stdout → Docker logs → searchable
- Metrics: Kafka Connect JMX → Prometheus → Grafana
- Traces: Jaeger agent captures Kafka Connect spans
- Alerts: Prometheus Alertmanager → webhook/email

### V. Modular Architecture with Clear Boundaries
- ✅ **PASS**: Clear separation of concerns:
  - **Extractor**: Debezium SQL Server connector (CDC capture)
  - **Message Broker**: Kafka (durable event log)
  - **Transformer**: Kafka Connect SMTs (type conversions, filtering)
  - **Loader**: JDBC Sink connector (PostgreSQL writes)
  - **Coordinator**: Kafka Connect distributed workers
  - **Monitor**: Prometheus + Grafana + Jaeger
  - **Reconciler**: Python CLI tool (on-demand or scheduled)

**Module Interfaces**:
- Debezium → Kafka topics (Avro schema via Schema Registry)
- Kafka → JDBC Sink (Avro to SQL type mapping)
- Reconciler → REST APIs (SQL Server ODBC, PostgreSQL psycopg2)
- Management scripts → Kafka Connect REST API (CRUD connectors)

### Gate Evaluation: ✅ ALL GATES PASSED

No constitutional violations detected. The architecture leverages proven open-source components with minimal custom code, follows TDD for all custom tooling, and provides comprehensive data integrity guarantees through Debezium CDC, Kafka durability, and reconciliation tooling.

## Project Structure

### Documentation (this feature)

```text
specs/001-sqlserver-pg-cdc/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── debezium-sqlserver-source.json
│   ├── jdbc-postgresql-sink.json
│   └── kafka-topics.yaml
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Infrastructure and tooling project structure
docker/
├── docker-compose.yml           # Full stack: SQL Server, Kafka, PostgreSQL, monitoring, Vault
├── docker-compose.test.yml      # Test environment with Testcontainers overrides
├── configs/
│   ├── debezium/
│   │   └── sqlserver-source.json
│   ├── kafka-connect/
│   │   └── postgresql-sink.json
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alert-rules.yml
│   ├── grafana/
│   │   └── dashboards/
│   │       ├── cdc-pipeline.json
│   │       └── kafka-connect.json
│   ├── vault/
│   │   ├── policies/
│   │   └── config.hcl
│   └── jaeger/
│       └── jaeger-config.yml

scripts/
├── bash/
│   ├── deploy-connector.sh      # Deploy Debezium/JDBC connectors
│   ├── scale-connector.sh       # Scale connector tasks
│   ├── pause-resume.sh          # Pause/resume replication
│   ├── monitor.sh               # Query metrics and health
│   └── vault-init.sh            # Initialize Vault with DB credentials
└── python/
    ├── reconcile.py             # Reconciliation CLI tool
    ├── setup.py
    └── tests/
        ├── test_reconcile.py
        └── test_integration.py

src/
├── reconciliation/
│   ├── __init__.py
│   ├── compare.py               # Row count and checksum comparison
│   ├── report.py                # Generate reconciliation reports
│   └── scheduler.py             # Cron-like scheduler for automated reconciliation
└── utils/
    ├── vault_client.py          # Vault integration for fetching credentials
    └── metrics.py               # Custom metrics publishing

tests/
├── contract/
│   ├── test_debezium_schema.py
│   └── test_jdbc_sink_schema.py
├── integration/
│   ├── test_replication_flow.py
│   ├── test_schema_evolution.py
│   └── test_error_recovery.py
└── e2e/
    ├── test_full_pipeline.py
    └── test_reconciliation.py

docs/
├── architecture.md              # System architecture diagrams
├── operations.md                # Runbook for common operations
└── troubleshooting.md           # Common issues and resolutions
```

**Structure Decision**:

This is an infrastructure/data pipeline project, not a traditional application. The structure prioritizes:

1. **docker/**: All deployment artifacts in one place (Docker Compose, connector configs, monitoring configs)
2. **scripts/**: Operational tooling separated by language (Bash for Docker/Kafka ops, Python for data reconciliation)
3. **src/**: Minimal custom code limited to reconciliation logic and utilities
4. **tests/**: Comprehensive test suite following constitution requirements (contract, integration, e2e)
5. **docs/**: Operational documentation (no API docs since there's no management API)

This structure supports the requirement for script-based management (no centralized API) while maintaining clear separation between infrastructure (docker/), operations (scripts/), and custom logic (src/).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected - this section intentionally left empty as all constitutional gates passed.
