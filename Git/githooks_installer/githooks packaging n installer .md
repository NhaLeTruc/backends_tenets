# .githooks packaging & installer

Purpose:
- Keep hooks versioned in the repo under `.githooks/`
- Provide a simple installer to enable them for all contributors

Quick setup:
1. Add your hook scripts to `.githooks/` (make them executable).
2. Run (POSIX):
   ./scripts/install-githooks.sh
   or on Windows (PowerShell):
   .\scripts\install-githooks.ps1

Notes:
- The installer sets `git config core.hooksPath .githooks`.
- Use `git config --unset core.hooksPath` to revert to default `.git/hooks`.
- For robust multi-language checks prefer a pre-commit framework (`pre-commit`) and run it from hooks.
- If some users cannot use `core.hooksPath`, installer supports copying hooks into `.git/hooks` as fallback (`--force-copy` or -ForceCopy).