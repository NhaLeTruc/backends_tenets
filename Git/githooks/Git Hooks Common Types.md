# Git Hooks — Types and Subtypes (Concise Reference)

## Overview
Git hooks are scripts executed by Git on certain events. Hooks live in `.git/hooks` or a custom `core.hooksPath`. Hooks can be client-side (run on a developer machine) or server-side (run on the Git server). Hooks exit non‑zero to abort the associated Git operation.

---

## Client-side hooks
Run during user actions (quality gates, formatting, local checks).

- applypatch-msg
  - When: after `git apply --cached` (patch applied by git-am/apply-mailbox).
  - Input: commit message file path.
  - Use: validate imported patch message.

- pre-applypatch
  - When: before applying a patch.
  - Use: prepare environment or run checks.

- post-applypatch
  - When: after applying patch.
  - Use: cleanup, notifications.

- pre-commit
  - When: before creating a commit object.
  - Use: run linters, unit tests, prevent bad commits. Should operate on staged content.

- prepare-commit-msg
  - When: before the commit message editor opens (or auto-generated message is created).
  - Input: path to message file, commit source, SHA (optional).
  - Use: prefill/modify commit message templates.

- commit-msg
  - When: after message is prepared, before commit is finalized.
  - Input: path to commit message file.
  - Use: enforce commit message format (Conventional Commits, ticket IDs).

- post-commit
  - When: after commit is recorded.
  - Use: local notifications, CI triggers, logging.

- pre-rebase
  - When: before rebase starts.
  - Input: interactive flag possibility.
  - Use: prevent rebases on protected branches, run checks.

- post-rewrite
  - When: after `git commit --amend` or `git rebase` rewrites history.
  - Input: receives rewritten refs via arguments.
  - Use: update external systems, notify CI, clean refs.

- post-checkout
  - When: after `git checkout` (branch/commit change).
  - Args: previous ref, new ref, checkout type (branch/commit).
  - Use: rebuild artifacts, update dev environment.

- post-merge
  - When: after a successful merge.
  - Use: run migrations, rebuild, run integration tests locally.

- pre-push
  - When: before `git push` sends refs to remote.
  - Input: remote name, URL; reads stdin lines "local_ref local_sha remote_ref remote_sha".
  - Use: run tests for affected modules, prevent sensitive pushes.

- pre-auto-gc
  - When: before automatic `git gc`.
  - Use: conditionally disable gc or perform maintenance.

---

## Server-side hooks
Run on the remote repository to enforce policies and trigger workflows.

- pre-receive
  - When: before refs are updated on the server (on `git push`).
  - Input: stdin lines "oldrev newrev refname".
  - Use: reject pushes violating policies (branch protection, size limits, forbidden file patterns).

- update
  - When: once per ref pushed (called with refname, oldrev, newrev).
  - Use: per-ref validation, fine-grained access control (can reject a single ref).

- post-receive
  - When: after all refs updated.
  - Input: same stdin as pre-receive.
  - Use: CI triggers, notifications, deploys, update mirrors.

- post-update
  - When: after refs updated (simpler than post-receive; receives refnames as args).
  - Use: update server-side cache, hooks for dumb HTTP servers.

- reference-transaction (less common)
  - When: on transactional ref updates.
  - Use: complex server workflows, transactional integrity.

- push-to-checkout (rare)
  - When: used by repositories configured to update working tree on push.
  - Use: perform actions when pushing to a checked-out branch on a bare/checked-out repository.

---

## Hook input/output and behavior notes
- Hooks run with repository root as CWD.
- Input conventions:
  - commit-msg/prepare-commit-msg: message file path argument.
  - pre-push: remote name & url as args; refs on stdin.
  - pre-receive/post-receive: refs on stdin ("old new ref").
  - update: three args (refname, oldrev, newrev).
- Exit code: `0` = success; non-zero = abort operation (client or server behavior).
- Hooks should be fast and deterministic; long tasks should delegate to background workers via events.

---

## Best practices
- Keep hooks small and focused (lint, tests, message checks).
- Operate on staged content (use `git show :path` or `git diff --cached`).
- Avoid heavy operations in blocking hooks; prefer post-receive webhooks for async work.
- Use `--no-verify` cautiously (bypasses client hooks).
- Version hooks in repo (e.g., `.githooks/`) and set `git config core.hooksPath .githooks`.
- Provide helpful failure messages and remediation steps.
- Log server-side hook rejections with reason and who to contact.
- Test hooks across OSes used by the team (Windows, macOS, Linux).

---

## Common uses by teams
- Pre-commit / pre-push: run linters, unit tests, secret checks.
- Commit-msg: enforce message templates and ticket references.
- Pre-receive/update: enforce branch protection, prevent direct pushes to protected branches.
- Post-receive: trigger CI/CD pipelines, update dashboards, notify channels.

---

## References
- Official Git hooks documentation: https://git-scm.com/docs/githooks
