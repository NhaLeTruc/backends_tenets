# Organizational GitHub Policies — Data Engineering Team

## Purpose

Provide concise, enforceable GitHub policies and recommended rules for the Data Engineering organization to ensure safe, auditable, and efficient collaboration.

## Scope

Applies to all repositories owned by the Data Engineering org, including ETL jobs, pipeline configs, data libraries, infra-as-code, and monitoring/playbooks.

1. **Ownership & Repository Classification**
   - Classify repos: app/service, library, infra, dataset-metadata, docs.
   - Maintain `CODEOWNERS` per repo root; map directories to responsible teams/individuals.
   - Owners are accountable for reviews, security triage, and release approvals.

2. **Branching & Trunk Policy**
   - main (or trunk) must be deployable at all times.
   - Short-lived feature branches: `feature/PROJ-123-description`, bugfix: `fix/PROJ-123`.
   - Require rebasing or merging up-to-date main before merge; prefer small, incremental PRs.

3. **Pull Request Requirements**
   - Use PR template (motivation, data impact, testing plan, rollback steps, dataset contracts).
   - Require CI green, at least one code-owner approval, and one data-owner approval for schema or pipeline changes.
   - Enforce draft PRs for WIP and large refactors.

4. **CI / Test Gates**
   - CI must include: lint, unit tests, integration tests (local pipeline runner or emulator), schema validation, and data contract checks.
   - Implement affected-only `builds/tests` to limit CI cost.
   - Fail fast on schema or contract breaks.

5. **Data Governance & Schema Changes**
   - All `schema/table/contract` changes must include migration plan and backwards-compatible steps.
   - Use changelog and migration PR checklist: add migration script, update downstream consumers, and schedule rollout windows for breaking changes.
   - Require data-owner sign-off for production dataset changes.

6. **Secrets, Credentials & Sensitive Data**
   - Never store secrets, credentials, or sample PII in Git. Use GitHub Secrets, HashiCorp Vault, or cloud secret stores.
   - Enable secret scanning and block pushes containing high-confidence secrets.
   - Use minimal-access service principals with rotation policy.

7. **Security & Scanning**
   - Enable CodeQL or equivalent code scanning and Dependabot alerts.
   - Enable branch protection with required status checks, required reviewers, and dismissal rules.
   - Enforce 2FA at org level and restrict third-party app access.

8. **Commit & Message Standards**
   - Adopt Conventional Commits. Example: `feat(pipeline): add dedup step`.
   - Keep subject ≤72 chars; include data-impact summary and ticket reference.
   - Use commit hooks (pre-commit) for formatting and basic static checks.

9. **Release & Deployment Controls**
   - Use semantic versioning for libraries; tag releases and publish to internal package registry.
   - Production pipeline deploys require approval from `on-call/data-owner` and successful canary validation.
   - Use feature flags or gated releases for behavioral changes.

10. **Observability & Runbooks**
    - PRs that change monitoring, SLAs, or alerts must include test plan and runbook updates.
    - Store runbooks in repo `docs/runbooks/` and reference them in PRs.

11. **Access Control & Least Privilege**
    - Use GitHub teams for permission groups. Grant write permissions only to active contributors.
    - Use `CODEOWNERS` to enforce review from domain experts.

12. **Automation & Bots**
    - Enable Dependabot, stale-PR bot, and labeler bots. Document bot behavior in `CONTRIBUTING.md`.
    - Automate changelog generation for dataset and infra changes.

13. **Onboarding & Documentation**
    - Maintain `CONTRIBUTING.md`, `SECURITY.md`, and a `DATA_OWNERS.md` in each repo.
    - Provide quick-start for local pipeline debugging and affected-only test commands.

14. **Enforcement & Exceptions**
    - Automate enforcement via branch protection, actions, and pre-merge checks.
    - Exceptions must be approved and recorded in an ISSUE with rationale and expiry.

15. **Metrics & Continuous Improvement**
    - Track: PR lead time, CI duration, merge failures, schema-change incidents, and rollback frequency.
    - Review policies quarterly and adjust based on metrics and team feedback.

## Contact & Escalation

For policy questions or exception requests, open an ISSUE in the central ops repo and tag `@data-eng-ops` and the relevant CODEOWNERS.

> Document and apply these policies uniformly; prefer automation over manual policing.
