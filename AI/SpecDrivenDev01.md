# Revised Prompt for Spark App

```bash
specify init <PROJECT_NAME>
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd <PROJECT_NAME> && code .
```

```prompt
/constitution Create principles focused on clean and SOLID code, testing standards for both unit tests and integration test, data quality assurance, and big data performance requirements for an extracts, transforms, and loads application.
```

```prompt
/specify Build an application that can help me extracts, transforms, loads data from and to sources or sinks like kafka, postgres, mysql, and amazon S3. All code must be unit tested and integration tested. Any test data must be mocked - you do not need to pull anything from any real sources. The application must process these qualities:

1. The core codebase must utilizes design patterns like strategy, factory, or singleton wherever applicable.
2. The core codebase must be clean and follow the "SOLID" principles.
3. The core codebase must be built around a "pipeline" object for creating customizable pipeline implementations. Following the strategy design pattern, "pipeline" must has its own interface with a "run" function for the pipeline's instantiation.
4. Each "pipeline" composes multiple functional steps of extracts, transforms, and loads. You must build these functional steps modules strictly following the functional programming paradigm.
5. These pipeline objects must be built so that they can be individually submitted to spark cluster's spark-submit tool for execution.
6. Data format between pipeline stages must be avro. Data schemas for validation must be stored in JSON and organized separately in a dedicated module.
7. Configurations classes must be written in Scala. Customizable config variables must be stored in JSON format and organized separately in a dedicated module.
8. Functional transformations types are aggregations, joins, and windowing. You only need to write one transformation function per type for testing purposes. Structure the transformation module for easy expansion later.
9. Write modes must provide options such as append, overwrite, and upsert for user to specify in each loads function.
10. Execution models includes batch utilizes Spark, and streaming utilizes Spark Streaming.
11. Metrics exposure must be logs only.
12. Expected batch throughput/data volume targets are 100K records/sec (simple), 10K records/sec (complex). And for streaming is 5s p95 latency, 50K events/sec throughput.
13. Each pipeline must be retried at most 3 times after a delay of 5 seconds.
14. Credential must be stored in a simple vault solution which can be tested locally.
```

```prompt
/plan The application uses Apache Spark version 3.5.6, Java version 11, Scala version 2.12, and a compatible version of Simple Build Tool or SBT, with minimal number of libraries. You must follow these three principle closely:
1. The Strategy design pattern must be the guiding principle for the central pipeline object and other object oriented entities.
2. The functional programming paradigm must be the guiding principle for building reusable and as customizable as possible data extracts, and loads functions for each sources and sinks. 
3. Unit tests must be written for coverage of all core components.
```

```bash
/speckit.tasks
```

```bash
/speckit.implement
```
