# Step-by-step Guide — Setting up GitHub Rules (Best Practices)

Purpose: concrete, repeatable steps to configure repository rules, CI gates, security, and contributor workflows.

## 1. Prep: decide policy and owners

1. Define branch model (main/trunk, release branches, short-lived feature branches).
2. Define required checks (CI, linters, security scans, codecov).
3. Identify CODEOWNERS and team owners for areas of the repo.

## 2. Add repository files (make these first commits)

- Create `.github/` files to make rules discoverable and automatic:
  - `.github/CONTRIBUTING.md` — contributor workflow, testing commands, branch naming.
  - `.github/PULL_REQUEST_TEMPLATE.md` — PR motivation, testing, impact, rollback.
  - `.github/ISSUE_TEMPLATE/bug.md` and `feature_request.md`.
  - `.github/CODEOWNERS` — map paths to teams/people.
  - `SECURITY.md` — vulnerability reporting process.
  - `.github/workflows/ci.yml` — CI pipeline (unit tests, lint, build).

Example CODEOWNERS entry:

```
# filepath: .github/CODEOWNERS
# Owners for backend code
/src/backend/ @backend-team
# Owners for infra
/.github/ @devops-team
```

## 3. Enforce branch protections (UI or gh)

Required protections for `main` (or trunk):

- Require status checks to pass (CI workflow names).
- Require pull request reviews before merging (1-2 approvals).
- Dismiss stale approvals on push.
- Require linear history or allow merge commits based on policy.
- Require signed commits (commit signature verification) if desired.

UI: Repository → Settings → Branches → Add rule → configure above options.
CLI (example using gh api; replace owner/repo and checks):

```bash
# Example: require PR reviews via gh api (simplified)
gh api -X PUT repos/:owner/:repo/branches/main/protection -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"required_approving_review_count":1}' -F enforce_admins=true
```

## 4. Gate PRs with CI and status checks

1. Create CI workflows that expose consistent job names used in branch protection (e.g., `ci/build`, `ci/test`, `ci/lint`).
2. Configure branch protection to require those job names to succeed.
3. Enable GitHub Actions caching & matrix builds for speed and selective runs.

## 5. Automate dependency & security checks

- Enable Dependabot for dependency updates (.github/dependabot.yml).
- Enable GitHub Advanced Security features if available: Code scanning (CodeQL), secret scanning, and Dependabot alerts.
- Add CodeQL workflow: `.github/workflows/codeql.yml`

## 6. Secrets and environment protections

- Store secrets in repo settings or organization secrets: `Settings → Secrets and variables → Actions`.
- Use environment protections for deploy environments (required reviewers, wait timers).
CLI example to set a secret:

```bash
gh secret set MY_SECRET --body 'value' --repo owner/repo
```

## 7. Enforce commit & PR quality

- Enforce Conventional Commits or commit message rules via commit-msg hook (document in CONTRIBUTING.md).
- Use pre-commit hooks (pre-commit framework) and require them in CI:
  - `.pre-commit-config.yaml`
  - Add instructions to CONTRIBUTING.md: `pipx run pre-commit install`
- Optionally require signed commits in branch protection.

## 8. Access control & governance

- Use GitHub teams for permissions; grant least privilege.
- Configure CODEOWNERS to auto-request reviews for critical areas.
- Enforce 2FA at org level and review third-party app access.

## 9. PR lifecycle & automation

- Require PR template and enforce required fields using a bot or GitHub Actions check.
- Use automation for:
  - Labeling (stale, needs-triage)
  - Dependency PR handling (Dependabot)
  - Changelog generation on merge
- Configure merge strategy policy (squash, merge commit, rebase) and document in CONTRIBUTING.md.

## 10. Monitoring, metrics, and maintenance

- Monitor: CI duration, PR lead time, merge frequency, flaky tests.
- Regularly prune stale branches and update CODEOWNERS.
- Periodically review required checks to avoid excessive CI cost.

## 11. Rollout and communication

1. Announce the rules and rationale in team channels.
2. Provide a short "how-to" doc in repo root with quick commands and links.
3. Enforce via CI for 1–2 weeks while supporting the team (fixes, templates, examples).
4. Iterate based on feedback and metrics.

## Quick checklist (apply at repo creation)

- [ ] CONTRIBUTING.md present
- [ ] PULL_REQUEST_TEMPLATE.md present
- [ ] ISSUE_TEMPLATEs present
- [ ] CODEOWNERS configured
- [ ] CI workflows created and named
- [ ] Branch protection rule for main set and referencing CI job names
- [ ] Dependabot and CodeQL enabled
- [ ] Secrets stored in GitHub Secrets
- [ ] Team permissions and 2FA enforced
- [ ] Pre-commit hooks documented and recommended

Notes:

- Prefer automation (CI, bots) over manual enforcement.
- Start with a minimal, well-documented rule set and tighten over time.
- Use feature flags and trunk-safe practices to keep main deployable.
