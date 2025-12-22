# Switching from Github Flow to Trank based development

Transitioning a GitHub repository from a GitOps workflow that uses long-lived branches (like GitFlow) to trunk-based development involves changing both repository settings and team practices.

## Update Git Branch Structure

The core change is moving away from multiple long-lived branches (e.g., dev, staging, production) to a single, primary branch (commonly named main or trunk).

### Create a new trunk or main branch

```bash
git checkout master # go to current canonical branch (or existing primary branch)
git checkout -b trunk # create the new branch locally
git push origin trunk # push the new branch to GitHub
```

### Set the new branch as default in GitHub

Go to your repository on GitHub, navigate to Settings > Branches, and change the default branch in the dropdown menu to trunk (or main).

### Merge and retire old branches

Migrate all relevant code from your old dev or feature branches into the new trunk branch. You can then add branch protection rules to the old branches to prevent new pushes, or delete them entirely if they are fully merged. A detailed process for migrating an entire branch's history can be found in this [Stack Overflow guide](https://stackoverflow.com/questions/70773853/suggestions-for-moving-from-gitflow-to-trunk-based-dev).

### Configure GitHub Branch Protection Rules

With all development focusing on a single branch, strong protection rules are essential to maintain code stability and quality.

- **Require pull requests (PRs)**: Enforce that all changes must pass through a pull request review.
- **Require status checks to pass**: Ensure your CI pipeline (tests, linters, security scans) runs successfully before a merge is allowed.
- **Prevent force pushes**: This is critical to maintain a linear and predictable history.
- Require signed commits (optional but recommended for security).

## Adapt Workflow and Team Practices

The technical changes must be supported by process changes within the development team to benefit from trunk-based development's speed and efficiency. 

- **Short-lived feature branches**: Encourage developers to create branches off the trunk and merge them back within a few hours or days (never more than a week).
- **Small, frequent commits**: Focus on merging small code changes often to avoid large, conflict-prone pull requests.
- **Continuous integration (CI)**: Ensure every commit or PR triggers an automated build and test pipeline, providing instant feedback loops.
- **Feature flags/toggles**: Use feature flags for unfinished or sensitive code. This allows the code to be merged into the main trunk without being activated in production, separating deployment from release.
- **Automated deployment/promotion**: Integrate your GitOps tools (like Flux or Argo CD) to automatically promote changes through environments (staging, production) as commits are added to the trunk, potentially using directory structures to manage environment-specific configurations. 