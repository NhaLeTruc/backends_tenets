# Generate Speckit project

Start the project:

```bash
# If not installed
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

specify init olap-demos
# Choose AI agent and cmd script type to boostrap your project.
# Open project directory, which was created last step, in vscode.
cd olap-demos && code .
# optional
specify check
```

```txt
You're a world-class excellent software engineer with 20 years experiences in databases administration; backends systems design; data ETL; and distributed computing. You're building a OLAP's core capabilities tech demo. Use the `/speckit.constitution` command to create your project's governing principles and development guidelines that will guide all subsequent development.
```

```txt
Use the `/speckit.specify` command to describe what you want to build for the OLAP's core capabilities tech demo. Focus on the what and why, not the tech stack.
```

```txt
Use the `/speckit.plan` command to provide your tech stack and architecture choices for the OLAP's core capabilities tech demo. Make sure to include local testing tools. YOU MUST USE JAVA for the CORE of the codebase, other languages can be included for supporting roles which they excel at.
```

```bash
/speckit.tasks
```

```bash
/speckit.implement
```
