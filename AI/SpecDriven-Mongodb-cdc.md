# Spec Kit

## What is Spec-Driven Development?

Spec-Driven Development flips the script on traditional software development. For decades, code has been king — specifications were just scaffolding we built and discarded once the "real work" of coding began. Spec-Driven Development changes this: specifications become executable, directly generating working implementations rather than just guiding them.

## Get started

```bash

uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

specify init <PROJECT_NAME>
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd <PROJECT_NAME> && code .
# optional
specify check
```

## Constitution

Use the `/speckit.constitution` command to create your project's governing principles and development guidelines that will guide all subsequent development.

```bash
/speckit.constitution Create principles focused on Test Driven Development, clean easy to maintain code, robust architecture follow best practice design patterns, and enterprise-level production's capabilities of change data capture pipelines project.
```

## Specify

Use the `/speckit.specify` command to describe what you want to build. Focus on the what and why, not the tech stack.

```bash
/speckit.specify Create a change data capture pipeline from a MongoDB to a Delta-Lake lakehouse lives on MinIO server. The pipeline must has the following qualities:
1. Locally testable. Its docker compose environment enables e2e, and integration tests locally.
2. Production graded. It must be capable enough for enterprise's production deployment.
3. Observable. Its logs management systems and monitoring infrastructures must be enterprise's production level.
4. Strictly Tested. Tests must be written first before implementation for all of its components.
5. Robust. There must be proper enterprise level reconciliation mechanism, error handling, retry strategies, and stale events handling for the cdc pipeline.
6. Flexible. There must be proper handlings of schema evolutions, and dirty data.
7. Secured. There must be a proper authorization management system. In addition, safe-guards against SQL injection and other commom security vulnerabilities.
8. Centralized. There must be proper api server for managing the cdc pipeline.
9. Analytical ready. DuckDB must be able to query data in Delta-Lake lakehouse lives on MinIO server.
```

## Plan

Use the `/speckit.plan` command to provide your tech stack and architecture choices.

```bash
/speckit.plan The pipeline uses the latest stable version of MongoDB, Kafka, Kafka Connect, Debezium connectors, MinIO, FastAPI, Delta Lake, and DuckDB. 
1. Local testing must utilize docker compose. 
2. Mock data generation must utilizes best fit opensource tools. 
3. You MUST also choose opensource proven tools for linting, logging, monitoring, credentials vault, and other aspects of software development. 
4. You MUST utilize opensource proven tools AS MUCH AS POSSIBLE. 
5. Only choose custom built solution if there is NO AVAILABLE FREE TOOL.
6. DuckDB is the analytical tool for querying data in Delta Lake.
```

## Task and Implement

Use `/speckit.tasks` to create an actionable task list from your implementation plan.

```bash
/speckit.tasks
```

```txt
Create enforcing mechanism for first keeping all .md file except README.md and CLAUDE.md in a dedicated directory named "docs". Secondly, for NOT commiting any credential to github. Finally for all changes to be linted before committing.
```

Use `/speckit.implement` to execute all tasks and build your feature according to the plan.

```bash
/speckit.implement
```
