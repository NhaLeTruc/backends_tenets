#!/usr/bin/env bash
# Simple installer to enable in-repo .githooks directory via core.hooksPath
# Usage: ./scripts/install-githooks.sh [--force-copy]  (run from repo root)
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo '.')"
HOOKS_DIR=".githooks"
FORCE_COPY=0

for arg in "$@"; do
  case "$arg" in
    --force-copy) FORCE_COPY=1 ;;
    -h|--help)
      cat <<EOF
Install .githooks into this repo:

  ./scripts/install-githooks.sh        # set core.hooksPath to .githooks
  ./scripts/install-githooks.sh --force-copy
                                       # also copy hooks to .git/hooks (fallback for older Git)

To uninstall:
  git config --unset core.hooksPath

EOF
      exit 0
    ;;
  esac
done

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "ERROR: not a git repository (run from inside a git repo)"
  exit 1
fi

cd "$REPO_ROOT"

if [ ! -d "$HOOKS_DIR" ]; then
  echo "ERROR: $HOOKS_DIR not found. Create the directory and add hooks first."
  exit 2
fi

# Make hook scripts executable
echo "Making hooks executable under $HOOKS_DIR..."
find "$HOOKS_DIR" -type f -exec chmod +x {} \; || true

# Configure git to use the hooks path
echo "Setting git config core.hooksPath to $HOOKS_DIR"
git config core.hooksPath "$HOOKS_DIR"

# Optional: copy to .git/hooks as fallback (useful for some older clients)
if [ "$FORCE_COPY" -eq 1 ]; then
  echo "Copying hooks to .git/hooks as fallback..."
  mkdir -p .git/hooks
  cp -f "$HOOKS_DIR"/* .git/hooks/ || true
  find .git/hooks -type f -exec chmod +x {} \; || true
fi

echo "Installed .githooks successfully. To uninstall: git config --unset core.hooksPath"