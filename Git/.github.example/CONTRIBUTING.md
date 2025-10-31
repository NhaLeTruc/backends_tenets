# Contributing

Thank you for contributing. This file explains how to get started and what we expect.

## Code of Conduct
Be respectful. Follow our code of conduct in CODE_OF_CONDUCT.md (if present).

## Getting started
1. Fork and clone the repo.
2. Install dependencies:
   - Python: `pip install -r requirements.txt`
   - Node: `npm ci`
3. Run tests locally: `pytest` / `npm test`

## Branching & workflow
- Branch naming: `feature/PROJ-123-short-desc`, `fix/PROJ-123-short-desc`.
- Keep branches short-lived and focused.
- Rebase frequently on `main`.

## Commit messages
- Follow Conventional Commits: `type(scope?): short summary`
  - Examples: `feat(auth): add refresh-token`, `fix(api): handle null id`
- Subject ≤ 72 chars, blank line, body wrapped at ~72 chars.

## Pull Requests
- Open a PR early; use draft PRs as needed.
- Fill the PR template. Provide testing steps and impact notes.
- Small PRs preferred (< 300 LOC). Ensure CI passes.

## Tests & quality
- Add tests for new behavior.
- Run linters and formatters before committing.
  - Install pre-commit hooks: `pipx run pre-commit install` or `pre-commit install`
- Ensure PR includes test results and screenshots if applicable.

## Security
- Never commit secrets. Use GitHub Secrets / Vault.
- Report security issues privately (see SECURITY.md).

## Getting help
- For quick questions, use the `#dev` channel.
- For repo-specific decisions, open an ISSUE and tag CODEOWNERS.

## Thanks
We appreciate your contributions — they make this project better.