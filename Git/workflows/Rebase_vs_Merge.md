# Git Rebase and Merge Guide

## Understanding Merge vs Rebase

- **Merge**: Combines branches by creating a new commit
- **Rebase**: Rewrites commit history by moving commits to a new base

## Basic Merge Operation

### Fast-forward Merge
When branches have no diverging commits:

```bash
git checkout main
git merge feature
```

### Three-way Merge

When branches have diverged:

```bash
git checkout main
git merge feature-branch
# Resolve conflicts if any
git add .
git commit -m "Merge feature-branch into main"
```

## Basic Rebase Operation

### Simple Rebase

Moving feature branch commits onto main:

```bash
git checkout feature-branch
git rebase main
```

### Interactive Rebase

Cleaning up commits before merging:

```bash
git checkout feature-branch
git rebase -i HEAD~3  # Last 3 commits
```

Common interactive rebase commands:

```
pick 1234567 First commit
squash 2345678 Second commit
fixup 3456789 Third commit
```

## Advanced Scenarios

### Rebase with Conflicts

```bash
git checkout feature
git rebase main
# If conflicts occur:
git status  # Check conflicting files
# Resolve conflicts manually
git add .
git rebase --continue
# Or abort if needed:
git rebase --abort
```

### Squashing Commits with Rebase

```bash
# Squash last 3 commits
git rebase -i HEAD~3

# In the editor:
pick abc1234 First commit
squash def5678 Second commit
squash ghi9012 Third commit
```

## Best Practices

### When to Use Merge

1. Preserving complete history
2. Working on public branches
3. Maintaining feature branches

Example:

```bash
# Merging a feature into main
git checkout main
git merge --no-ff feature-branch
git push origin main
```

### When to Use Rebase

1. Cleaning up local commits
2. Maintaining linear history
3. Updating feature branches

Example:

```bash
# Update feature branch with main
git checkout feature-branch
git rebase main
git push --force-with-lease origin feature-branch
```

## Common Pitfalls

### 1. Rebasing Public Branches

❌ Don't do this:

```bash
git checkout main
git rebase feature-branch
git push --force origin main
```

✅ Instead do this:

```bash
git checkout main
git merge feature-branch
git push origin main
```

### 2. Losing Work During Rebase

Always create a backup:

```bash
# Create backup branch
git branch backup-feature feature-branch

# If rebase goes wrong
git checkout feature-branch
git reset --hard backup-feature
```

## Advanced Tips

### Cherry-picking with Rebase

```bash
# Cherry-pick specific commits
git checkout feature-branch
git rebase --onto main commit1^ commit2
```

### Rewriting History

```bash
# Change last commit message
git commit --amend -m "New message"

# Rewrite multiple commits
git rebase -i HEAD~3
# Change 'pick' to 'reword' for commits to modify
```

## Safety Measures

### Pre-rebase Checks

```bash
# Check if branch is public
git fetch origin
git log origin/feature-branch..feature-branch

# Create backup
git branch backup-$(date +%Y%m%d) feature-branch
```

### Post-rebase Verification

```bash
# Verify changes
git log --graph --oneline --all
git diff backup-branch..feature-branch
```

## Git Configuration Tips

### Rebase Configuration

```bash
# Set pull to rebase by default
git config --global pull.rebase true

# Enable automatic stashing
git config --global rebase.autoStash true
```

Remember:

1. Never rebase public/shared branches
2. Always create backups before complex operations
3. Use `--force-with-lease` instead of `--force`
4. Keep commits atomic and meaningful
5. Test after resolving conflicts
