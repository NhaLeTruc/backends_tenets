#!/usr/bin/env bash
# Enforce Conventional Commits + provide a commit message template when missing.
set -euo pipefail

MSG_FILE="${1:-}"
[ -n "$MSG_FILE" ] || { echo "ERROR: commit-msg hook requires path to commit message file."; exit 1; }

# If the commit message is empty, write a helpful template and abort the commit so user can edit.
if [ ! -s "$MSG_FILE" ]; then
  cat > "$MSG_FILE" <<'TEMPLATE'
# Commit message template (Conventional Commits)
# Format:
#   type(scope?): short summary (max 72 chars)
#
#   A longer description of the change. Explain WHY the change was made,
#   and any important implementation notes. Wrap lines at ~72 chars.
#
#   Footer (optional): references, issue IDs, BREAKING CHANGE: description
#
# Examples:
#   feat(auth): add refresh token support
#
#   Fixes token refresh logic for expired sessions. Added tests and
#   updated docs.
#
#   Resolves: PROJ-123
TEMPLATE
  echo "ERROR: Empty commit message. A template was written to $MSG_FILE. Please edit and retry commit."
  exit 1
fi

# Load message into array
readarray -t LINES < "$MSG_FILE"
SUBJECT="${LINES[0]:-}"

trim() { printf "%s" "$1" | sed -E 's/^[[:space:]]+|[[:space:]]+$//g'; }
SUBJECT="$(trim "$SUBJECT")"

# Configuration
MAX_SUBJECT_LEN=72
MAX_BODY_LINE_LEN=100
ALLOWED_TYPES="feat|fix|docs|style|refactor|perf|test|chore|ci|build|revert"
CONVENTIONAL_REGEX="^(${ALLOWED_TYPES})(\\([a-z0-9._/-]+\\))?: [^ ].+"

fail() {
  echo "ERROR: $1"
  echo
  echo "Commit message must follow Conventional Commits:"
  echo "  <type>(optional-scope): <short subject>"
  echo "Example: feat(auth): add token refresh"
  exit 1
}

# Basic checks
if [ -z "$SUBJECT" ]; then
  fail "Empty commit subject."
fi

if echo "$SUBJECT" | grep -qEi '(^|[[:space:]]|:)(wip|work in progress|do not merge)([[:space:]]|$)'; then
  fail "WIP or temporary markers are not allowed in commit subject."
fi

if ! echo "$SUBJECT" | grep -qE "$CONVENTIONAL_REGEX"; then
  fail "Subject does not match conventional format. Expected: type(scope)?: subject"
fi

if [ "${#SUBJECT}" -gt "$MAX_SUBJECT_LEN" ]; then
  fail "Subject exceeds ${MAX_SUBJECT_LEN} characters (length=${#SUBJECT}). Keep it brief."
fi

if echo "$SUBJECT" | grep -qE '\.$'; then
  fail "Subject should not end with a period."
fi

# If there is a body, ensure one blank line between subject and body
if [ "${#LINES[@]}" -gt 1 ]; then
  SECOND_LINE="${LINES[1]}"
  if [ -n "$(trim "$SECOND_LINE")" ]; then
    fail "If providing a body, the second line must be blank (one blank line between subject and body)."
  fi
fi

# Body line length checks
if [ "${#LINES[@]}" -gt 2 ]; then
  for i in "${!LINES[@]}"; do
    if [ "$i" -le 1 ]; then continue; fi
    line="${LINES[$i]}"
    # ignore code blocks heuristic
    if echo "$line" | grep -qE '^[[:space:]]{4}|^```'; then
      continue
    fi
    if [ "${#line}" -gt "$MAX_BODY_LINE_LEN" ]; then
      fail "Body line $((i+1)) exceeds ${MAX_BODY_LINE_LEN} characters."
    fi
  done
fi

exit 0