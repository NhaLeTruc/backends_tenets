# Speckit slash commands

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

1. /constitution - Establish project principles
2. /specify - Create specifications
3. /clarify - Clarify and de-risk specification (run before /plan)
4. /plan - Create implementation plan
5. /task - Generate actionable tasks
6. /analyze - Validate alignment & surface inconsistencies (read-only)
7. /implement - Execute implemenation
