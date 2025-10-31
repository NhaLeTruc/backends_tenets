#!/usr/bin/env bash
# Lightweight, practical pre-commit hook with common best-practice checks.
# Works by checking the staged version of files (not working tree).
set -euo pipefail

# Configuration
MAX_FILE_SIZE=$((5 * 1024 * 1024))   # 5 MB
TMPDIR="$(mktemp -d)"
FAIL=0

cleanup() {
  rm -rf "$TMPDIR"
}
trap cleanup EXIT

# Helper: get staged files (added/modified/copied)
mapfile -t STAGED < <(git diff --cached --name-only --diff-filter=ACM)

if [ "${#STAGED[@]}" -eq 0 ]; then
  exit 0
fi

# Utility: write staged content to tmp file preserving path
dump_staged() {
  local file="$1"
  local out="$TMPDIR/$file"
  mkdir -p "$(dirname "$out")"
  # Use git show to get staged content (':' prefix accesses index)
  if ! git show ":$file" > "$out" 2>/dev/null; then
    # binary or removed/unsupported; create empty placeholder
    : > "$out"
  fi
  echo "$out"
}

# Check functions
check_merge_markers() {
  local stagedfile="$1"; shift
  if grep -nE '^(<<<<<<< |>>>>>>> |=======$)' "$stagedfile" >/dev/null 2>&1; then
    echo "ERROR: Merge conflict markers found in staged file: $2"
    FAIL=1
  fi
}

check_trailing_whitespace() {
  local stagedfile="$1"; shift
  if grep -n --line-number -E '[[:space:]]$' "$stagedfile" >/dev/null 2>&1; then
    echo "ERROR: Trailing whitespace in staged file: $2"
    FAIL=1
  fi
}

check_large_file() {
  local file="$1"
  # size in bytes of staged object
  if git cat-file -s ":$file" >/dev/null 2>&1; then
    local size
    size=$(git cat-file -s ":$file")
    if [ "$size" -gt "$MAX_FILE_SIZE" ]; then
      echo "ERROR: Staged file too large (>$(($MAX_FILE_SIZE/1024/1024))MB): $file ($size bytes)"
      FAIL=1
    fi
  fi
}

check_basic_secrets() {
  local stagedfile="$1"; shift
  # Simple regexes for common tokens/keys (quick, not exhaustive). Adjust as needed.
  if grep -nE --line-number -I -E 'AKIA[0-9A-Z]{16}|aws_secret_access_key|-----BEGIN RSA PRIVATE KEY-----|eyJhbGciOiJI|ghp_[0-9A-Za-z]{36}|token[[:space:]]*[:=]' "$stagedfile" >/dev/null 2>&1; then
    echo "ERROR: Possible secret/key found in staged file: $2"
    FAIL=1
  fi
}

run_py_checks() {
  local tmp="$1"; shift
  local orig="$1"
  if command -v black >/dev/null 2>&1; then
    if ! black --check "$tmp" >/dev/null 2>&1; then
      echo "ERROR: black formatting issues in $orig (run 'black $orig' or stage formatted file)"
      FAIL=1
    fi
  fi
  if command -v flake8 >/dev/null 2>&1; then
    if ! flake8 "$tmp"; then
      echo "ERROR: flake8 issues in $orig"
      FAIL=1
    fi
  fi
  if command -v python >/dev/null 2>&1; then
    if python -m py_compile "$tmp" >/dev/null 2>&1; then
      :
    else
      echo "ERROR: Python syntax error in staged file: $orig"
      FAIL=1
    fi
  fi
}

run_js_checks() {
  local tmp="$1"; shift
  local orig="$1"
  if command -v npx >/dev/null 2>&1 && npx --no-install eslint --version >/dev/null 2>&1; then
    if ! npx --no-install eslint "$tmp" --no-eslintrc --env node >/dev/null 2>&1; then
      echo "ERROR: eslint issues in $orig"
      FAIL=1
    fi
  fi
}

# Iterate staged files and run checks (only basic filetype-based checks here)
for file in "${STAGED[@]}"; do
  # skip deleted files (shouldn't appear due to diff-filter)
  [ -f "$file" ] || true

  check_large_file "$file"

  tmpfile="$(dump_staged "$file")"

  # Basic content checks
  check_merge_markers "$tmpfile" "$file"
  check_trailing_whitespace "$tmpfile" "$file"
  check_basic_secrets "$tmpfile" "$file"

  case "${file##*.}" in
    py)
      run_py_checks "$tmpfile" "$file"
      ;;
    js|jsx|ts|tsx)
      run_js_checks "$tmpfile" "$file"
      ;;
    sh)
      if command -v shellcheck >/dev/null 2>&1; then
        if ! shellcheck "$tmpfile" >/dev/null 2>&1; then
          echo "ERROR: shellcheck issues in $file"
          FAIL=1
        fi
      fi
      ;;
    *)
      # no-op for other filetypes
      :
      ;;
  esac
done

if [ "$FAIL" -ne 0 ]; then
  echo
  echo "Pre-commit checks failed. Fix issues, stage changes, then retry commit."
  exit 1
fi

exit 0