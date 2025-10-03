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
specify check

```

## Constitution

Use the `/constitution` command to create your project's governing principles and development guidelines that will guide all subsequent development.

```prompt
/constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements for a extracts, transforms, and loads application
```

or click on `constitution.md`, then open vscode's chat window and pick your AI agent. Prompt it to:

```prompt
Fill the constitution with the principles focused on code quality, testing standards, user experience consistency, and performance requirements for a extracts, transforms, and loads application based on the template.
```

## Specify

Use the `/specify` command to describe what you want to build. Focus on the what and why, not the tech stack.

```prompt
/specify Build an application that can help me extracts, transforms, loads data from and to sources or sinks like kafka, postgres, mysql, and amazon S3. All code should be unit and integration tested. Any test data should be mocked - you do not need to pull anything from any real sources.
```

## Plan

Use the `/plan` command to provide your tech stack and architecture choices.

```prompt
/plan The application uses Apache Spark version 3.5.6, Java version 11, and Gradle Build Tool version 7.6.5, with minimal number of libraries. Dependency injection should be the guiding principle for code structure. There should be reusable extracts, transforms, and loads modules for each sources or sinks. Extracted or transformed data which is loaded into amazon S3 should be saved as parquet files. Unit tests should be written for coverage of all extracts, transforms, and loads modules. Unit test should be written utilizing the ScalaTest testing framework for Scala.
```

## Task and Implement

Use `/tasks` to create an actionable task list from your implementation plan.

```bash
/tasks
```

Use `/implement` to execute all tasks and build your feature according to the plan.

```bash
/implement
```
