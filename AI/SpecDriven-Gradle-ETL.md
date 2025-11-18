# Generate Speckit project

```bash
specify init <PROJECT_NAME>
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd <PROJECT_NAME> && code .
```

```bash
/speckit.constitution Create principles focused on clean and SOLID code, comprehensive testing standards, data quality assurance, and big data performance requirements for an ETL pipeline application.
```

```bash
/speckit.specify Build an application that can help contructing pipeline of different collections of steps including but not limited to extracts, transforms, validates, and loads data from and to sources or sinks like kafka, postgres, mysql, deltalake, and amazon S3. Users must be able to create these pipelines using JSON files ONLY containing non-sensitve credential parameters. All code must be unit tested. The project must includes a docker compose environment for local integration tests. Any test data must be mocked - you do not need to pull anything from any real sources. The application must process these qualities:

1. The core entities are: Pipeline, PipelineStep, PipelineContext, ExtractMethods, LoadMethods, UserMethods, JdbcConfig, IAMConfig, and OtherConfig.
2. Users are able to create customized Pipelines with different collections of PipelineStep entities using different JSON config files containing non-credential parameters.
3. Each Pipeline entity ONLY needs ONE JSON config file to be instantiated. But this JSON config file can references other JSON files for additional configs.
4. The Pipeline entity is responsible for parsing JSON config files containing non-credential parameters to create its collection of PipelineStep entities.
5. The Pipeline entity must have a "main" method which execute its collection of PipelineStep entities.
6. You must utilizes the Chain of Responsibility pattern to implement the relationship between PipelineStep entities. 
7. Data format between PipelineStep entities must be Spark DataFrame, which each PipelineStep could receive and output multiple instances of; utilizing the PipelineContext entity.
8. Each PipelineStep instance employs one static method imported from ExtractMethods, LoadMethods, or UserMethods entity. 
9. The ExtractMethods entity contains static methods which help extracting data from sources.
10. The LoadMethods entity contains static methods which help loading data to sinks.
11. ExtractMethods and LoadMethods static methods employ the uses of JdbcConfig, IAMConfig, and OtherConfig entities in fetching credentials from Vault.
12. JdbcConfig is responsible for Postgres and MySQL crendential config objects.
13. IAMConfig is responsible for S3 crendential config objects.
14. OtherConfig is responsible for kafka and DeltaLake crendential config objects.
16. Sensitive credential parameters must be stored in a vault solution which can be tested locally using the docker compose environment. The credentials must be populated into the Vault solution using a git-ignored ".env" file, which you can create an example named ".env.example".
17. You must pick an optimal design pattern for implementing JdbcConfig, IAMConfig, and OtherConfig entities.
18. The UserMethods entity contains user defined methods which help transforming or validating data by utilizing Apache Spark packaged libraries. For testing purposes, you only need to create 5 common usecase methods for each type.
19. Execution models includes batch utilizes Spark, and micro-batch utilizes Spark Streaming.
20. Metrics exposure must be logs only.
21. Expected batch throughput/data volume targets are 100K records/sec (simple), 10K records/sec (complex). And for streaming is 5s p95 latency, 50K events/sec throughput.
22. Each pipeline must be retried at most 3 times after a delay of 5 seconds.
23. The application can be executed by both CLI commands and spark clusters' spark submit tool. 
```

```bash
/speckit.plan The application must uses Apache Spark version 3.5.6, Scala version 2.12, and a compatible version of Gradle, with minimal number of libraries.
```

```bash
/speckit.tasks
```

```bash
/speckit.implement
```
