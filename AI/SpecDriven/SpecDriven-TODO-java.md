# Spec Kit

## What is Spec-Driven Development?

Spec-Driven Development flips the script on traditional software development. For decades, code has been king — specifications were just scaffolding we built and discarded once the "real work" of coding began. Spec-Driven Development changes this: specifications become executable, directly generating working implementations rather than just guiding them.

## Get started

```bash

uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

specify init todo-pg-java
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd todo-pg-java && code .
# optional
specify check
```

## Constitution

Use the `/speckit.constitution` command to create your project's governing principles and development guidelines that will guide all subsequent development.

```bash
/speckit.constitution Create principles focused on clean easy to maintain code, hybrid testing - Core logic uses TDD, integration tests written after, and robust architecture following best practices of 15-Factor App methodology for a TODOs list application. Make sure the constitution technology agnostic and devoid of specificalities, only principles.
```

## Specify

Use the `/speckit.specify` command to describe what you want to build. Focus on the what and why, not the tech stack.

```bash
/speckit.specify Create a TODOs list application that has the following qualities:
1. Locally testable. Its docker compose environment MUST enables extensive tests locally.
2. Communities supported. It MUST utilize free open-sourced softwares, and minimum amount of custom code.
3. Full-stacked. It Must include solutions for frontend, backend, API, and other components of a full-stacked application.
4. 15-Factor App methodology approved. It MUST delivers on all 15-principles for building robust modern applications.
```

## Plan

Use the `/speckit.plan` command to provide your tech stack and architecture choices.

```bash
/speckit.plan Choose the most battle-proven open-source or free tech stack and architecture that meet the TODOs list application specs and constitution.
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
/speckit.implement
```
