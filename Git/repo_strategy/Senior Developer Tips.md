# Git: Tips to Use Like a Senior Developer

## Philosophy
- Keep history readable and useful. Prefer clarity over cleverness.
- Make small, testable changes. Ship often; revert easily.
- Protect shared branches with CI and branch protection policies.

## Essential configuration
- Use meaningful identity and signing:
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
  git config --global commit.gpgsign true
  ```
- Enable safer defaults:
  ```bash
  git config --global pull.rebase true
  git config --global rebase.autoStash true
  git config --global credential.helper manager-core   # Windows
  ```

## Commit practices
- Make atomic commits: one logical change per commit.
- Write clear commit messages:
  ```
  Short summary (50 chars)
  
  Brief explanation of *why*, not just *what*.
  ```
- Use `git add -p` to stage logically related hunks.
- Amend instead of new commits for local cleanup:
  ```bash
  git commit --amend --no-edit
  ```

## Branching and naming
- Keep branches short-lived (hours/days).
- Use clear names: `feature/auth-login`, `fix/timeout-escape`, `chore/deps`.
- Create a backup before risky history changes:
  ```bash
  git branch backup/feature-xxx
  ```

## PRs and code review
- Open PRs early; iterate in small increments.
- Use CI to gate merges; require passing checks.
- Add context to PR descriptions: motivation, testing, rollback plan.
- Use draft PRs for work-in-progress.

## Rebase vs merge
- Rebase local feature branches onto up-to-date main to keep history linear:
  ```bash
  git fetch origin
  git rebase origin/main
  ```
- Never rebase public/shared branches. Use `--force-with-lease` when pushing rewritten history:
  ```bash
  git push --force-with-lease origin feature/xxx
  ```

## Conflict resolution
- Resolve conflicts thoughtfully; run tests after resolution.
- Use `git mergetool` or modern IDE merge UI for complex conflicts.
- If overwhelmed, abort and reassess:
  ```bash
  git rebase --abort
  git merge --abort
  ```

## Inspecting history and debugging
- Use concise, visual logs:
  ```bash
  git log --graph --oneline --decorate --all
  ```
- Find when a bug was introduced:
  ```bash
  git bisect start
  git bisect bad
  git bisect good <commit>
  ```
- Recover lost commits via reflog:
  ```bash
  git reflog
  git checkout -b restore <reflog-commit>
  ```

## Cherry-pick and interactive rebase
- Extract specific changes:
  ```bash
  git cherry-pick <commit>
  ```
- Clean up commits before merging:
  ```bash
  git rebase -i HEAD~5
  ```

## Performance and maintenance
- Prune stale remote branches and fetch/cleanup regularly:
  ```bash
  git fetch --prune
  git remote prune origin
  ```
- Run GC occasionally in large repos:
  ```bash
  git gc --aggressive --prune=now
  ```

## Automation and hooks
- Use pre-commit hooks for linters/tests (`pre-commit` framework).
- Add helpful commit-msg checks (ticket ID, format).
- Automate changelog generation and release tagging.

## Useful aliases
```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.lg "log --graph --oneline --decorate --all"
```

## Collaboration etiquette
- Rebase interactively to tidy local work, but communicate history rewrites.
- Keep PRs small and focused. Link to issues and test plans.
- Respect CI and address flaky tests; do not merge flaky green builds.

## Advanced tips
- Use feature flags to decouple deploy and release.
- Consider `sparse-checkout` for very large monorepos.
- Be careful with submodules; prefer alternatives unless necessary.
- Use LFS for large binaries.

## Safety rules (never forget)
- Do not force-push to main or protected branches.
- Prefer `--force-with-lease` over `--force`.
- Backup before destructive operations:
  ```bash
  git branch safe-backup
  ```

## Quick checklist before merging
- Tests and linters pass.
- CI green and approvals met.
- Commit history clear and documented.
- Rollback plan exists (revert commit or tag).

Keep practices consistent across the team. Discipline + good tools = reliable delivery.