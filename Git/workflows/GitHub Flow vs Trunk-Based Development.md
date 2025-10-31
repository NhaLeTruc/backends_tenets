# GitHub Flow vs Trunk-Based Development (TBD)

## Summary
- **GitHub Flow**: Lightweight branch-per-feature + PRs; continuous delivery oriented.  
- **Trunk-Based Development (TBD)**: Single shared trunk with very short-lived branches or feature flags; emphasizes frequent small commits to trunk.

## Core differences
- **Branching**
  - GitHub Flow: Feature branches pushed to origin; merged via Pull Request.
  - TBD: Very short-lived branches (hours/days) or work directly on trunk behind feature flags.
- **Integration cadence**
  - GitHub Flow: Integration at PR merge time.
  - TBD: Continuous integration to trunk multiple times per day.
- **History**
  - GitHub Flow: Retains branch/PR history (merge commits unless squashed).
  - TBD: Encourages linear history; rebasing/squashing common.
- **Review process**
  - GitHub Flow: PRs are primary review gate.
  - TBD: Reviews are lightweight; rely on fast CI, pair programming, or pre-commit checks.
- **Release model**
  - GitHub Flow: Merges to main trigger releases; suitable for continuous deployment.
  - TBD: Suited for continuous delivery with feature flags/dark launches.

## Pros / Benefits
- **GitHub Flow**
  - Easy to adopt; clear isolation; good for formal PR workflows.
- **TBD**
  - Minimizes merge conflicts; faster integration; better for high-velocity teams.

## Cons / Risks
- **GitHub Flow**
  - Long-lived branches can cause integration drift; PRs may bottleneck.
- **TBD**
  - Requires strong CI, tests, and discipline; needs feature flags to avoid shipping unfinished work.

## When to choose which
- Use **GitHub Flow** if:
  - Team prefers formal PR reviews and gated merges.
  - Release cadence is moderate and feature isolation is desired.
- Use **TBD** if:
  - You need maximal release velocity and minimal merge pain.
  - You have robust CI/CD, test coverage, and feature flags.

## Practical recommendations
- Combine strengths: short-lived branches + PRs with frequent rebases; enforce fast CI feedback.
- Enforce CI, code review SLAs, and branch protection rules.
- Use feature flags, dark launches, and canary releases to decouple deploy from release.
- Keep commits small, testable, and reversible.
- Monitor metrics (lead time, PR size, failure rates) to tune workflow.

## Quick checklist
- Need strict PR audits? → GitHub Flow.  
- Need maximal merge velocity with trunk stability? → Trunk-Based Development.  
- Want both safety and speed? → Trunk-Based with PRs for larger changes + feature flags.