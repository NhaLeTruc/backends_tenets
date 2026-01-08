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
/speckit.constitution Create principles focused on clean well tested code, and data quality assurance for a full local demonstration of all common change data capture approaches for major opensource data storages like Postgres, MySQL, DeltaLake, MinIO, and Iceberg.
```

## Specify

Use the `/speckit.specify` command to describe what you want to build. Focus on the what and why, not the tech stack.

```bash
/speckit.specify Build a change data capture demo project for common open-source data storage solutions.
The project should have these qualities:

1. Included with CDC approaches of data storage solutions like Postgres, MySQL, DeltaLake, and Iceberg.
2. Demonstrates all common CDC approaches of each data storage solution.
3. Utilizes only open-source or free tools.
4. Is fully localized using containerization technologies.
5. Generates its own mock data for testing. No real datasouce is needed.
6. Follow TDD strictly. Write test before implementations.
7. Follow document as code priciples strictly.
```

## Clarify

Clarify and de-risk specification (run before /plan)

```bash
/speckit.clarify
```

## Plan

Use the `/speckit.plan` command to provide your tech stack and architecture choices.

```bash
/speckit.plan The CDC demo project MUST use open source tools like Debezium, Kafka Connect, and native tools built into Postgres, MySQL, DeltaLake, and Iceberg. Pick optimal open-source or free tools for other aspects like testing, project managment, CICD, etc.
```

## Task and Implement

Use `/speckit.tasks` to create an actionable task list from your implementation plan.

```bash
/speckit.tasks
```

Validate alignment & surface inconsistencies (read-only)

```bash
/speckit.analyze
```

Use `/speckit.implement` to execute all tasks and build your feature according to the plan.

```bash
/speckit.implement
```
