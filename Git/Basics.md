# Git basics

## Common Git Branching Strategies

### 1. GitFlow
A robust branching model designed for larger projects with scheduled releases.

#### Structure
- **main/master**: Production-ready code
- **develop**: Main development branch
- **feature/***:  New features
- **release/***:  Release preparation
- **hotfix/***:  Production fixes

#### Example workflow:
```bash
# Start a new feature
git checkout develop
git checkout -b feature/user-auth

# After feature completion, merge to develop
git checkout develop
git merge --no-ff feature/user-auth

# Prepare release
git checkout -b release/1.0.0
# Make release fixes if needed

# Finalize release
git checkout main
git merge release/1.0.0
git tag -a v1.0.0
```

### 2. Trunk-Based Development
Emphasizes small, frequent commits directly to the main branch.

#### Structure
- **main**: Single source of truth
- **feature-flags**: For managing in-progress features
- Short-lived feature branches (1-2 days max)

#### Example workflow:
```bash
# Small feature changes
git checkout -b small-fix
# Make changes
git checkout main
git merge small-fix

# Feature flags for larger changes
git checkout main
# Add feature flag code
```

### 3. GitHub Flow
Simplified workflow suitable for continuous delivery.

#### Structure
- **main**: Production-ready code
- **feature branches**: All development work

#### Example workflow:
```bash
# Create feature branch
git checkout -b new-feature

# Push regularly
git push origin new-feature

# Create Pull Request via GitHub
# After review and CI passes
git checkout main
git merge new-feature
```

### 4. Release Branch Strategy
Focuses on maintaining multiple versions in production.

#### Structure
- **main**: Latest development
- **release/***: Supported versions
- **hotfix/***: Critical fixes

#### Example workflow:
```bash
# Create release branch
git checkout -b release/2.0

# Hotfix for release
git checkout -b hotfix/2.0.1 release/2.0
# Fix critical bug
git checkout release/2.0
git merge hotfix/2.0.1
```

## Best Practices
1. Document your chosen strategy
2. Enforce branch naming conventions
3. Use meaningful commit messages
4. Implement automated testing
5. Regular code reviews
6. Branch protection rules
7. Clean up merged branches

## Strategy Selection Considerations
- Team size and experience level
- Project complexity
- Release frequency
- CI/CD requirements
- Production environment
- Customer requirements

> **Note**: The best strategy is one that your team will actually follow consistently.