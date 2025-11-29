# CDC Pipelines Checklist

## Design Patterns

- **Repository Pattern**: Abstract data access for MongoDB, Delta Lake, and reconciliation state storage
- **Strategy Pattern**: Support multiple CDC strategies (change streams, oplog tailing) and reconciliation modes
- **Factory Pattern**: Create appropriate handlers for different MongoDB BSON data types and Delta Lake conversions
- **Observer Pattern**: Event-driven pipeline stages with pub/sub messaging
- **Circuit Breaker**: Fault tolerance for external service calls
- **Retry with Exponential Backoff**: Resilient error handling
- **Bulkhead**: Isolate failures to prevent cascade effects

## Key Components

### I. MongoDB-CDC-Delta

1. Local Infrastructure & Orchestration (Docker; Prometheus; Grafana; Jaeger)
2. Management API (FastAPI)
3. Delta Lake Writer (Custom Python module)
4. Reconciliation Engine (Custom Python module)
5. Logging and Monitoring
6. Tests (pytest; testcontainers)

   - e2e
   - load/performance
   - contract
   - unit
   - integration

7. Configuration & Scripts (bash; JSON)
8. Documentation (markdown)

### II. Claude-CDC-Demo

1. cdc_pipelines (kafka connect wannabe custom modules)
2. cli (bespoke tool for pipelines management)
3. data_generators (Python Faker module)
4. validators (Python Data validation module for CDC pipelines)
5. Logging and Monitoring
6. Tests (pytest; testcontainers)

   - e2e
   - load/performance
   - contract
   - unit
   - integration

7. Configuration & Scripts (bash; python)
8. Documentation (markdown)
9. Docker (modular docker compose env with 10+ components)

## Keywords

- Performance Requirements
- Reliability Requirements
- Operational Requirements
- Structured Logging
- REDS Method
  - **Rate**: Requests/events per second (throughput)
  - **Errors**: Error rate by type and component
  - **Duration**: Latency percentiles (P50, P95, P99)
  - **Saturation**: Resource utilization (CPU, memory, disk, network)
  - Business Metrics: Records processed, lag time, backlog depth
  - Custom Metrics: Schema evolution events, type conversion failures
- Tracing
  - Distributed tracing for end-to-end request flows
    - Essential for debugging issues across 6+ components (MongoDB, Debezium, Kafka, Delta Lake writer, FastAPI, DuckDB) in event-driven architecture
  - Trace sampling
- Alerting
  - SLO-based alerts: Notify when SLIs approach SLO thresholds
  - Critical alerts: Data loss, system unavailability, cascading failures
  - Alert runbooks: Every alert includes diagnostic steps and remediation actions
- Optimization
  - Micro-batching: Accumulate events for 100ms or 1000 records (whichever first)
  - Adaptive batching: Adjust batch size based on throughput and latency metrics
  - Partitioned processing: Distribute work by MongoDB document _id or shard key via Kafka partitions
  - Thread pools: Separate pools for I/O (unbounded) and CPU (bounded) tasks
  - Async I/O: Non-blocking operations using async/await for MongoDB, MinIO, and Delta Lake writes
  - Schema cache: Cache MongoDB collection schemas and Delta Lake table schemas (TTL 5 minutes)
  - Connection pooling: Reuse MongoDB and MinIO connections (min 5, max 50 per pool)
- Schema evolution strategy
  - Delta Lake schema merging adds complexity but required for handling MongoDB's schemaless nature and avoiding pipeline failures. DuckDB extension help inheriting this Delta Lake's ability.
- Kafka Exactly-Once Semantics
- Debezium MongoDB Connector Configuration
- Reconciliation Algorithm Design
  - Merkle trees, sampling, hash-based comparison
- Jaeger sampling strategies (probabilistic, rate-limiting)
- Uvicorn with Gunicorn workers for production FastAPI deployment.
- Dynamic Secrets for MongoDB
