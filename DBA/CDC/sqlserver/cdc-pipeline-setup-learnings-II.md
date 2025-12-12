# CDC Pipeline Setup Learnings II

This document captures important issues, troubleshooting steps, and learnings from setting up and operating the SQL Server to PostgreSQL CDC pipeline.

## PostgreSQL Exporter Issues

### Issue: postgres-exporter Service Unhealthy (Dec 2025)

**Symptoms:**
- `cdc-postgres-exporter` container shows status: `unhealthy`
- Health check returns HTTP 500 Internal Server Error
- Metrics endpoint at http://localhost:9187/metrics fails

**Root Causes:**

1. **Missing `pg_stat_statements` Extension**
   - Error in logs: `pg_stat_statements pq: relation "pg_stat_statements" does not exist`
   - The custom queries configuration (docker/configs/prometheus/postgres-exporter-queries.yaml) includes a query that requires the `pg_stat_statements` extension
   - This extension must be loaded via `shared_preload_libraries` configuration parameter

2. **Metric Description Conflicts**
   - postgres_exporter has built-in collectors for `pg_stat_user_tables`
   - Custom queries with the same metric names but different descriptions cause conflicts
   - Error: `has help "Number of sequential scans initiated on this table" but should have "Number of sequential scans"`

**Resolution:**

1. **Enable `pg_stat_statements` in PostgreSQL** (docker/docker-compose.yml):
   ```yaml
   postgres:
     command: >
       postgres
       -c shared_preload_libraries=pg_stat_statements
       -c pg_stat_statements.track=all
       -c pg_stat_statements.max=10000
   ```

2. **Install the extension in the database**:
   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
   ```

3. **Remove conflicting custom queries**:
   - Removed `pg_stat_user_tables` from the custom queries file since it conflicts with built-in collector
   - The built-in collector already provides these metrics with proper descriptions

4. **Restart services**:
   ```bash
   docker compose stop postgres && docker compose rm -f postgres && docker compose up -d postgres
   docker restart cdc-postgres-exporter
   ```

**Prevention:**
- When using postgres_exporter with custom queries, check for conflicts with built-in collectors
- Always configure required PostgreSQL extensions via `shared_preload_libraries` before creating the extension
- Monitor health checks during initial setup to catch configuration issues early

**References:**
- [PostgreSQL pg_stat_statements documentation](https://www.postgresql.org/docs/current/pgstatstatements.html)
- [postgres_exporter built-in collectors](https://github.com/prometheus-community/postgres_exporter#built-in-collectors)

---

## Future Learnings

Additional issues and learnings will be documented here as they are discovered.
