# Data Volume & Capacity Plan — Template & Best Practices

**Priority:** 17 — Right-size Kafka partitions, PostgreSQL storage, and compute before provisioning
**Owner:** Data Engineer + DevOps
**Phase:** 0 — Week 2; revisited in Phase 3 after load testing

---

## Purpose

Prevents under-provisioning (pipeline falls over under real load) and over-provisioning (wasted cost). Drives Kafka partition count, consumer group scaling, PostgreSQL sizing, and storage retention decisions.

---

## Document Metadata

| Field | Value |
|---|---|
| Document Owner | |
| Last Updated | |
| Version | 1.0 |
| Review Cycle | Phase 3 after load test; quarterly in production |

---

## Capacity Sizing Inputs

Collect these before calculating:

| Input | Value | Source |
|---|---|---|
| Total current records per entity | | Source System Profile |
| New records per day (average) | | Source System Profile |
| New records per day (peak) | | Source System Profile |
| Update rate per day | | Source System Profile |
| Average event payload size (bytes) | | Measure from sample events |
| Number of Kafka consumers per topic | | Architecture decision |
| Kafka retention period (days) | | Data retention policy |
| PostgreSQL row size estimate (bytes) | | Schema DDL |
| Expected data growth rate (% per year) | | Business estimate |

---

## Kafka Sizing

### Partition Count Formula

```
Recommended partitions = MAX(
    target_throughput_MB_per_sec / producer_throughput_per_partition_MB,
    target_throughput_MB_per_sec / consumer_throughput_per_partition_MB,
    number_of_consumers_in_group
)

Round up to the nearest power of 2 (easier to rebalance later).
Minimum: 3 partitions per topic for any production topic.
```

### Kafka Sizing Table

| Topic | Msgs/Day (avg) | Msgs/Day (peak) | Msg Size (bytes) | Throughput MB/s (peak) | Consumers | Recommended Partitions | Replication Factor |
|---|---|---|---|---|---|---|---|
| hr.employee.hired | 50 | 200 | 1,024 | 0.002 | 3 | 6 | 3 |
| hr.employee.terminated | 10 | 50 | 512 | 0.0003 | 3 | 3 | 3 |
| finance.invoice.approved | 500 | 2,000 | 2,048 | 0.04 | 2 | 6 | 3 |
| | | | | | | | |

### Kafka Storage Estimate

```
Storage per topic (GB) =
    (messages_per_day × avg_message_size_bytes × retention_days) / 1,073,741,824

With replication:
    Storage × replication_factor
```

| Topic | Msgs/Day | Msg Size | Retention | Raw Storage (GB) | With 3x Replication (GB) |
|---|---|---|---|---|---|
| hr.employee.hired | 50 | 1,024 B | 7 days | 0.0003 | 0.001 |
| finance.invoice.approved | 500 | 2,048 B | 7 days | 0.007 | 0.021 |
| **Total (all topics)** | | | | | |

---

## PostgreSQL Sizing

### Storage Estimate

```
Table storage (GB) =
    (total_rows × avg_row_size_bytes) / 1,073,741,824

Include:
  + 20% for indexes
  + 20% for PostgreSQL overhead (MVCC, page fill factor)
  + growth buffer for 2 years at expected growth rate
```

| Table | Current Rows | Avg Row Size | Current Storage (MB) | 1-Year Growth | 2-Year Estimate |
|---|---|---|---|---|---|
| employees | 5,000 | 512 B | 2.4 MB | +20% | 3.5 MB |
| invoices | 50,000 | 1,024 B | 47.7 MB | +30% | 80 MB |
| | | | | | |
| **Total** | | | | | |

### Connection Pool Sizing

```
Max connections = (num_cpu_cores × 2) + num_disk_spindles

For K8s: size per pod, not per cluster.
Rule of thumb: 10 connections per consumer service pod.
Use PgBouncer in transaction mode for high-connection workloads.
```

| Service | Pods | Connections per Pod | Max Total Connections |
|---|---|---|---|
| finance-service | 3 | 10 | 30 |
| payroll-service | 2 | 10 | 20 |
| PgBouncer pool | — | — | 100 (to PostgreSQL) |

---

## Consumer Scaling

### How Many Consumer Instances?

```
Max parallelism = number of partitions on the topic
(You cannot have more active consumers in a group than partitions)

Recommended: start at partitions / 3, scale to partitions under load.
```

| Topic | Partitions | Min Consumers | Max Consumers | Scale Trigger |
|---|---|---|---|---|
| hr.employee.hired | 6 | 2 | 6 | Consumer lag > 500 msgs |
| finance.invoice.approved | 6 | 2 | 6 | Consumer lag > 1,000 msgs |

### Kubernetes HPA (Horizontal Pod Autoscaler) Config

Trigger autoscaling based on Kafka consumer lag (via KEDA — Kubernetes Event-Driven Autoscaling):

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: finance-service-scaler
spec:
  scaleTargetRef:
    name: finance-service
  minReplicaCount: 2
  maxReplicaCount: 6
  triggers:
    - type: kafka
      metadata:
        topic: finance.invoice.approved
        bootstrapServers: kafka:9092
        consumerGroup: finance-service-group
        lagThreshold: "100"
```

---

## Load Test Targets

Define acceptance criteria before Phase 3 load testing:

| Metric | Target | Test Tool |
|---|---|---|
| Consumer lag under peak load | < 1,000 messages | k6 + Kafka producer |
| API p99 latency under load | < 2 seconds | k6 |
| API error rate under load | < 0.1% | k6 |
| Pipeline end-to-end latency | < 5 minutes | Manual trace |
| PostgreSQL CPU under peak | < 70% | Grafana |
| PostgreSQL connection utilisation | < 80% | Grafana |
| Kafka broker CPU under peak | < 60% | Grafana |

---

## Capacity Review Triggers

Re-run this plan when any of the following occur:

```
[ ] A new integration is added that materially increases volume
[ ] Data volume grows > 50% above original estimate
[ ] Load test results exceed any target threshold
[ ] Quarterly capacity review
[ ] Before onboarding a new high-volume source system
```
