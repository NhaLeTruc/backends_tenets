#!/usr/bin/env bash
# Minimal example pre-commit hook: run linters on staged files
#
# This file is an example; replace with your real checks (pre-commit, etc.)
set -euo pipefail

STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|ts|sh)$' || true)
if [ -z "$STAGED" ]; then
  exit 0
fi

echo "Running quick linters on staged files..."
for f in $STAGED; do
  case "$f" in
    *.py)
      command -v black >/dev/null && black --check "$f" || true
      command -v flake8 >/dev/null && flake8 "$f" || true
      ;;
    *.sh)
      command -v shellcheck >/dev/null && shellcheck "$f" || true
      ;;
    *.js|*.ts)
      command -v npx >/dev/null && npx --no-install eslint "$f" || true
      ;;
  esac
done

# Exit 0 to allow commit (make checks advisory) or non-zero to block commit
exit 0