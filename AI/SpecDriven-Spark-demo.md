# Generate Speckit project

Start the project:

```bash
# If not installed
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

specify init spark-demos
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd spark-demos && code .
# optional
specify check
```

```txt
You're a world-class excellent software engineer with 20 years experiences in databases administration; backends systems design; data ETL; and distributed computing. You're building an application that can handle skew, dirty, untabulated, and without constraints data in both batch and stream mode; before insert/update into a local datawarehouse. Use the `/speckit.constitution` command to create your project's governing principles and development guidelines that will guide all subsequent development.
```

```txt
Use the `/speckit.specify` command to describe what you want to build for this application. Focus on the what and why, not the tech stack. You MUST take into account handling impossible to normalized or constrained data records.
```

```txt
Use the `/speckit.plan` command to provide your open-sourced tech stack and architecture choices for this application. You MUST choose latest stable versions, and include local testing tools. If it is advisable use Spark for batch mode and Spark Streaming for streaming mode.
```

```bash
/speckit.tasks
```

```bash
/speckit.implement
```
