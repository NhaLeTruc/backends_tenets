# Production Deployment

## Production Readiness Checklist

## Infrastructure

- [ ] Provision production infrastructure (3+ nodes per service)
- [ ] Configure VPC/network segmentation
- [ ] Set up firewall rules (allow only necessary ports)
- [ ] Enable auto-scaling for Kafka Connect workers
- [ ] Configure load balancers (if applicable)
- [ ] Set up DNS records for service discovery
- [ ] Provision sufficient storage (1TB+ per ScyllaDB node)
- [ ] Use NVMe/SSD for all database and Kafka storage

## Security

- [ ] Generate production TLS certificates (Let's Encrypt or CA)
- [ ] Enable TLS 1.2+ for all connections (ScyllaDB, PostgreSQL, Kafka)
- [ ] Configure mutual TLS (mTLS) for service-to-service communication
- [ ] Change all default passwords (use password manager)
- [ ] Configure HashiCorp Vault in production mode (HA setup)
- [ ] Store all credentials in Vault (never in code or config files)
- [ ] Enable authentication on all services (ScyllaDB, Kafka, PostgreSQL)
- [ ] Configure role-based access control (RBAC)
- [ ] Set up IP whitelisting / VPN access
- [ ] Enable audit logging on databases
- [ ] Configure secret rotation (90-day cycle)
- [ ] Review and apply security hardening guide: [configs/security/README.md](configs/security/README.md)

## Kafka Configuration

- [ ] Set replication factor to 3 for all topics
- [ ] Configure min.insync.replicas=2
- [ ] Set retention policy (24-48 hours recommended)
- [ ] Enable compression (snappy or lz4)
- [ ] Configure log cleanup policy (delete or compact)
- [ ] Set up topic auto-creation policy
- [ ] Increase partition count for high-throughput topics
- [ ] Enable JMX for monitoring

## Database Configuration

**ScyllaDB**:
- [ ] Enable CDC on all source tables
- [ ] Configure compaction strategy (ICS recommended)
- [ ] Set appropriate replication factor (RF=3)
- [ ] Enable audit logging
- [ ] Configure connection pooling
- [ ] Set up user authentication (PasswordAuthenticator)
- [ ] Create service accounts with least privilege

**PostgreSQL**:
- [ ] Configure connection pooling (PgBouncer recommended)
- [ ] Enable Write-Ahead Logging (WAL) archiving
- [ ] Set up read replicas for query load
- [ ] Tune performance parameters (shared_buffers, work_mem)
- [ ] Create indexes on frequently queried columns
- [ ] Configure vacuum and analyze schedules
- [ ] Enable statement logging for audit
- [ ] Set up row-level security (if needed)

## Connector Configuration

- [ ] Review and optimize connector configurations
- [ ] Set appropriate batch sizes (1000-5000)
- [ ] Configure error tolerance and DLQ
- [ ] Enable exactly-once semantics
- [ ] Set max retries and backoff
- [ ] Configure heartbeat interval (30s)
- [ ] Test connector failover scenarios
- [ ] Document connector dependencies

## Monitoring & Alerting

- [ ] Deploy Prometheus in HA mode (2+ instances)
- [ ] Configure AlertManager for notifications
- [ ] Set up alert routing (email, Slack, PagerDuty)
- [ ] Create Grafana dashboards for all metrics
- [ ] Configure alert rules (see [docker/prometheus/alert-rules.yml](docker/prometheus/alert-rules.yml))
- [ ] Test alert delivery (send test alerts)
- [ ] Set up on-call rotation
- [ ] Configure log aggregation (ELK, Splunk, or CloudWatch)
- [ ] Enable distributed tracing (Jaeger)
- [ ] Set up uptime monitoring (external probes)
- [ ] Configure retention policies for metrics (30-90 days)

## Backup & Disaster Recovery

- [ ] Set up automated offset backups (daily): `./scripts/backup-offsets.sh`
- [ ] Configure PostgreSQL backups (pg_dump daily + WAL archiving)
- [ ] Set up ScyllaDB snapshots (nodetool snapshot)
- [ ] Test restore procedures (quarterly)
- [ ] Document recovery time objective (RTO: 4 hours)
- [ ] Document recovery point objective (RPO: 24 hours)
- [ ] Store backups in separate region/location
- [ ] Encrypt backups at rest
- [ ] Set up backup retention policy (30-90 days)
- [ ] Create disaster recovery runbook

## Performance & Capacity

- [ ] Run baseline performance benchmark: `./scripts/benchmark.sh --profile large`
- [ ] Load test with expected peak traffic (2x normal load)
- [ ] Stress test to find breaking points: `./scripts/benchmark.sh --profile stress`
- [ ] Test failure recovery scenarios: `./scripts/test-failure-recovery.sh`
- [ ] Document capacity limits (max throughput, storage)
- [ ] Create capacity planning model (see [docs/scaling.md](docs/scaling.md))
- [ ] Set up auto-scaling thresholds
- [ ] Configure resource limits (CPU, memory)
- [ ] Plan for 6-month growth

## Operational Procedures

- [ ] Document deployment procedures (see [docs/runbook.md](docs/runbook.md))
- [ ] Create troubleshooting guide (see [docs/troubleshooting.md](docs/troubleshooting.md))
- [ ] Write incident response playbook
- [ ] Schedule reconciliation (daily cron): `crontab -e`
  ```cron
  0 2 * * * /path/to/scripts/schedule-reconciliation.sh --all-tables
  ```
- [ ] Set up DLQ monitoring and replay procedures
- [ ] Document schema evolution process
- [ ] Create maintenance window procedures
- [ ] Test rollback procedures
- [ ] Conduct chaos engineering tests: `./scripts/chaos-test.sh`

## Testing & Validation

- [ ] Run all unit tests: `pytest -m unit`
- [ ] Run integration tests: `pytest -m integration`
- [ ] Test schema evolution scenarios: `./scripts/test-schema-evolution.sh`
- [ ] Test failure recovery: `./scripts/test-failure-recovery.sh`
- [ ] Test network partition: `./scripts/test-network-partition.sh`
- [ ] Test poison message handling: `./scripts/test-poison-message.sh`
- [ ] Validate data consistency: `./scripts/reconcile.py full --all-tables`
- [ ] Test monitoring and alerting (trigger test alerts)
- [ ] Perform load testing at scale
- [ ] Conduct security penetration testing

## Documentation

- [ ] Update architecture diagrams
- [ ] Document all environment variables
- [ ] Create API documentation (if applicable)
- [ ] Write operator training guide
- [ ] Document all configuration parameters
- [ ] Create FAQ from common issues
- [ ] Update README with production URLs
- [ ] Document SLAs and SLOs
- [ ] Create change management process
- [ ] Write post-mortem template

## Compliance & Governance

- [ ] Review data privacy requirements (GDPR, CCPA)
- [ ] Implement data retention policies
- [ ] Configure audit logging for compliance
- [ ] Document data lineage and transformations
- [ ] Set up access logs and reviews
- [ ] Create data classification policy
- [ ] Implement data masking (if needed)
- [ ] Schedule compliance audits
- [ ] Document incident notification procedures

## Go-Live

- [ ] Schedule go-live date and time
- [ ] Communicate to stakeholders
- [ ] Prepare rollback plan
- [ ] Conduct final pre-flight check
- [ ] Monitor closely for first 24 hours
- [ ] Hold post-deployment retrospective
- [ ] Update production documentation

## Production Deployment Steps

1. **Infrastructure Setup** (Day 1-3)
   ```bash
   # Provision infrastructure using IaC (Terraform/CloudFormation)
   terraform apply -var-file=production.tfvars
   ```

2. **Security Configuration** (Day 4-5)
   ```bash
   # Generate certificates
   ./scripts/generate-certs.sh production

   # Configure Vault
   vault operator init
   vault operator unseal
   ```

3. **Service Deployment** (Day 6-7)
   ```bash
   # Deploy services
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

   # Verify health
   ./scripts/health-check.sh
   ```

4. **Connector Deployment** (Day 8)
   ```bash
   # Deploy connectors
   ./scripts/deploy-connector.sh create scylla-source
   ./scripts/deploy-connector.sh create postgres-sink
   ```

5. **Validation** (Day 9-10)
   ```bash
   # Run benchmarks
   ./scripts/benchmark.sh --profile large

   # Run reconciliation
   ./scripts/reconcile.py full --all-tables
   ```

6. **Go-Live** (Day 11)
   ```bash
   # Enable production traffic
   # Monitor dashboards: http://grafana.example.com
   ```

## Production Support

- **Monitoring**: [Grafana Dashboards](http://grafana.example.com)
- **Alerts**: [AlertManager](http://alertmanager.example.com)
- **Logs**: [Log Aggregation](http://logs.example.com)
- **Runbook**: [docs/runbook.md](docs/runbook.md)
- **On-Call**: [PagerDuty/Opsgenie]