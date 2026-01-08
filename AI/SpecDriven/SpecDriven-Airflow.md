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
/speckit.constitution Create principles focused on clean well tested code, and data quality assurance for a Apache Airflow project that can serves as a full demo of Apache Airflow's ETL capabilities.
```

## Specify

Use the `/speckit.specify` command to describe what you want to build. Focus on the what and why, not the tech stack.

```bash
/speckit.specify Build a full demo Apache Airflow ETL application which interacts with a mock data warehouse. All code must be tested. Any test data must be mocked - you do not need to pull anything from any real sources. You can assume most common ETL usecases for this Airflow application. Additionally, It must also has these very important qualities:

1. Able to dynamically generate DAGs using JSON configuration files.
2. Able to handle retry, interruption, failure, and error of Airflow DAGs.
3. Has custom operators for submitting Spark artifacts to different Spark clusters e.g. standalone, YARN, and Kubernetes for execution.
4. Has custom operators for sending text messages to different channels e.g. email, MS Teams, and telegram, which can be triggered by events or results of other operators in the Airflow DAG.
5. Has at least 12 examples of DAGs demonstrating typical to advanced Airflow's ETL workloads.
6. Has a docker compose local environment for integration tests.

Finally, you need to suggest a CICD solution for verifying, building, testing, and deploying DAGs using JSON files. If such solution can be achieved in production using Github Actions then implement it, else create a .md file with your suggestions fully explained.
```

## Plan

Use the `/speckit.plan` command to provide your tech stack and architecture choices.

```bash
/speckit.plan The application uses the latest stable version of Apache Airflow with minimal number of libraries, and Postgres for the mock data warehouse. Please also picks optimal free tools for project management tasks like: build automation, dependency management, packaging, linting, and testing.
```

## Task and Implement

Use `/speckit.tasks` to create an actionable task list from your implementation plan.

```bash
/speckit.tasks
```

Use `/speckit.implement` to execute all tasks and build your feature according to the plan.

```bash
/speckit.implement
```
