#!/usr/bin/env python3
"""
Client-side commit-msg git hook (Python 3).
Enforces a Conventional Commits style template + basic best-practice checks.

Install:
  - Save this file to .githooks/commit-msg
  - Make executable: chmod +x .githooks/commit-msg
  - Configure git to use it (optional): git config core.hooksPath .githooks
"""

from __future__ import annotations
import os
import re
import sys
import textwrap

# Configuration
MAX_SUBJECT_LEN = 72
MAX_BODY_LINE_LEN = 100
ALLOWED_TYPES = (
    "feat fix docs style refactor perf test chore ci build revert hotfix"
).split()
CONVENTIONAL_RE = re.compile(
    r"^(" + "|".join(ALLOWED_TYPES) + r")(\([a-z0-9._/-]+\))?:\s.+$", re.IGNORECASE
)

TEMPLATE = textwrap.dedent(
    """\
    # Commit message template (Conventional Commits)
    # Format: <type>(optional-scope): short summary
    # - type: one of: {types}
    # - scope: optional, lowercase, no spaces
    # - subject: brief summary, <= {max_subject} chars, no trailing period
    #
    # Blank line, then an optional body explaining WHY the change was made.
    # Wrap body lines at ~{max_body} chars.
    #
    # Examples:
    #   feat(auth): add refresh token support
    #
    #   Add server-side token refresh to avoid forcing re-login. Updated tests
    #   and docs.
    #
    #   Resolves: PROJ-123
    #
    """.format(
        types=", ".join(ALLOWED_TYPES), max_subject=MAX_SUBJECT_LEN, max_body=MAX_BODY_LINE_LEN
    )
)


def read_message(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_template_and_fail(path: str) -> None:
    # Prepend template so user can edit commit message in editor
    existing = ""
    if os.path.exists(path):
        existing = read_message(path)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(TEMPLATE)
        fh.write("\n")
        fh.write(existing)
    print(
        "ERROR: Empty commit message. A template was written to the commit message file.\n"
        "Please edit the message, follow the template, and try committing again."
    )
    sys.exit(1)


def first_non_comment_line(lines: list[str]) -> tuple[int, str] | tuple[None, None]:
    for idx, ln in enumerate(lines):
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        return idx, ln.rstrip("\n")
    return None, None


def validate_subject(subject: str) -> None:
    if len(subject) > MAX_SUBJECT_LEN:
        raise ValueError(f"Subject exceeds {MAX_SUBJECT_LEN} characters ({len(subject)}).")
    if subject.endswith("."):
        raise ValueError("Subject should not end with a period.")
    if not CONVENTIONAL_RE.match(subject):
        raise ValueError(
            "Subject does not match Conventional Commits format: "
            "<type>(optional-scope): short summary\n"
            f"Allowed types: {', '.join(ALLOWED_TYPES)}"
        )


def validate_body(lines: list[str], subj_idx: int) -> None:
    # If there are any non-comment lines after subject, require a blank line immediately after subject
    body_start_idx = subj_idx + 1
    # skip comment lines immediately after subject when determining layout
    if body_start_idx < len(lines) and lines[body_start_idx].strip().startswith("#"):
        # find first non-comment after subject
        i = body_start_idx
        while i < len(lines) and lines[i].strip().startswith("#"):
            i += 1
        body_start_idx = i

    if body_start_idx < len(lines):
        # check second line is blank (allow comments)
        second_line = lines[subj_idx + 1] if subj_idx + 1 < len(lines) else ""
        if second_line.strip() != "":
            raise ValueError("When including a body, the second line must be blank (one blank line between subject and body).")

    # Check body line lengths (skip commented lines and code blocks heuristic)
    in_code_block = False
    for i in range(subj_idx + 2, len(lines)):
        ln = lines[i].rstrip("\n")
        stripped = ln.lstrip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if ln.strip().startswith("#"):
            continue
        if len(ln) > MAX_BODY_LINE_LEN:
            raise ValueError(f"Body line {i+1} exceeds {MAX_BODY_LINE_LEN} characters.")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: commit-msg <path-to-commit-msg-file>", file=sys.stderr)
        sys.exit(2)

    msg_file = sys.argv[1]
    if not os.path.exists(msg_file):
        print(f"ERROR: Commit message file not found: {msg_file}", file=sys.stderr)
        sys.exit(2)

    content = read_message(msg_file)
    if not content.strip():
        write_template_and_fail(msg_file)

    lines = content.splitlines()
    subj_idx, subject = first_non_comment_line(lines)
    if subj_idx is None:
        write_template_and_fail(msg_file)

    subject = subject.strip()
    try:
        validate_subject(subject)
        validate_body(lines, subj_idx)
    except ValueError as exc:
        print("ERROR: Invalid commit message:")
        print(f"  {exc}")
        print("\nTip: Follow the Conventional Commits format. Example:")
        print("  feat(auth): add token refresh")
        print("\nFor an editable template the hook will leave in the commit message file when empty.")
        sys.exit(1)

    # All checks passed
    sys.exit(0)


if __name__ == "__main__":
    main()