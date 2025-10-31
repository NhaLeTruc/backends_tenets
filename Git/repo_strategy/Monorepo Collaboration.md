# Monorepo Collaboration: Guidance for Lead Developers

## Purpose
Provide clear, actionable guidance a lead developer can use to align the team when working in a monorepo. Focus on predictable workflows, low-friction collaboration, and maintainable repository hygiene.

---

## Key communication principles
- Be concise and explicit. State the why, what, and how.
- Lead by example: use the same commands and templates you ask others to use.
- Prefer written, discoverable guidance (docs, templates) over one-off messages.
- Make changes to the collaboration rules via PR so the team can discuss and iterate.

---

## Core policies to announce and document
1. Repo scope and ownership
   - Define which directories map to services, libraries, infra.
   - Assign owners or on-call contacts for packages/areas.

2. Branching rules
   - Main/trunk policy (e.g., main must be green and deployable).
   - Short-lived branches: name convention (e.g., feature/<ticket>-short-desc).
   - When to rebase vs merge; require `--force-with-lease` on rewritten branches.

3. Pull request standards
   - Small, focused PRs; ideally < 300 LOC.
   - PR template: motivation, testing, impact, rollback steps.
   - Required checks: CI, linters, security scan, 1–2 approvals.
   - Use draft PRs for early feedback.

4. CI/affected-only builds
   - Describe how CI determines affected projects.
   - Ask contributors to run local subset builds/tests before pushing.

5. Versioning & releases
   - Explain how packages/apps are versioned and published.
   - Document release process and tagging convention.

6. Dependency changes and cross-cutting refactors
   - Require tests and a migration plan for changes affecting many packages.
   - Prefer atomic cross-project PRs that update all affected code in one PR when feasible.

7. Feature flags and dark launches
   - Recommend feature flags for incomplete work that lands on trunk.
   - Document flag naming and lifecycle (create, monitor, remove).

8. Access & security
   - State access boundaries and how to request exceptions.
   - Enforce secret scanning and avoid committing secrets.

---

## Daily operational guidance (what to tell the team)
- Pull frequently and rebase/update your branch against main before opening a PR.
- Keep PRs small; open early and iterate based on CI and review feedback.
- Run targeted local tests for the affected packages to reduce CI cycles.
- Annotate PRs with affected packages (use labels or a checklist).
- If a PR causes CI failures for unrelated areas, communicate immediately and revert or fix.

---

## Conflict resolution and cross-team coordination
- If a merge conflict affects multiple teams, create a coordination PR and assign stakeholders.
- For high-risk cross-cutting changes, schedule a short sync (15 min) and post decisions in the relevant channel.
- Use a "merge window" policy if many teams need synchronized deploys; otherwise prefer continuous merging.

---

## Tooling and automation to communicate
- Share links and short instructions for:
  - Local dev bootstrap
  - Affected-only CI command
  - Lint/format commands
  - How to run package-level tests
- Provide templates (PR, changelog, issue) and add them to the repo.
- Enable bots for dependency updates, PR labeling, and stale branch cleanup; document their behavior.

---

## Onboarding and documentation
- Maintain a short "Getting started" doc for new contributors:
  - How to clone (sparse-checkout if supported)
  - How to run local builds/tests for one package
  - Branch/PR process and where to ask for help
- Keep a visible CHANGELOG or release notes for public-facing changes.

---

## Meetings and async updates
- Use brief, focused coordination meetings only when necessary.
- Prefer async status updates in a dedicated channel for broad-impact changes.
- Post post-mortems for major incidents and summarize lessons learned in the repo.

---

## Metrics and feedback loop
- Track and share metrics: PR lead time, CI times, merge conflicts per week, flaky test rate.
- Revisit rules every quarter based on data and team feedback.

---

## Example short announcement (lead -> team)
1) Why: "We are moving to a disciplined monorepo workflow to reduce cross-repo friction and speed up refactors."  
2) What: "Rules: trunk must be green, use feature/<ticket>-desc branch names, run affected-only tests locally, use PR template, require 1 approval + CI green."  
3) How: "Docs updated at /Git/Monorepo_Collaboration_Guide.md. Please read and follow for new changes. Questions in #dev-monorepo."

---

Keep guidance accessible, iterate based on team experience, and enforce via CI and documentation rather than manual policing.