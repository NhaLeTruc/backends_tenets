# Consumer Group Registry — Template & Best Practices

**Priority:** 18 — Prevents consumer group naming conflicts and orphaned groups
**Owner:** Data Engineer
**Phase:** 1 — Week 4; updated as each consumer is deployed

---

## Purpose

The Consumer Group Registry is the authoritative list of every Kafka consumer group in the platform — what it reads, who owns it, and its current health. Prevents naming collisions, orphaned groups accumulating lag, and confusion during incident triage.

**Rule:** No consumer group goes to production without an entry here first.

---

## Consumer Group Naming Convention

```
{service-name}-{topic-domain}-{purpose}-group

Examples:
  finance-service-hr-employee-group
  it-provisioning-hr-employee-group
  payroll-service-hr-employee-group
  reporting-service-finance-invoice-group
```

**Rules:**
- All lowercase, hyphen-separated
- Always include the service name — makes `kafka-consumer-groups.sh` output immediately readable
- Never reuse a group name for a different topic or purpose
- Dead groups must be deleted from the broker, not just abandoned

---

## Consumer Group Registry Table

| Group ID | Topic(s) Consumed | Consumer Service | Owner Team | Pod / Deployment | Partition Assignment | Lag Alert Threshold | Status | Notes |
|---|---|---|---|---|---|---|---|---|
| finance-service-hr-employee-group | hr.employee.hired, hr.employee.terminated | finance-service | Finance Integration Team | K8s: finance-service | Auto (range) | 500 msgs | Active | |
| it-provisioning-hr-employee-group | hr.employee.hired, hr.employee.terminated | it-provisioning-service | IT Ops Team | K8s: it-provisioning-service | Auto (range) | 500 msgs | Active | |
| payroll-service-hr-employee-group | hr.employee.hired | payroll-service | Payroll Team | K8s: payroll-service | Auto (range) | 1,000 msgs | Active | |
| reporting-finance-invoice-group | finance.invoice.approved | reporting-service | Analytics Team | K8s: reporting-service | Auto (range) | 2,000 msgs | Active | |
| | | | | | | | | |

---

## Consumer Group Entry Template

One block per consumer group.

---

### Group: `finance-service-hr-employee-group`

| Field | Value |
|---|---|
| **Group ID** | finance-service-hr-employee-group |
| **Topics** | hr.employee.hired, hr.employee.terminated |
| **Consumer Service** | finance-service |
| **Owner Team** | Finance Integration Team |
| **Owner Contact** | |
| **K8s Deployment** | finance-service |
| **K8s Namespace** | integrations |
| **Min Replicas** | 2 |
| **Max Replicas** | 6 |
| **Partition Assignment Strategy** | RangeAssignor |
| **Auto Offset Reset** | earliest (new group), latest (restart) |
| **Enable Auto Commit** | No — manual commit after successful DB write |
| **Max Poll Records** | 100 |
| **Session Timeout** | 30,000 ms |
| **Heartbeat Interval** | 10,000 ms |
| **Lag Alert Threshold** | 500 messages |
| **DLQ Topic** | hr.employee.hired.dlq |
| **Idempotency Key** | source_event_id |
| **Status** | Active |
| **Created Date** | |
| **Last Modified** | |

---

## Prometheus Lag Monitoring Query

Use this Grafana query to show consumer lag per group:

```promql
kafka_consumer_group_lag{
  group=~"finance-service-hr-employee-group"
}
```

Alert rule (fire if lag exceeds threshold for 5 minutes):

```yaml
- alert: KafkaConsumerLagHigh
  expr: kafka_consumer_group_lag > 500
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Consumer group {{ $labels.group }} lag is {{ $value }}"
    runbook: "https://docs.internal/runbooks/kafka-consumer-lag"
```

---

## Useful Kafka CLI Commands

```bash
# List all consumer groups
kafka-consumer-groups.sh --bootstrap-server kafka:9092 --list

# Describe a specific group (shows lag per partition)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --describe --group finance-service-hr-employee-group

# Reset offsets to earliest (use for replay)
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group finance-service-hr-employee-group \
  --topic hr.employee.hired \
  --reset-offsets --to-earliest --execute

# Delete an orphaned / retired consumer group
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --delete --group old-retired-group-name
```

---

## Consumer Group Health Checklist

Run weekly and during incident triage:

```
[ ] All active groups have lag below their alert threshold
[ ] No orphaned groups with growing lag and no active consumers
[ ] All groups consuming from existing (non-deleted) topics
[ ] DLQ topics for each group are being monitored
[ ] No group is using auto-commit (manual commit enforced)
[ ] Consumer group names match naming convention
[ ] Registry is up to date with deployed groups
```
