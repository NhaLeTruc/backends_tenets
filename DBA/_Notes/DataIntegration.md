# Data Integration Tools and Techniques

## Table of Contents

- [Data Integration Tools and Techniques](#data-integration-tools-and-techniques)
  - [Table of Contents](#table-of-contents)
  - [1. Data Integration (Batch)](#1-data-integration-batch)
    - [1.1 Messaging & Kafka](#11-messaging--kafka)
      - [Kafka vs RabbitMQ](#kafka-vs-rabbitmq)
      - [Kafka Rate Limiting](#kafka-rate-limiting)
      - [Kafka Throttling](#kafka-throttling)
      - [Kafka Backpressure](#kafka-backpressure)
    - [1.2 Change Data Capture (CDC)](#12-change-data-capture-cdc)
      - [Acceptable CDC and CRUD Operations Latency in Production](#acceptable-cdc-and-crud-operations-latency-in-production)
      - [Versioned Tables in Handling Late Data](#versioned-tables-in-handling-late-data)
      - [Merge Large Data in Batch Not Per Record](#merge-large-data-in-batch-not-per-record)
      - [Guarantees Idempotent Write by DELETE before INSERT](#guarantees-idempotent-write-by-delete-before-insert)
    - [1.3 Incremental Processing](#13-incremental-processing)
      - [Incremental Processing: Process Only New Data Not Reprocessing All History](#incremental-processing-process-only-new-data-not-reprocessing-all-history)
      - [Incremental Backfilling](#incremental-backfilling)
  - [2. Streaming & Real-Time Processing](#2-streaming--real-time-processing)
    - [2.1 Stream Processing Patterns](#21-stream-processing-patterns)
      - [Kafka Streaming Watermark](#kafka-streaming-watermark)
      - [Sessionization Algorithm](#sessionization-algorithm)
      - [Testing Spark Streaming Pipelines](#testing-spark-streaming-pipelines)
      - [Testing Kafka Streaming Pipelines](#testing-kafka-streaming-pipelines)
      - [Testcontainers vs Docker Compose](#testcontainers-vs-docker-compose)
    - [2.2 Real-Time Communication](#22-real-time-communication)
      - [Web Sockets](#web-sockets)
      - [Web Hooks](#web-hooks)
      - [Server-Sent Events (SSE)](#server-sent-events-sse)
      - [Long Polling](#long-polling)
      - [Message Queue](#message-queue)

## 1. Data Integration (Batch)

### 1.1 Messaging & Kafka

#### Kafka vs RabbitMQ

**Definition**: Comparison of message brokers - Kafka excels at high-throughput, replay, partitioned topics; RabbitMQ provides routing, priority queues, multiple protocols.

**SWOT Analysis - Apache Kafka**:

| Strengths | Weaknesses |
|-----------|------------|
| Extremely high throughput (millions of msgs/sec) | More complex to set up and operate |
| Built-in message retention and replay capability | No built-in priority queues |
| Horizontal scaling via partitions | Consumer group rebalancing can cause delays |
| Strong ordering guarantees within partitions | Heavier resource footprint (disk, memory) |
| Excellent for event sourcing and stream processing | Overkill for simple task queues |

| Opportunities | Threats |
|---------------|---------|
| Growing adoption of event-driven architectures | Managed alternatives (Kinesis, Pub/Sub) reduce operational appeal |
| Kafka Streams and ksqlDB expand use cases | Pulsar gaining traction as modern alternative |
| Cloud-native offerings (Confluent, MSK) simplify ops | Complexity may push teams to simpler solutions |
| Central nervous system for data mesh architectures | Learning curve limits adoption in smaller teams |

**SWOT Analysis - RabbitMQ**:

| Strengths | Weaknesses |
|-----------|------------|
| Flexible routing (direct, topic, fanout, headers) | Lower throughput than Kafka at scale |
| Priority queues and TTL support | No built-in message replay (consumed = gone) |
| Multiple protocols (AMQP, MQTT, STOMP) | Scaling requires clustering complexity |
| Simpler operational model for basic use cases | Not ideal for event sourcing patterns |
| Mature ecosystem with excellent documentation | Can struggle under very high message rates |

| Opportunities | Threats |
|---------------|---------|
| Strong fit for microservices task distribution | Kafka dominance in streaming/event space |
| IoT and MQTT protocol support growing | Cloud-native message queues (SQS) simpler to operate |
| Quorum queues improve durability story | Perceived as "legacy" compared to newer options |
| Plugin ecosystem enables customization | Teams often default to Kafka without evaluating fit |

**Comparison Table**:

| Aspect | Kafka | RabbitMQ | Winner |
|--------|-------|----------|--------|
| **Throughput** | Millions of msgs/sec | Tens of thousands of msgs/sec | Kafka |
| **Latency** | Low (batched), sub-10ms typical | Very low, sub-1ms possible | RabbitMQ |
| **Message Retention** | Configurable (hours to forever) | Until consumed (or TTL) | Kafka |
| **Replay Capability** | Native (offset-based) | Not supported | Kafka |
| **Ordering Guarantees** | Per-partition ordering | Per-queue ordering | Tie |
| **Priority Queues** | Not supported | Native support | RabbitMQ |
| **Routing Flexibility** | Topic-based only | Exchange types (direct, topic, fanout, headers) | RabbitMQ |
| **Protocol Support** | Kafka protocol only | AMQP, MQTT, STOMP, HTTP | RabbitMQ |
| **Scaling Model** | Partition-based (horizontal) | Clustering + federation | Kafka |
| **Operational Complexity** | Higher (ZK/KRaft, partitions, replication) | Moderate (clustering, policies) | RabbitMQ |
| **Stream Processing** | Native (Kafka Streams, ksqlDB) | Requires external tools | Kafka |
| **Dead Letter Handling** | Manual implementation | Native DLX support | RabbitMQ |
| **Consumer Groups** | Native, with rebalancing | Competing consumers pattern | Kafka |
| **Exactly-Once Semantics** | Supported (with transactions) | At-most-once or at-least-once | Kafka |
| **Cloud Managed Options** | Confluent, MSK, Aiven | CloudAMQP, AmazonMQ | Tie |

**Recommendation by Use Case**:

| Use Case | Recommended | Rationale |
|----------|-------------|-----------|
| High-throughput event streaming | Kafka | Designed for massive scale, partitioned logs |
| Event sourcing / audit logs | Kafka | Immutable log with replay capability |
| Real-time analytics pipelines | Kafka | Stream processing integrations (Flink, Spark) |
| Simple task queue / work distribution | RabbitMQ | Lightweight, priority support, easy setup |
| Request-reply patterns | RabbitMQ | Built-in RPC support, flexible routing |
| IoT message ingestion | RabbitMQ | MQTT protocol support |
| Microservices async communication | Either | Depends on scale and replay requirements |
| Log aggregation | Kafka | High throughput, retention, multiple consumers |
| Order processing with priorities | RabbitMQ | Native priority queue support |
| CDC / database replication | Kafka | Debezium integration, log compaction |

**External Resources**:

- https://www.rabbitmq.com/
- https://kafka.apache.org/
- https://aws.amazon.com/blogs/architecture/comparing-messaging-brokers-rabbitmq-and-kafka/

#### Kafka Rate Limiting

**Definition**: Techniques to control producer/consumer throughput (throttling, backpressure, quota enforcement) preventing overwhelming downstream systems.

**External Resources**:

- https://docs.confluent.io/kafka/design/quotas.html
- https://kafka.apache.org/documentation/#brokerconfigs_quota.producer.default
- https://medium.com/@danielchen.dc/kafka-quota-and-rate-limiting-9a35b23c2f1b

#### Kafka Throttling

**Definition**: Broker-enforced mechanism that delays client requests when they exceed configured quotas, ensuring fair resource allocation and protecting cluster stability.

**How Kafka Throttling Works**:

Throttling is Kafka's built-in enforcement mechanism for quotas:

1. Broker tracks byte rates and request rates per client/user
2. When a client exceeds quota, broker calculates delay time
3. Client receives throttle time in response, must wait before next request
4. Throttling is transparent—client SDKs handle delays automatically

**Guidelines and Best Practices**:

1. **Understanding Quota Types**

   | Quota Type | Scope | Configuration | Use Case |
   |------------|-------|---------------|----------|
   | `producer_byte_rate` | Bytes/sec produced | Per client-id, user, or both | Control ingestion rate |
   | `consumer_byte_rate` | Bytes/sec consumed | Per client-id, user, or both | Control fetch rate |
   | `request_percentage` | % of broker I/O threads | Per client-id, user, or both | Limit request processing time |
   | `controller_mutation_rate` | Mutations/sec | Per broker | Limit metadata changes |

2. **Setting Up Client Quotas**

   ```bash
   # Set quota for specific client-id
   kafka-configs.sh --bootstrap-server localhost:9092 \
     --alter --add-config 'producer_byte_rate=10485760,consumer_byte_rate=20971520' \
     --entity-type clients --entity-name my-app

   # Set quota for specific user
   kafka-configs.sh --bootstrap-server localhost:9092 \
     --alter --add-config 'producer_byte_rate=5242880' \
     --entity-type users --entity-name alice

   # Set quota for user + client-id combination
   kafka-configs.sh --bootstrap-server localhost:9092 \
     --alter --add-config 'producer_byte_rate=5242880' \
     --entity-type users --entity-name alice \
     --entity-type clients --entity-name my-app
   ```

3. **Default Quotas Configuration**

   ```properties
   # In server.properties - default quotas for all clients
   quota.producer.default=10485760        # 10 MB/s per producer
   quota.consumer.default=20971520        # 20 MB/s per consumer

   # Request percentage quota (limits CPU time)
   quota.window.num=11                    # Number of samples retained
   quota.window.size.seconds=1            # Each sample window duration
   ```

4. **Monitoring Throttling Metrics**

   Key JMX metrics to monitor:

   | Metric | Description | Alert Threshold |
   |--------|-------------|-----------------|
   | `kafka.server:type=FetchThrottleTimeMs` | Consumer throttle delay | > 100ms avg |
   | `kafka.server:type=ProduceThrottleTimeMs` | Producer throttle delay | > 100ms avg |
   | `kafka.server:type=RequestThrottleTimeMs` | Request quota throttle | > 50ms avg |
   | `kafka.network:type=ThrottledRequests` | Count of throttled requests | Increasing trend |

5. **Client-Side Throttle Handling**

   ```python
   from kafka import KafkaProducer
   from kafka.errors import KafkaError

   producer = KafkaProducer(
       bootstrap_servers=['localhost:9092'],
       client_id='my-throttled-producer',
       # These settings help handle throttling gracefully
       max_block_ms=120000,          # Wait up to 2 min if throttled
       request_timeout_ms=60000,     # Timeout for individual requests
       retries=5,                    # Retry on transient errors
       retry_backoff_ms=500,         # Backoff between retries
   )

   # Check for throttling in producer metrics
   metrics = producer.metrics()
   throttle_time = metrics.get('producer-metrics', {}).get('produce-throttle-time-avg', 0)
   if throttle_time > 100:
       print(f"Warning: Producer being throttled, avg delay: {throttle_time}ms")
   ```

6. **Quota Hierarchy and Precedence**

   ```
   Most Specific (highest priority)
   ├── user="alice" + client-id="my-app"    → Specific user + client
   ├── user="alice" + client-id=<default>   → User with any client
   ├── user=<default> + client-id="my-app"  → Any user with specific client
   ├── user="alice"                         → Specific user only
   ├── client-id="my-app"                   → Specific client only
   └── <default>                            → Broker-wide default
   Least Specific (lowest priority)
   ```

7. **Sizing Quotas Appropriately**

   | Cluster Size | Producer Quota (per client) | Consumer Quota (per client) | Rationale |
   |--------------|-----------------------------|-----------------------------|-----------|
   | Small (3 brokers) | 5-10 MB/s | 10-20 MB/s | Protect limited resources |
   | Medium (6-12 brokers) | 20-50 MB/s | 50-100 MB/s | Balance sharing |
   | Large (20+ brokers) | 50-100 MB/s | 100-200 MB/s | Higher capacity per client |

   Formula: `per_client_quota = (total_cluster_bandwidth * 0.7) / expected_concurrent_clients`

8. **Throttling vs Rate Limiting Comparison**

   | Aspect | Kafka Throttling (Broker) | Application Rate Limiting |
   |--------|---------------------------|---------------------------|
   | Enforcement | Broker-side, automatic | Client-side, manual |
   | Granularity | Per client-id/user | Custom (per API, per tenant) |
   | Visibility | JMX metrics, logs | Application metrics |
   | Flexibility | Fixed quota types | Fully customizable |
   | Overhead | Minimal (built-in) | Additional code/dependencies |
   | Failure Mode | Client waits | Depends on implementation |

9. **Common Throttling Scenarios**

   | Scenario | Symptom | Solution |
   |----------|---------|----------|
   | Single client overwhelming cluster | High throttle time for one client | Set client-specific quota |
   | Burst traffic during peak hours | Periodic throttling across clients | Increase quotas or add capacity |
   | Noisy neighbor in multi-tenant | Other clients throttled unfairly | Implement per-tenant quotas |
   | Reprocessing/backfill job | Consumer throttled during catch-up | Temporary quota increase or separate client-id |
   | New client without quota | Unbounded resource usage | Set default quotas in server.properties |

10. **Best Practices Summary**

    - Always set default quotas (`quota.producer.default`, `quota.consumer.default`)
    - Use client-id naming conventions for easy quota management (e.g., `team-service-env`)
    - Monitor throttle time metrics and alert on sustained throttling
    - Size quotas based on cluster capacity and expected client count
    - Document quota policies and communicate to client teams
    - Use separate client-ids for batch jobs vs real-time workloads
    - Test quota changes in non-production first
    - Consider request_percentage quota for CPU-intensive clients

**External Resources**:

- https://kafka.apache.org/documentation/#design_quotas
- https://docs.confluent.io/kafka/design/quotas.html
- https://www.conduktor.io/kafka/kafka-quotas/

#### Kafka Backpressure

**Definition**: Mechanism where slow consumers signal producers to slow down message production, preventing buffer overflow and maintaining system stability.

**Understanding Kafka's Backpressure Model**:

Unlike traditional message queues, Kafka doesn't have built-in backpressure signaling from consumers to producers. Instead, backpressure is managed through:

- Consumer lag accumulation (messages queue in brokers)
- Producer blocking when broker buffers are full
- Quota-based throttling at the broker level

**Guidelines and Best Practices**:

1. **Monitor Consumer Lag as Primary Indicator**
   - Consumer lag = difference between latest offset and consumer's committed offset
   - Set up alerts when lag exceeds acceptable thresholds
   - Tools: Kafka Consumer Group CLI, Burrow, Kafka Lag Exporter (Prometheus)

   ```bash
   # Check consumer lag
   kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
     --group my-consumer-group --describe
   ```

2. **Producer-Side Backpressure Configuration**

   ```python
   # Producer configs for backpressure handling
   producer_config = {
       'buffer.memory': 33554432,          # 32MB buffer (blocks when full)
       'max.block.ms': 60000,              # Max time to block when buffer full
       'linger.ms': 5,                     # Batch wait time
       'batch.size': 16384,                # Batch size in bytes
       'acks': 'all',                      # Wait for all replicas
       'retries': 3,                       # Retry on transient failures
       'retry.backoff.ms': 100,            # Backoff between retries
   }
   ```

3. **Consumer-Side Backpressure Handling**

   ```python
   # Consumer configs for controlled consumption
   consumer_config = {
       'max.poll.records': 500,            # Limit records per poll
       'max.poll.interval.ms': 300000,     # Max processing time before rebalance
       'fetch.min.bytes': 1,               # Min data to fetch
       'fetch.max.bytes': 52428800,        # Max data per fetch (50MB)
       'fetch.max.wait.ms': 500,           # Max wait for fetch.min.bytes
   }
   ```

4. **Broker-Level Quota Enforcement**

   ```bash
   # Set producer quota (bytes/sec per client)
   kafka-configs.sh --bootstrap-server localhost:9092 \
     --alter --add-config 'producer_byte_rate=1048576' \
     --entity-type clients --entity-name my-producer

   # Set consumer quota
   kafka-configs.sh --bootstrap-server localhost:9092 \
     --alter --add-config 'consumer_byte_rate=2097152' \
     --entity-type clients --entity-name my-consumer
   ```

5. **Partition-Based Flow Control**
   - Increase partitions to parallelize consumption
   - Match consumer instances to partition count
   - Avoid over-partitioning (metadata overhead, rebalancing cost)
   - Formula: `partitions >= max_expected_consumer_instances`

6. **Pause/Resume Pattern for Consumer-Side Control**

   ```python
   # Pause partitions when downstream is slow
   from kafka import KafkaConsumer, TopicPartition

   consumer = KafkaConsumer('my-topic', group_id='my-group')

   # Pause when backpressure detected
   if downstream_buffer_full():
       partitions = consumer.assignment()
       consumer.pause(*partitions)

   # Resume when ready
   if downstream_ready():
       consumer.resume(*consumer.paused())
   ```

7. **Dead Letter Queue (DLQ) for Failed Messages**
   - Route unprocessable messages to DLQ instead of blocking
   - Prevents poison messages from stalling consumers
   - Implement retry logic with exponential backoff before DLQ

8. **Reactive Streams Integration**
   - Use reactive Kafka libraries for automatic backpressure
   - Reactor Kafka (Java), Alpakka Kafka (Scala), aiokafka (Python async)
   - Demand-based pulling prevents consumer overwhelm

**Backpressure Detection Metrics**:

| Metric | Healthy Range | Warning Threshold | Critical Threshold |
|--------|---------------|-------------------|-------------------|
| Consumer Lag (records) | < 1,000 | > 10,000 | > 100,000 |
| Consumer Lag (time) | < 1 min | > 5 min | > 30 min |
| Producer Queue Time | < 10ms | > 100ms | > 1s |
| Broker Request Queue | < 100 | > 500 | > 1,000 |
| Fetch Throttle Time | 0ms | > 50ms | > 500ms |

**Common Backpressure Scenarios and Solutions**:

| Scenario | Symptom | Solution |
|----------|---------|----------|
| Slow consumer processing | Growing lag, constant throughput | Scale consumers, optimize processing, async processing |
| Downstream system slow | Consumer pause, DLQ growth | Implement circuit breaker, batch writes, buffer locally |
| Producer burst traffic | Producer blocks, timeout errors | Increase buffer.memory, add rate limiting upstream |
| Network congestion | High fetch/produce latency | Tune batch.size, linger.ms; check network capacity |
| Broker disk I/O bottleneck | High request queue, throttling | Add brokers, faster disks, adjust retention |
| Rebalancing storms | Frequent partition reassignment | Increase session.timeout.ms, use static membership |

**Architecture Patterns for Backpressure**:

1. **Buffering Layer**: Add Redis/Kafka Streams state store between Kafka and slow sinks
2. **Circuit Breaker**: Stop consuming when downstream failure rate exceeds threshold
3. **Rate Limiting Gateway**: Control producer ingest rate at API gateway level
4. **Spillover Topic**: Route excess traffic to secondary topic during spikes
5. **Priority Queues**: Use separate topics for different priority levels

**External Resources**:

- https://kafka.apache.org/documentation/
- https://medium.com/@danielchen.dc/kafka-quota-and-rate-limiting-9a35b23c2f1b
- https://www.confluent.io/blog/kafka-without-zookeeper/

### 1.2 Change Data Capture (CDC)

#### Acceptable CDC and CRUD Operations Latency in Production

**Definition**: Performance benchmarks for acceptable latency in change capture and database operations - typically milliseconds to seconds depending on use case (analytical vs operational).

**Production Latency Benchmarks by Operation Type**:

| Operation Type | Use Case | Acceptable Latency (ms) | Target Latency (ms) | Notes |
|---|---|---|---|---|
| **READ Operations** | | | | |
| Point Lookup (by PK) | Operational | 1-10 | 5 | Sub-10ms critical for user-facing features |
| Index Scan | Operational | 5-50 | 20 | Filtered queries with good index coverage |
| Full Table Scan | Analytical | 500-5000 | 2000 | Large datasets, acceptable for batch jobs |
| Aggregation Query | Analytical | 1000-10000 | 5000 | GroupBy, SUM, COUNT on millions of rows |
| Join Query (2-3 tables) | Operational | 50-500 | 200 | Typical business queries |
| Join Query (5+ tables) | Analytical | 500-5000 | 2000 | Complex analytical queries |
| **WRITE Operations** | | | | |
| Single INSERT | Transactional | 1-5 | 3 | Simple row insert |
| Batch INSERT (100-1K rows) | Transactional | 10-50 | 25 | Typically used in applications |
| Batch INSERT (10K-100K rows) | ETL | 100-1000 | 500 | Bulk data loading |
| UPDATE (single row) | Transactional | 2-10 | 5 | Update by primary key |
| UPDATE (bulk, 1K+ rows) | ETL | 50-500 | 200 | Batch updates with WHERE clause |
| DELETE (single row) | Transactional | 2-10 | 5 | Delete by primary key |
| DELETE (bulk, 1K+ rows) | ETL | 50-500 | 200 | Batch deletes with WHERE clause |
| MERGE/UPSERT | ETL | 50-200 | 100 | Delta Lake MERGE or Postgres UPSERT |
| **CDC (Change Data Capture)** | | | | |
| CDC Event Latency (Log-based) | Real-time | 100-1000 | 500 | Debezium, AWS DMS, logical replication |
| CDC Event Latency (Query-based) | Near Real-time | 1000-10000 | 5000 | Polling-based CDC (less frequent) |
| CDC Batch Latency | Analytical | 10000-300000 | 60000 | Daily/hourly batch CDC jobs |
| CDC End-to-End (capture → Kafka) | Real-time | 200-2000 | 1000 | Full pipeline including message pub |
| CDC End-to-End (capture → warehouse) | Real-time | 500-5000 | 2000 | Including downstream processing |
| **Transaction Operations** | | | | |
| ACID Transaction (simple) | Operational | 5-50 | 20 | Single table transaction |
| ACID Transaction (multi-table) | Operational | 20-200 | 100 | Cross-table consistency |
| Two-Phase Commit (2PC) | Distributed | 100-1000 | 500 | Distributed transaction across DBs |
| Lock Acquisition | Concurrent | 1-20 | 10 | Row-level or page-level locks |
| **Replication/HA Operations** | | | | |
| Primary → Replica Lag | Synchronous | 10-100 | 50 | Synchronous replication (PostgreSQL Patroni) |
| Primary → Replica Lag | Asynchronous | 100-5000 | 1000 | Asynchronous replication (HA standby) |
| Failover Cutover Time | High Availability | 1000-30000 | 5000 | Time to promote replica to primary |
| Streaming Replication Lag | Real-time | 100-1000 | 500 | Kafka/Flink-based replication |

**Latency Guidelines by Environment**:

| Environment | User-Facing Queries | Operational Writes | Batch/ETL | CDC Ingestion |
|---|---|---|---|---|
| **Interactive (Web/API)** | <100ms | <50ms | N/A | N/A |
| **Operational (SaaS/E-commerce)** | 100-500ms | 50-200ms | <5s | 500ms-2s |
| **Analytical (Data Warehouse)** | 1-10s | 100-1000ms | 1-60s | 1-60s |
| **Real-time (Streaming)** | N/A | <50ms | N/A | 100-500ms |
| **Batch (Data Lake)** | 10-60s | 1-10s | 5-300s | 10-300s |

**Performance Targets by Percentile**:

| Latency Metric | Target | Acceptable | Warning | Critical |
|---|---|---|---|---|
| **p50 (Median)** | baseline | baseline × 1.5 | baseline × 3 | baseline × 5+ |
| **p95 (95th percentile)** | baseline × 2 | baseline × 3 | baseline × 5 | baseline × 10+ |
| **p99 (99th percentile)** | baseline × 3 | baseline × 5 | baseline × 10 | baseline × 20+ |
| **p99.9 (99.9th percentile)** | baseline × 5 | baseline × 10 | baseline × 20 | baseline × 50+ |

**Key Considerations**:

- **Baseline Establishment**: Measure p50 latency under normal production load for each operation type and use as baseline
- **Seasonal Peaks**: Account for 2-3x latency increase during peak traffic periods (shopping events, month-end close)
- **Data Volume Scaling**: Latency increases logarithmically with data volume; revisit targets when data grows 10x+
- **Network Latency**: Add 5-50ms for cross-region/cross-AZ operations; critical for distributed systems
- **Retry Logic Impact**: Exponential backoff can cause observable latency of 100ms-10s; factor into SLOs
- **Database Tuning**: Proper indexing can reduce latency 10-100x; regularly analyze slow query logs
- **Infrastructure Limits**: Cloud providers often guarantee 99.9% uptime (43 minutes/month downtime); design accordingly

**External Resources**:

- https://aws.amazon.com/dms/
- https://docs.oracle.com/en/database/oracle/oracle-database/19/adfns/
- https://debezium.io/

#### Versioned Tables in Handling Late Data

**Definition**: Table versioning strategy where updates and inserts are tracked with version numbers, enabling historical queries and handling of out-of-order data arrivals.

**External Resources**:

- https://docs.databricks.com/en/delta/versioning.html
- https://delta.io/blog/2023-02-01-delta-lake-time-travel/
- https://iceberg.apache.org/docs/latest/

#### Merge Large Data in Batch Not Per Record

**Definition**: Performance best practice for MERGE operations - batching updates together rather than processing individually to reduce overhead and improve throughput.

**External Resources**:

- https://docs.databricks.com/en/delta/merge.html
- https://delta.io/blog/2020-12-11-getting-started-with-merges/
- https://spark.apache.org/docs/latest/sql-ref-syntax-dml-merge-into.html

#### Guarantees Idempotent Write by DELETE before INSERT

**Definition**: Data quality pattern ensuring exactly-once semantics by removing existing records before inserting, preventing duplicates in case of retries.

**External Resources**:
- https://databricks.com/blog/2020/03/06/introducing-delta-lake-on-databricks.html
- https://delta.io/blog/2021-09-01-delta-lake-compaction/
- https://en.wikipedia.org/wiki/Idempotence

### 1.3 Incremental Processing

#### Incremental Processing: Process Only New Data Not Reprocessing All History

**Definition**: ETL pattern processing only newly arrived data since last run, avoiding expensive re-computation of historical data and improving performance.

**External Resources**:

- https://databricks.com/blog/2020/03/06/introducing-delta-lake-on-databricks.html
- https://www.getdbt.com/blog/what-is-incremental-models/
- https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html

#### Incremental Backfilling

**Definition**: Strategy for retroactively computing historical data in stages rather than all at once, managing resource consumption and reducing risk.

**When to Use Incremental Backfilling**:

- Historical data reprocessing after schema changes or bug fixes
- Populating new derived tables/aggregations from existing data
- Migrating data between systems with minimal downtime
- Recovering from data quality issues in specific time ranges
- Adding new columns that require historical computation

**Guidelines and Best Practices**:

1. **Chunk by Time Windows**

   Break backfills into manageable time-based chunks:

   ```python
   from datetime import datetime, timedelta

   def backfill_by_date_range(start_date, end_date, chunk_days=7):
       current = start_date
       while current < end_date:
           chunk_end = min(current + timedelta(days=chunk_days), end_date)
           process_date_range(current, chunk_end)
           log_checkpoint(chunk_end)  # Track progress
           current = chunk_end
   ```

   | Data Volume per Day | Recommended Chunk Size | Rationale |
   |---------------------|------------------------|-----------|
   | < 1 GB | 30 days | Low overhead, fewer iterations |
   | 1-10 GB | 7 days | Balance between speed and recovery |
   | 10-100 GB | 1 day | Manageable memory, quick restarts |
   | > 100 GB | 1-6 hours | Fine-grained control, parallel processing |

2. **Implement Checkpointing**

   Always track progress to enable restart from failure:

   ```python
   # Store checkpoint in database or file
   def save_checkpoint(table_name, last_processed_date, status):
       checkpoint = {
           'table': table_name,
           'last_processed': last_processed_date.isoformat(),
           'status': status,
           'updated_at': datetime.utcnow().isoformat()
       }
       # Save to checkpoint store (Redis, DB, S3, etc.)
       checkpoint_store.save(checkpoint)

   def resume_backfill(table_name):
       checkpoint = checkpoint_store.get(table_name)
       if checkpoint and checkpoint['status'] != 'completed':
           return datetime.fromisoformat(checkpoint['last_processed'])
       return None  # Start from beginning
   ```

3. **Idempotency is Critical**

   Ensure re-running the same chunk produces identical results:

   ```sql
   -- Use MERGE/UPSERT instead of INSERT
   MERGE INTO target_table t
   USING source_chunk s
   ON t.id = s.id AND t.date = s.date
   WHEN MATCHED THEN UPDATE SET t.value = s.value, t.updated_at = CURRENT_TIMESTAMP
   WHEN NOT MATCHED THEN INSERT (id, date, value, updated_at) VALUES (s.id, s.date, s.value, CURRENT_TIMESTAMP);

   -- Or DELETE + INSERT pattern
   DELETE FROM target_table WHERE date BETWEEN @chunk_start AND @chunk_end;
   INSERT INTO target_table SELECT * FROM source WHERE date BETWEEN @chunk_start AND @chunk_end;
   ```

4. **Resource Management Strategies**

   | Strategy | Implementation | When to Use |
   |----------|----------------|-------------|
   | Off-peak scheduling | Run backfills during low-traffic hours | Shared production cluster |
   | Dedicated resources | Spin up separate cluster for backfill | Large backfills, SLA-critical production |
   | Throttled execution | Add delays between chunks | Competing with real-time workloads |
   | Dynamic scaling | Auto-scale based on queue depth | Cloud environments with elastic compute |

5. **Parallel Backfilling with Partitions**

   ```python
   from concurrent.futures import ThreadPoolExecutor, as_completed

   def parallel_backfill(partitions, max_workers=4):
       results = {}
       with ThreadPoolExecutor(max_workers=max_workers) as executor:
           futures = {
               executor.submit(process_partition, p): p
               for p in partitions
           }
           for future in as_completed(futures):
               partition = futures[future]
               try:
                   results[partition] = future.result()
               except Exception as e:
                   results[partition] = {'status': 'failed', 'error': str(e)}
       return results

   # Partition by non-overlapping keys (date, region, customer_id hash)
   partitions = generate_partitions(start_date, end_date, partition_column='date')
   parallel_backfill(partitions, max_workers=8)
   ```

6. **Validation and Reconciliation**

   Always validate backfilled data:

   ```sql
   -- Row count reconciliation
   SELECT
       'source' as dataset,
       date,
       COUNT(*) as row_count,
       SUM(amount) as total_amount
   FROM source_table
   WHERE date BETWEEN @start AND @end
   GROUP BY date

   UNION ALL

   SELECT
       'target' as dataset,
       date,
       COUNT(*) as row_count,
       SUM(amount) as total_amount
   FROM target_table
   WHERE date BETWEEN @start AND @end
   GROUP BY date;

   -- Flag discrepancies
   -- Expected: row counts and sums should match per date
   ```

7. **Handling Schema Evolution**

   | Scenario | Approach |
   |----------|----------|
   | New column added | Backfill with default/computed value, then switch to live |
   | Column type changed | Create new column, backfill, rename, drop old |
   | Column removed | No backfill needed, just update pipeline |
   | Business logic changed | Backfill affected date ranges with new logic |

   ```python
   # Version your backfill logic
   def compute_metric_v2(row):
       """Updated calculation as of 2024-01-15"""
       return row['revenue'] - row['refunds'] - row['chargebacks']

   def compute_metric_v1(row):
       """Original calculation before 2024-01-15"""
       return row['revenue'] - row['refunds']

   def backfill_metric(row):
       if row['date'] < date(2024, 1, 15):
           return compute_metric_v1(row)
       return compute_metric_v2(row)
   ```

8. **Backfill Priority and Ordering**

   ```
   Recommended backfill order:

   1. Most recent data first (highest business value)
      └── Users expect recent data to be accurate

   2. Then work backwards in time
      └── Diminishing returns on older data

   3. Or prioritize by business impact
      └── High-revenue customers/products first
   ```

9. **Monitoring and Alerting**

   Track these metrics during backfill:

   | Metric | Purpose | Alert Condition |
   |--------|---------|-----------------|
   | Chunks completed | Progress tracking | Stalled for > 1 hour |
   | Processing rate | Performance trending | < 50% of baseline |
   | Error rate | Quality monitoring | > 1% of chunks failed |
   | Resource utilization | Capacity planning | > 80% CPU/memory sustained |
   | Data latency | SLA tracking | Backfill blocking live data |

10. **Rollback Strategy**

    Always have a rollback plan:

    ```python
    # Option 1: Soft delete with backfill flag
    UPDATE target_table
    SET is_backfilled = true, backfill_batch_id = @batch_id
    WHERE date BETWEEN @start AND @end;

    # Rollback: DELETE WHERE backfill_batch_id = @batch_id

    # Option 2: Shadow table approach
    # 1. Backfill into target_table_new
    # 2. Validate thoroughly
    # 3. Swap: RENAME target_table TO target_table_old, target_table_new TO target_table
    # Rollback: Reverse the rename

    # Option 3: Time-travel (Delta Lake, Iceberg)
    # RESTORE TABLE target_table TO VERSION AS OF @pre_backfill_version
    ```

**Common Pitfalls to Avoid**:

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| No checkpointing | Full restart on failure | Implement checkpoint after each chunk |
| Non-idempotent writes | Duplicate data on retry | Use MERGE/UPSERT or DELETE+INSERT |
| Unbounded chunks | OOM errors, timeouts | Always limit chunk size |
| No validation | Silent data corruption | Compare source/target counts and sums |
| Blocking production | SLA violations | Use separate resources or throttle |
| Missing rollback plan | Stuck with bad data | Plan rollback before starting |

**Backfill Estimation Formula**:

```
total_backfill_time = (total_records / processing_rate) * overhead_factor

Where:
- processing_rate = records/hour from test run on sample data
- overhead_factor = 1.5 to 2.0 (accounts for retries, validation, checkpointing)

Example:
- 1 billion records to backfill
- Test shows 10 million records/hour
- Estimated time = (1B / 10M) * 1.5 = 150 hours ≈ 6.25 days
```

**External Resources**:
- https://www.getdbt.com/blog/what-is-incremental-models/
- https://databricks.com/blog/2020/03/06/introducing-delta-lake-on-databricks.html
- https://towardsdatascience.com/backfilling-data-incrementally-7a3be2dd5c48

---

## 2. Streaming & Real-Time Processing

### 2.1 Stream Processing Patterns

#### Kafka Streaming Watermark
**Definition**: Mechanism in streaming engines tracking progress through time to handle late-arriving data, triggering late-binding aggregations based on processing/event time.

**External Resources**:
- https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#handling-late-data-with-watermarks
- https://kafka.apache.org/documentation/streams/architecture/
- https://www.youtube.com/watch?v=3KDLX-_ycpY

#### Sessionization Algorithm
**Definition**: Algorithm grouping user events into sessions based on time windows and inactivity thresholds, enabling session-level analytics and user journey analysis.

**Key Implementation Techniques**:
- **Fixed Time Window Approach**: Create sessions by partitioning events into fixed-duration windows (e.g., 30-minute chunks); simple but doesn't adapt to actual user behavior gaps
- **Inactivity Timeout Method**: Define a timeout threshold (typically 10-30 minutes); if gap between consecutive events exceeds threshold, start new session; most common approach
- **Window Function with LEAD/LAG**: Use SQL window functions to compare current event timestamp with previous/next event; calculate time gaps and mark session boundaries
- **Session ID Generation with Row Number**: Assign unique session IDs by using row number within partitioned groups; restart row numbering when timeout is exceeded
- **Gap-and-Island Technique**: Create "islands" (continuous event groups) by calculating cumulative flag where timeout creates new island; group by island to define sessions
- **Spark Session Window**: Use Spark's `session_window()` function (available in Spark 3.2+) for efficient sessionization with configurable gap duration
- **Timestamp-Based Bucketing**: Bucket events into time buckets (hourly, daily) then apply sessionization within buckets to improve performance on large datasets
- **Multi-Level Sessionization**: Create sessions at multiple levels (page visits → sessions → day-long sessions) for hierarchical user journey analysis
- **User Agent / Device Change Detection**: Reset session on user agent or device change to isolate different platforms/devices in separate sessions
- **Geography/IP-Based Session Boundaries**: End session if user's IP or geography changes significantly; useful for fraud detection and multi-device tracking
- **Event Type-Driven Session Resets**: Define specific event types (logout, app crash, payment completion) that automatically end current session regardless of timeout
- **Weighted Inactivity Thresholds**: Use different timeout thresholds based on event type (page views = 30min, mobile app = 10min) reflecting user behavior patterns
- **Rolling Time Window with Overlap**: Create overlapping sessions for sliding window analytics; users appear in multiple sessions during overlapping periods
- **Attribution Window Definition**: Define sessions for marketing attribution (e.g., 30-day sessions for conversion tracking) different from behavior sessions
- **Real-Time Streaming Sessionization**: Use session watermarks in Spark Streaming or Kafka Streams to handle out-of-order events and late arrivals
- **Incremental Session Updates**: Update existing sessions incrementally as new events arrive rather than recalculating from scratch; efficient for streaming
- **Session Completion Detection**: Identify "completed" sessions based on timeout (no events for 30+ min) vs "active" sessions for real-time aggregation
- **Cross-Device Session Linking**: Link events across devices using user ID or fingerprinting; combine into unified user sessions spanning multiple devices
- **Bot/Crawler Filtering**: Filter automated sessions (identified by user agent or behavior patterns) separately to isolate legitimate user sessions
- **Session Merging on Re-identification**: When user logs in mid-session (initially anonymous), merge anonymous session with authenticated session for complete journey

**Practical Sessionization Workflow**:
1. **Prepare Event Data**: Collect user events with user_id, timestamp, event_type, and relevant context (device, location, app version)
2. **Sort by User and Time**: Partition events by user_id and sort chronologically within each user to establish event sequence
3. **Calculate Time Gap**: For each event, calculate time delta from previous event within same user (use LAG() window function or compare with previous row)
4. **Identify Session Boundaries**: Mark new session when time gap exceeds inactivity threshold (e.g., 30 minutes); create session boundary flag
5. **Generate Session IDs**: Use cumulative sum of boundary flags to generate session_id; all events with same flag sum belong to same session
6. **Validate Session Boundaries**: Check session distribution (min/max duration, count) to ensure thresholds align with expected user behavior
7. **Aggregate Session Metrics**: Calculate per-session metrics (duration, event count, first/last event, user actions, conversion) for analysis
8. **Enrich Session Data**: Join with user attributes (cohort, region, device) and event details (page, action, outcome) for contextual analysis
9. **Generate Session Dimensions**: Create session dimension table with session_id, user_id, start_time, end_time, duration, event_count, and session_type
10. **Implement Incremental Loading**: For streaming, store session state (incomplete sessions) and update incrementally as new events arrive
11. **Handle Late Arrivals**: Establish watermark; events arriving after watermark may reopen "completed" sessions (design based on SLA)
12. **Output for Analytics**: Store sessionized events and session dimensions in analytical warehouse for user journey, retention, and behavior analysis

**External Resources**:
- https://spark.apache.org/docs/latest/sql-programming-guide.html#unstructured-text
- https://www.youtube.com/watch?v=_-JM7kI7r2o
- https://www.getdbt.com/blog/sessionization-in-dbt/
- https://databricks.com/blog/2021/03/15/generating-sessions-using-apache-spark.html
- https://docs.databricks.com/structured-streaming/session-windowing.html
- https://mode.com/sql-tutorial/finding-user-sessions/

#### Testing Spark Streaming Pipelines
**Definition**: Strategies and frameworks for unit testing, integration testing, and performance testing of Spark Streaming applications with stateful operations.

**External Resources**:
- https://spark.apache.org/docs/latest/streaming-programming-guide.html#testing
- https://databricks.com/blog/2016/12/13/testing-cloud-native-code-on-production-data-in-apache-spark.html
- https://github.com/MrPowers/spark-streaming-test-example

#### Testing Kafka Streaming Pipelines
**Definition**: Testing approaches for Kafka Streams and Kafka consumers including embedded Kafka, test containers, and mocking techniques.

**External Resources**:
- https://kafka.apache.org/documentation/streams/developer-guide/testing.html
- https://testcontainers.org/modules/kafka/
- https://www.testcontainers.org/

#### Testcontainers vs Docker Compose
**Definition**: Testing approach comparison - Testcontainers uses containerized dependencies programmatically in code; Docker Compose manages containers via configuration files.

**External Resources**:
- https://www.testcontainers.org/
- https://docs.docker.com/compose/
- https://www.testcontainers.org/supported_docker_daemons/testcontainers-cloud/

### 2.2 Real-Time Communication

#### Web Sockets
**Definition**: Bidirectional communication protocol enabling persistent, low-latency connections between client and server for real-time data delivery.

**External Resources**:

- <https://en.wikipedia.org/wiki/WebSocket>
- <https://developer.mozilla.org/en-US/docs/Web/API/WebSocket>
- <https://www.rfc-editor.org/rfc/rfc6455>

#### Web Hooks
**Definition**: HTTP callbacks where a server sends POST requests to a configured URL when specific events occur, enabling event-driven integrations without polling.

**Key Characteristics**:

- Push-based: Server initiates request when event occurs (no polling)
- HTTP POST: Payload typically JSON with event data and metadata
- Async: Fire-and-forget delivery; sender doesn't wait for processing
- Stateless: Each request is independent, no persistent connection

**Common Use Cases**:

- Payment notifications (Stripe, PayPal)
- CI/CD triggers (GitHub, GitLab)
- Chat integrations (Slack, Discord)
- CRM/SaaS event notifications

**Implementation Best Practices**:

- **Verify signatures**: Validate HMAC/signature header to authenticate sender
- **Respond quickly**: Return 2xx immediately, process async in background queue
- **Idempotency**: Handle duplicate deliveries (use event ID for deduplication)
- **Retry logic**: Expect senders to retry on 4xx/5xx; implement exponential backoff
- **Logging**: Log received payloads for debugging and replay

**Comparison with Alternatives**:

| Approach | Direction | Connection | Best For |
| --- | --- | --- | --- |
| Webhooks | Server → Server | Per-event HTTP | Event notifications, integrations |
| WebSockets | Bidirectional | Persistent | Real-time UI, chat, gaming |
| SSE | Server → Client | Persistent HTTP | Live feeds, dashboards |
| Polling | Client → Server | Repeated requests | Legacy systems, simple cases |

**External Resources**:

- <https://en.wikipedia.org/wiki/Webhook>
- <https://docs.github.com/en/webhooks>
- <https://stripe.com/docs/webhooks>

#### Server-Sent Events (SSE)
**Definition**: Unidirectional server-to-client protocol for pushing updates using HTTP, simpler than WebSockets but limited to server-initiated messages.

**External Resources**:
- https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events
- https://html.spec.whatwg.org/multipage/server-sent-events.html
- https://www.w3.org/TR/eventsource/

#### Long Polling
**Definition**: Request-response pattern where clients repeatedly poll servers at intervals for new data, enabling near-real-time updates without persistent connections.

**External Resources**:
- https://en.wikipedia.org/wiki/Push_technology#Long_polling
- https://www.ably.io/topic/websockets
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

#### Message Queue
**Definition**: System for asynchronous communication between services, decoupling producers from consumers through intermediate message storage (e.g., RabbitMQ, Kafka, AWS SQS).

**External Resources**:
- https://aws.amazon.com/sqs/
- https://www.rabbitmq.com/
- https://kafka.apache.org/
