# GitHub Rules vs Policies

## Definitions

- **GitHub rules** — technical controls/settings in GitHub (branch protection, required checks, CODEOWNERS, Actions).
- **Policies** — higher-level governance documents and decisions (security policy, contribution policy, release policy).

## Purpose

- Rules: enforce workflow mechanics and guardrails automatically at commit/PR/CI time.  
- Policies: define expectations, responsibilities, and decision-making principles for people and teams.

## Scope & Granularity

- Rules: fine‑grained, implementable, per‑repo or org settings.  
- Policies: broader, human‑facing, and organizational.

## Enforcement

- Rules: enforced by the platform (blocks actions when checks fail).  
- Policies: enforced via process, culture, and supporting rules; may require manual or managerial action.

## Examples

- Rules: branch protection, required CI job names, secret scanning, CODEOWNERS.  
- Policies: commit message conventions, review SLAs, release cadence, access provisioning.

## Lifecycle & Change Process

- Rules: changed via repo settings, API, or IaC; take immediate effect.  
- Policies: changed via proposals/RFCs, communicated and rolled out with training and tooling.

## Relationship

- Policies inform which rules to implement (policy → rule mapping).  
- Rules operationalize policies and provide auditability.

## Best Practices

- Keep policies concise and human‑readable.  
- Automate enforcement with rules where possible.  
- Map each policy to specific GitHub rules and publish that mapping.  
- Communicate changes and provide onboarding materials.  
- Review periodically using metrics (PR lead time, CI failures, incidents).

## Recommendation

1. Define a small set of core policies (branching, security, review, release).  
2. Implement corresponding GitHub rules (branch protections, required checks, CODEOWNERS, security scans).  
3. Document the mapping and onboard the team.  
4. Iterate based on metrics and feedback.

Short, automated rules + clear human policies = reliable, scalable collaboration.