# Spec Kit

## What is Spec-Driven Development?

Spec-Driven Development flips the script on traditional software development. For decades, code has been king — specifications were just scaffolding we built and discarded once the "real work" of coding began. Spec-Driven Development changes this: specifications become executable, directly generating working implementations rather than just guiding them.

## Get started

```bash

uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

specify init scylla-pg-cdc
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd scylla-pg-cdc && code .
# optional
specify check
```

## Constitution

Use the `/speckit.constitution` command to create your project's governing principles and development guidelines that will guide all subsequent development.

```bash
/speckit.constitution Create principles focused on clean easy to maintain code, hybrid testing - Core logic uses TDD, integration tests written after, and robust architecture following best practices of change data capture pipelines projects specifically and software development generally.
```

## Specify

Use the `/speckit.specify` command to describe what you want to build. Focus on the what and why, not the tech stack.

```bash
/speckit.specify Create a change data capture pipeline from a ScyllaDB to a Postgres data-warehouse. The pipeline MUST has the following qualities:
1. Locally testable. Its docker compose environment MUST enables e2e, and integration tests locally.
2. Communities supported. It MUST utilize free open-sourced softwares, and minimum amount of custom code.
3. Observable. There MUST BE proper logs management systems and monitoring infrastructures.
4. Strictly Tested. Tests MUST be written first before implementation for all of its components.
5. Robust. There MUST be proper reconciliation mechanism, error handling, retry strategies, and stale events handling for the cdc pipeline.
6. Flexible. There MUST be proper handlings of schema evolutions, and dirty data.
7. Secured. There MUST be a proper safe-guards against SQL injection and other commom security vulnerabilities.
8. Hybrid testing. Core logic uses TDD, integration tests written after the main codebase has been completely implemented.
```

## Plan

Use the `/speckit.plan` command to provide your tech stack and architecture choices.

```bash
/speckit.plan First, the pipeline must uses the latest stable version of these softwares:
1. Scylla CDC Source Connector from Confluent Hub.
2. PostgreSQL Sink JDBC Connector from Confluent Hub.
3. Kafka, Kafka Schema Registry, and Kafka Connect.
4. Scylla Database.
5. Postgres Database.
6. Prometheus, Grafana, and Jaeger.
7. HashiCorp Vault.
8. Other proven open-sourced tools.
Second, developers must be able to manage the pipeline through well-documented Bash. Shell, or Python commands, scripts, and guidances. There is NO NEED for a centralized management API.
Third, the reconciliation feature NEED to be both schedulable and triggred on demand.
Finally, ALL users and passwords MUST be managed through proper vault solution. There is NO NEED for more advanced authorization systems.
```

## Task and Implement

Use `/speckit.tasks` to create an actionable task list from your implementation plan.

```bash
/speckit.tasks

/speckit.analyze
```

```txt
Create enforcing mechanism for first keeping all .md file except README.md and CLAUDE.md in a dedicated directory named "docs". Secondly, for NOT commiting any credential to github. Finally for all changes to be linted before committing.
```

Use `/speckit.implement` to execute all tasks and build your feature according to the plan.

```bash
/speckit.implement You MUST IMPLEMENT ALL PHASE 1 TASKS. NO TODO COMMENTS, PLACEHOLDERS, OR STUBS IMPLEMENATIONS.
```
