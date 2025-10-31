# Monorepo vs Polyrepo vs Hybrid

## Quick summary
- **Monorepo** — single repository containing multiple projects/packages/services.  
- **Polyrepo** (multi-repo) — each project/service has its own repository.  
- **Hybrid** — combination (e.g., monorepo for core libs, separate repos for apps).

## Core differences
- Code locality: monorepo = everything together; polyrepo = isolated repos.  
- Dependency/versioning: monorepo often uses unified/internal tooling; polyrepo uses independent releases.  
- Tooling/CI: monorepo requires repo-aware build/test tooling; polyrepo uses per-repo pipelines.  
- Access & governance: monorepo centralizes standards; polyrepo enables fine-grained ownership.

## Monorepo

### Benefits
- Atomic cross-project refactors are simple.
- Better code discoverability and reuse.
- Easier to enforce repo-wide standards, linters and CI.
- Consistent dependency versions and unified versioning.
- Simplified workflow for changes spanning multiple projects.

### Drawbacks
- Tooling complexity at scale (build/test/dependency graph).
- Larger clones and heavier local tooling requirements.
- CI can become expensive without selective builds/tests.
- Harder to apply fine-grained access controls.
- Noisy history if not well-structured.

## Polyrepo

### Benefits
- Clear ownership boundaries and access control.
- Smaller clones and simpler local context.
- Independent release cadence per component.
- CI complexity is localized per repo.

### Drawbacks
- Cross-repo refactors are harder (coordination, multi-PRs).
- Versioning and compatibility drift risk.
- Shared code discoverability can suffer.
- Possible duplication of infra/config unless centralized automation exists.

## Hybrid approaches
- Group related services in domain repos; keep libraries in a monorepo.
- Use internal package registries and CI to manage compatibility.
- Monorepo for core infra + polyrepo for high-velocity teams.

## Tooling & operational concerns
- Monorepo tools: Bazel, Pants, Nx, Lerna, Rush (and large org custom tooling).  
- Techniques: affected-only builds/tests, caching, incremental CI.  
- Polyrepo tooling: package registries (npm, Maven, NuGet), repo automation (dependabot, templates).  
- Monitor metrics: CI duration, PR cycle time, repo size, cross-repo change friction.

## Governance & scaling
- Monorepo favors centralized governance and shared standards.  
- Polyrepo favors team autonomy and independent lifecycles.  
- Consider access control, compliance, and audit requirements when choosing.

## When to choose which
- Choose **Monorepo** if:
  - Frequent cross-project refactors and shared code are common.
  - Teams can invest in selective CI and centralized tooling.
- Choose **Polyrepo** if:
  - Teams require strict isolation, independent ownership, or differing release cadences.
- Choose **Hybrid** if:
  - Some components require tight coupling while others remain independent.

## Practical recommendations
- Start with the model that matches team structure and scale.
- For monorepo: invest early in tooling (affected-only CI, caching, dev ergonomics).
- For polyrepo: automate cross-repo changes and provide an internal package registry.
- Measure and iterate: track PR lead time, CI cost, and cross-repo change friction.

Keep decisions aligned with team size, release cadence, and expected coupling.