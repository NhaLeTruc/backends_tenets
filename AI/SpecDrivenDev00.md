# Generate DBT project

Start the project:

```bash
specify init <PROJECT_NAME>
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd <PROJECT_NAME> && code .
# optional
specify check
```

```prompt
/speckit.constitution Create principles focused on well tested code, and data quality assurance for a data build tool (dbt) project that can serve as a full demo of dbt's capabilities.
```

```prompt
/speckit.specify Build a full demo dbt application which interacts with a mock data warehouse. All code must be tested. Any test data must be mocked - you do not need to pull anything from any real sources. Assume most common usecases for this dbt application.
```

```prompt
/speckit.plan The application uses the latest version of dbt with minimal number of libraries. You must follow these three principle closely:
1. All core code components must be tested and commented for readability.
2. A local docker compose test environment must be created for testing. This environment must contain a Postgres database for storing mock data which the dbt application interact with during testing.
3. A Minio service must be included in the local docker compose test environment, but must remain untouched by the dbt application.
```

```bash
/speckit.tasks
```

```bash
/speckit.implement
```
