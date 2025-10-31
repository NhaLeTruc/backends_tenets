# GitHub Rules & Policies — Beginner Guide

Purpose
- Provide a short, consistent set of rules for contributors to follow when working with our GitHub repositories.
- Improve code quality, collaboration velocity, and security.

Repository scope & ownership
- Each top-level folder or package should have an owner (team or individual) listed in CODEOWNERS.
- Owners are responsible for reviews, releases, and urgent fixes for their area.

Branching & trunk policy
- main (or trunk) must always be green and deployable.
- Short-lived branches: feature/<ticket>-short-desc, fix/<ticket>-short-desc, chore/<short-desc>.
- Rebase local branches frequently; prefer small incremental PRs.

Pull requests (PRs)
- Keep PRs small and focused — aim for <300 LOC when possible.
- Use the PR template: summary, motivation, testing steps, impact, rollback plan.
- Required checks: CI green, linters, security scan. Require at least one approval from a code owner.
- Use draft PRs for work in progress; convert to ready when tests and self-review pass.

Commit message standards
- Follow Conventional Commits: type(scope?): short summary
  - Examples: feat(auth): add refresh token; fix(api): handle nil user
- Keep subject ≤72 chars, blank line, then detailed body wrapped at ~72 chars.

Code review etiquette
- Review for behavior, tests, clarity, and potential regressions — not only style.
- Ask focused questions; request changes only for real concerns.
- Approve when you understand the change and tests pass.

CI / testing
- CI must run unit tests and critical integration checks for affected components.
- Locally run affected-only tests before pushing to reduce CI cost.
- Flaky tests should be fixed or quarantined — don't ignore failing tests.

Dependency & release policy
- Dependabot or similar automation for dependency updates; review and test all dependency bumps.
- Tag releases with semantic versioning where applicable and update CHANGELOG.md.

Security & secrets
- Never commit secrets or private keys. Use secret stores (GitHub Secrets, Vault).
- Enable branch protection rules and secret scanning.
- Report vulnerabilities via the repo SECURITY.md process.

Issue tracking & labels
- Use issue templates for bugs/feature requests.
- Standardize labels (bug, enhancement, docs, priority/1, needs-triage).
- Link PRs to issues when applicable.

Code formatting & linters
- Enforce formatting via pre-commit hooks and CI (black, prettier, eslint, etc.).
- Include .editorconfig to standardize editor behavior.

Access control & permissions
- Grant least-privilege access; use teams and role-based permissions.
- Use CODEOWNERS to automatically request reviews from relevant owners.

Contribution process & onboarding
- Provide CONTRIBUTING.md with setup steps, test commands, and local dev tips.
- New contributors should be guided to a “first-timers” issue or checklist.

Enforcement & exceptions
- Violations should be corrected via PRs and documented; repeated issues are escalated to maintainers.
- Exceptions allowed with explicit approval from repo owners and documented in PR or ISSUE.

Where to find help
- README.md / CONTRIBUTING.md / CODEOWNERS / SECURITY.md in the repo root.
- Team channel (e.g., #dev) for quick questions and coordination.

Keep this document minimal and update it as workflows evolve.// filepath: e:\_MyFile\_WORK\backends_tenets\Git\GitHub_Rules_and_Policies.md
