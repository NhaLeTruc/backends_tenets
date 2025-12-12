# ScyllaDB to PostgreSQL CDC Pipeline - Scaling Guide

## Overview

This guide provides capacity planning and scaling strategies for the CDC pipeline to handle growing data volumes and throughput requirements.

## Table of Contents

1. [Current Capacity](#current-capacity)
2. [Growth Projections](#growth-projections)
3. [Scaling Decision Matrix](#scaling-decision-matrix)
4. [Horizontal Scaling](#horizontal-scaling)
5. [Vertical Scaling](#vertical-scaling)
6. [Performance Testing](#performance-testing)
7. [Cost Optimization](#cost-optimization)
8. [Monitoring and Metrics](#monitoring-and-metrics)

---

## Current Capacity

### Baseline Metrics (Development Environment)

**Infrastructure**:
- 1 ScyllaDB node (4 cores, 8 GB RAM)
- 1 PostgreSQL instance (4 cores, 8 GB RAM)
- 1 Kafka broker (2 cores, 4 GB RAM)
- 1 Kafka Connect worker (2 cores, 4 GB RAM)

**Performance**:
- Throughput: 5,000 events/sec
- End-to-end latency: 200ms (p95)
- Total data volume: 1M records (10 GB)
- Daily change volume: 10,000 changes/day

**Resource Utilization**:
```bash
# Check current utilization
docker stats --no-stream

# Example output:
CONTAINER          CPU %    MEM USAGE / LIMIT     MEM %
scylla            25%      4GB / 8GB             50%
postgres          15%      3GB / 8GB             37.5%
kafka             10%      2GB / 4GB             50%
kafka-connect     20%      2GB / 4GB             50%
```

### Production Baseline

**Infrastructure**:
- 3 ScyllaDB nodes (8 cores, 32 GB RAM each)
- 1 PostgreSQL primary + 1 replica (16 cores, 64 GB RAM each)
- 3 Kafka brokers (8 cores, 16 GB RAM each)
- 3 Kafka Connect workers (4 cores, 8 GB RAM each)

**Performance**:
- Throughput: 50,000 events/sec
- End-to-end latency: 100ms (p95)
- Total data volume: 100M records (1 TB)
- Daily change volume: 1M changes/day

---

## Growth Projections

### 6-Month Projection

**Data Growth**:
| Metric | Current | 6 Months | Growth |
|--------|---------|----------|--------|
| Total Records | 100M | 1B | 10x |
| Data Size | 1 TB | 10 TB | 10x |
| Daily Changes | 1M | 10M | 10x |
| Peak Events/sec | 50K | 500K | 10x |

**Required Capacity**:
- ScyllaDB: 9 nodes (3 → 9)
- Kafka: 9 brokers (3 → 9)
- Kafka Connect: 12 workers (3 → 12)
- PostgreSQL: Vertical scaling to 32 cores, 128 GB RAM

### 12-Month Projection

**Data Growth**:
| Metric | Current | 12 Months | Growth |
|--------|---------|-----------|--------|
| Total Records | 100M | 5B | 50x |
| Data Size | 1 TB | 50 TB | 50x |
| Daily Changes | 1M | 50M | 50x |
| Peak Events/sec | 50K | 2.5M | 50x |

**Required Capacity**:
- ScyllaDB: 30 nodes
- Kafka: 15 brokers
- Kafka Connect: 30 workers
- PostgreSQL: Sharding required (3-5 shards)

---

## Scaling Decision Matrix

### When to Scale Horizontally

**Indicators**:
- CPU utilization >70% sustained
- Memory utilization >80% sustained
- Replication lag >300 seconds
- Throughput approaching 80% of maximum capacity
- Storage >75% full

**Recommended Actions**:

| Component | Current Utilization | Action | Expected Improvement |
|-----------|---------------------|--------|---------------------|
| ScyllaDB | CPU >70% | Add 1-2 nodes | +50-100% throughput |
| Kafka | Disk >75% | Add 1 broker | +33% storage capacity |
| Kafka Connect | CPU >70% | Add 2 workers | +67% processing capacity |
| PostgreSQL | CPU >80% | Add read replica | Offload read queries |

### When to Scale Vertically

**Indicators**:
- Single-threaded bottlenecks
- Memory-intensive operations (sorts, aggregations)
- I/O-bound workloads (disk throughput limit)
- Latency-sensitive operations

**Recommended Actions**:

| Component | Bottleneck | Action | Expected Improvement |
|-----------|-----------|--------|---------------------|
| ScyllaDB | Disk I/O | Upgrade to NVMe | 5-10x IOPS |
| PostgreSQL | Memory | Double RAM | Better cache hit ratio |
| Kafka | Network | 10 Gbps NIC | +10x network throughput |
| Kafka Connect | CPU | Double cores | +50% single-task performance |

### Cost-Benefit Analysis

**Horizontal Scaling**:
- **Pros**: Better fault tolerance, linear scalability, no downtime
- **Cons**: Higher complexity, network overhead, rebalancing needed
- **Cost**: 3x increase in nodes = 3x compute cost

**Vertical Scaling**:
- **Pros**: Simpler architecture, better for single-threaded workloads
- **Cons**: Downtime required, upper limits, diminishing returns
- **Cost**: 2x RAM/CPU = ~1.5x compute cost (economies of scale)

**Recommendation**:
- **Horizontal first** for distributed components (ScyllaDB, Kafka, Kafka Connect)
- **Vertical first** for PostgreSQL (until sharding becomes necessary)
- **Hybrid approach** for best cost/performance ratio

---

## Horizontal Scaling

### Scale ScyllaDB Cluster

#### Add Nodes to Existing Cluster

```bash
# 1. Provision new node
docker-compose up -d scylla-node-4

# 2. Configure new node to join cluster
docker exec scylla-node-4 nodetool status

# Expected output shows new node joining:
# UN  192.168.1.4  ?       256 KB  1    ?  <rack-id>

# 3. Wait for node to join (status changes to UN - Up Normal)
watch -n 10 'docker exec scylla nodetool status'

# 4. Run repair to sync data
docker exec scylla-node-4 nodetool repair

# 5. Monitor repair progress
docker exec scylla-node-4 nodetool compactionstats

# 6. Verify data distribution
docker exec scylla nodetool status | grep "Load"
```

**Expected Timeline**:
- Node join: 5-10 minutes
- Data rebalance: 2-4 hours (for 1 TB)
- Repair completion: 4-8 hours

**Post-Scaling Validation**:
```bash
# Check cluster health
docker exec scylla nodetool status
docker exec scylla nodetool describecluster

# Verify replication
docker exec scylla nodetool getendpoints app_data users <key>

# Test performance
./scripts/benchmark.sh --profile large
```

#### Remove Nodes (Scale Down)

```bash
# 1. Decommission node (moves data to other nodes)
docker exec scylla-node-4 nodetool decommission

# 2. Monitor decommission progress
watch -n 10 'docker exec scylla nodetool status'

# 3. Stop node after decommission completes
docker-compose stop scylla-node-4

# 4. Remove from compose file
vim docker-compose.yml
```

### Scale Kafka Cluster

#### Add Broker

```bash
# 1. Start new broker
docker-compose up -d kafka-broker-4

# 2. Verify broker joined
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092 | grep "id: 4"

# 3. Create partition reassignment plan
cat > /tmp/reassignment.json << 'EOF'
{
  "version": 1,
  "partitions": [
    {
      "topic": "cdc.scylla.users",
      "partition": 0,
      "replicas": [1, 2, 3, 4]
    }
  ]
}
EOF

# 4. Execute reassignment
docker exec kafka kafka-reassign-partitions \
  --bootstrap-server localhost:9092 \
  --reassignment-json-file /tmp/reassignment.json \
  --execute

# 5. Monitor progress
docker exec kafka kafka-reassign-partitions \
  --bootstrap-server localhost:9092 \
  --reassignment-json-file /tmp/reassignment.json \
  --verify

# 6. Increase partition count for better distribution
docker exec kafka kafka-topics --bootstrap-server localhost:9092 \
  --alter --topic cdc.scylla.users --partitions 16
```

**Expected Timeline**:
- Broker join: 1-2 minutes
- Partition reassignment: 30-60 minutes (for 100 GB)

### Scale Kafka Connect Workers

#### Add Workers

```bash
# 1. Scale up workers
docker-compose up -d --scale kafka-connect=6

# 2. Wait for workers to join
sleep 60

# 3. Verify worker count
curl -s http://localhost:8083/ | jq '.

# 4. Check task rebalance
curl -s http://localhost:8083/connectors/scylla-source/status | \
  jq '.tasks[] | {id: .id, worker_id: .worker_id}'

# Expected: Tasks distributed across 6 workers
```

**Automatic Rebalancing**:
- Kafka Connect automatically redistributes tasks
- No manual intervention required
- Rebalance completes in 30-60 seconds

#### Remove Workers (Scale Down)

```bash
# 1. Stop worker gracefully
docker-compose stop kafka-connect-6

# 2. Wait for task rebalance (automatic)
sleep 60

# 3. Verify tasks redistributed
curl -s http://localhost:8083/connectors/scylla-source/status | jq .

# 4. Remove from compose
docker-compose up -d --scale kafka-connect=5
```

### Scale PostgreSQL (Read Replicas)

#### Add Read Replica

```bash
# 1. Create replica from primary backup
docker exec postgres pg_basebackup -h postgres-primary -D /var/lib/postgresql/data \
  -U replication -Fp -Xs -P -R

# 2. Start replica
docker-compose up -d postgres-replica

# 3. Verify replication
docker exec postgres-primary psql -U postgres -c \
  "SELECT client_addr, state, sync_state FROM pg_stat_replication;"

# Expected output:
#   client_addr   |   state   | sync_state
# ----------------+-----------+------------
#  192.168.1.10   | streaming | async

# 4. Check replication lag
docker exec postgres-replica psql -U postgres -c \
  "SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;"

# Expected: <1 second
```

**Use Cases for Read Replicas**:
- Reconciliation queries (read-only)
- Analytics and reporting
- Dashboard queries
- Backup operations

---

## Vertical Scaling

### Increase ScyllaDB Resources

```bash
# 1. Update resource limits
vim docker-compose.yml

# Change:
services:
  scylla:
    cpus: '16'        # from 8
    mem_limit: 64g    # from 32g

# 2. Restart node (one at a time in cluster)
docker-compose restart scylla-node-1

# 3. Verify new resources
docker stats scylla-node-1

# 4. Monitor performance improvement
./scripts/benchmark.sh --profile large
```

### Increase Kafka Connect Memory

```bash
# 1. Update JVM heap
vim docker-compose.yml

environment:
  KAFKA_HEAP_OPTS: "-Xms8G -Xmx16G"  # from -Xms4G -Xmx8G

# 2. Restart workers (rolling restart)
for i in {1..3}; do
  docker-compose restart kafka-connect-$i
  sleep 120  # Wait for rebalance
done

# 3. Verify heap size
docker exec kafka-connect-1 jmap -heap <pid> | grep "MaxHeapSize"
```

### Optimize PostgreSQL Configuration

```bash
# 1. Update PostgreSQL settings for larger instance
vim configs/postgres/postgresql.conf

# Memory settings (for 64 GB RAM instance)
shared_buffers = 16GB              # from 8GB (25% of RAM)
effective_cache_size = 48GB        # from 24GB (75% of RAM)
maintenance_work_mem = 4GB         # from 2GB
work_mem = 64MB                    # from 32MB

# Parallelism (for 16 core instance)
max_worker_processes = 16          # from 8
max_parallel_workers_per_gather = 8  # from 4
max_parallel_workers = 16          # from 8

# Checkpoint settings
checkpoint_completion_target = 0.9
wal_buffers = 16MB
max_wal_size = 8GB

# 2. Restart PostgreSQL
docker-compose restart postgres

# 3. Verify settings
docker exec postgres psql -U postgres -c "SHOW shared_buffers;"
docker exec postgres psql -U postgres -c "SHOW max_parallel_workers;"
```

---

## Performance Testing

### Baseline Performance Test

```bash
# 1. Run benchmark before scaling
./scripts/benchmark.sh --profile medium --duration 300

# Output:
# Throughput: 50,000 events/sec
# Latency p50: 50ms
# Latency p95: 100ms
# Latency p99: 200ms

# 2. Record baseline metrics
cat /tmp/benchmark-results-*.json
```

### Post-Scaling Validation

```bash
# After adding 3 ScyllaDB nodes and 3 Kafka brokers
./scripts/benchmark.sh --profile large --duration 300

# Expected improvement:
# Throughput: 150,000 events/sec (+3x)
# Latency p50: 40ms (-20%)
# Latency p95: 80ms (-20%)
# Latency p99: 150ms (-25%)
```

### Load Testing Scenarios

#### Scenario 1: Steady State Load

```bash
# Simulate normal production load
./scripts/generate-load.sh \
  --duration 3600 \
  --rate 50000 \
  --workers 10 \
  --operation-mix "insert:60,update:30,delete:10"

# Monitor metrics during test
watch -n 5 'curl -s http://localhost:9090/api/v1/query?query=cdc_replication_lag_seconds'
```

#### Scenario 2: Burst Load

```bash
# Simulate traffic spike
./scripts/generate-load.sh \
  --duration 300 \
  --rate 200000 \
  --workers 20 \
  --burst-mode

# Check if system handles burst gracefully
./scripts/health-check.sh
```

#### Scenario 3: Sustained High Load

```bash
# Test maximum sustainable throughput
./scripts/benchmark.sh --profile stress --duration 7200

# Acceptable criteria:
# - Replication lag stays <60 seconds
# - Error rate <0.01%
# - CPU utilization <80%
# - Memory utilization <85%
```

### Performance Regression Testing

```bash
# Run before and after any infrastructure changes
./scripts/benchmark.sh --profile medium --compare-baseline /tmp/baseline.json

# Output will show performance delta:
# Throughput: +15% (improvement)
# Latency p95: -10% (improvement)
# Error rate: +0.001% (acceptable)
```

---

## Cost Optimization

### Resource Right-Sizing

**Over-Provisioned Indicators**:
```bash
# Check CPU utilization (should be >50% average)
docker stats --format "table {{.Name}}\t{{.CPUPerc}}"

# Check memory utilization (should be >60% average)
docker stats --format "table {{.Name}}\t{{.MemPerc}}"

# If consistently low, reduce resources
```

**Under-Provisioned Indicators**:
- CPU >80% sustained
- Memory >90% sustained
- High swap usage
- Increasing replication lag
- Rising error rates

### Kafka Topic Retention Optimization

```bash
# Reduce retention to save disk space
docker exec kafka kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name cdc.scylla.users \
  --alter \
  --add-config retention.ms=43200000  # 12 hours instead of 24

# Enable compression
docker exec kafka kafka-configs --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name cdc.scylla.users \
  --alter \
  --add-config compression.type=snappy

# Expected savings: 40-60% disk space
```

### ScyllaDB Compaction Strategy

```bash
# Use Incremental Compaction Strategy (ICS) for better performance
docker exec scylla cqlsh -e \
  "ALTER TABLE app_data.users WITH compaction = {
    'class': 'IncrementalCompactionStrategy'
  };"

# Benefits:
# - 10-30% better write throughput
# - Lower space amplification
# - More predictable latency
```

### Batch Size Tuning

```bash
# Larger batches = fewer requests = lower cost
vim configs/connectors/postgres-sink.json

# Increase batch size:
"batch.size": "5000"  # from 3000

# Monitor impact on latency (should stay <200ms)
./scripts/deploy-connector.sh update postgres-sink
```

### Auto-Scaling Strategy

**Scale Up Triggers**:
- CPU >70% for 10 minutes
- Memory >80% for 10 minutes
- Replication lag >300 seconds for 5 minutes

**Scale Down Triggers**:
- CPU <30% for 60 minutes
- Memory <50% for 60 minutes
- Off-peak hours (2 AM - 6 AM)

**Implementation** (Kubernetes example):
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: kafka-connect-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: kafka-connect
  minReplicas: 3
  maxReplicas: 12
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

## Monitoring and Metrics

### Key Scaling Metrics

```bash
# Throughput trends
curl -s 'http://localhost:9090/api/v1/query_range?query=rate(cdc_records_replicated_total[5m])&start=<start>&end=<end>&step=60'

# Latency trends
curl -s 'http://localhost:9090/api/v1/query_range?query=cdc_replication_lag_seconds&start=<start>&end=<end>&step=60'

# Resource utilization trends
curl -s 'http://localhost:9090/api/v1/query_range?query=container_cpu_usage_seconds_total&start=<start>&end=<end>&step=60'
```

### Capacity Planning Dashboard

Create Grafana dashboard with:
- Current vs. maximum capacity (%)
- Projected capacity exhaustion date
- Resource utilization trends (30-day)
- Growth rate (week-over-week, month-over-month)

### Alerting for Capacity

```yaml
# docker/prometheus/alert-rules.yml
- alert: HighCapacityUtilization
  expr: cdc_records_replicated_total / cdc_max_capacity > 0.8
  for: 1h
  labels:
    severity: warning
  annotations:
    summary: "Approaching capacity limit"
    description: "Current utilization at {{ $value }}%, scale up recommended"

- alert: CriticalCapacityUtilization
  expr: cdc_records_replicated_total / cdc_max_capacity > 0.9
  for: 30m
  labels:
    severity: critical
  annotations:
    summary: "Critical capacity limit"
    description: "Current utilization at {{ $value }}%, scale up immediately"
```

---

## Scaling Checklist

### Pre-Scaling

- [ ] Backup all data and offsets
- [ ] Document current performance baselines
- [ ] Test scaling procedure in staging
- [ ] Schedule maintenance window (if downtime required)
- [ ] Notify stakeholders

### During Scaling

- [ ] Execute scaling procedure step-by-step
- [ ] Monitor metrics continuously
- [ ] Verify data rebalancing/replication
- [ ] Run health checks after each step
- [ ] Document any issues encountered

### Post-Scaling

- [ ] Run performance benchmarks
- [ ] Compare against baselines
- [ ] Run reconciliation to verify data consistency
- [ ] Update capacity planning documentation
- [ ] Monitor for 24 hours for regression
- [ ] Update runbook with lessons learned

---

## Best Practices

1. **Scale proactively**: Don't wait for outages
2. **Test in staging**: Always test scaling procedures before production
3. **Monitor continuously**: Watch metrics during and after scaling
4. **Document everything**: Record configurations, procedures, results
5. **Automate where possible**: Use infrastructure as code (Terraform, CloudFormation)
6. **Plan for failure**: Have rollback procedures ready
7. **Cost-optimize**: Right-size resources after scaling
8. **Review quarterly**: Revisit capacity planning every 3 months

---

## References

- [ScyllaDB Scaling Guide](https://docs.scylladb.com/stable/operating-scylla/procedures/cluster-management/add-node-to-cluster/)
- [Kafka Scaling Best Practices](https://kafka.apache.org/documentation/#basic_ops_cluster_expansion)
- [PostgreSQL Performance Tuning](https://www.postgresql.org/docs/current/performance-tips.html)
- [Kafka Connect Scaling](https://docs.confluent.io/platform/current/connect/userguide.html#distributed-mode)

---

**Document Version**: 1.0
**Last Updated**: 2025-12-09
**Maintained By**: Platform Team
**Review Cycle**: Quarterly
